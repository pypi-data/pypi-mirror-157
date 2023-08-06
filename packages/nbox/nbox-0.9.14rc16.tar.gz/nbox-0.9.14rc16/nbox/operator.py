"""
``Operators`` is how you write NBX-Jobs. If you are familiar with pytorch, then usage is
exactly same, for others here's a quick recap:

.. code-block:: python

  class MyOperator(Operator):
    def __init__(self, a: int, b: str):
      super().__init__()
      self.a: int = a
      self.b: Operator = MyOtherOperator(b) # nested calling
    
    def forward(self, x: int) -> int:
      y = self.a + x
      y = self.b(y) + x # nested calling
      return y

  job = MyOperator(1, "hello") # define once
  res = job(2)                 # use like python, screw DAGs

If you want to use deploy `nbox.Jobs <nbox.jobs.html>`_ is a better documentation.


Engineering
-----------

Fundamentally operators act as a wrapper on user code, sometime abstracting away functions
by breaking them into ``__init__``s and ``forward``s. But this is a simpler way to wrap
user function than letting users wrap their own function. It is easy to get false positives,
and so we explicitly expand things in two. These operators are like ``torch.nn.Modules``
spiritually as well because modules manage the underlying weights and operators manage the
underlying user logic.

Operators are combination of several subsystems that are all added in the same class, though
certainly if we come up with that high abstraction we will refactor this:

#. tree: All operators are really treated like a tree meaning that the execution is nested\
    and the order of execution is determined by the order of the operators in the tree. DAGs\
    are fundamentally just trees with some nodes spun togeather, to execute only once.
#. deploy, ...: All the services in NBX-Jobs.
#. get_nbx_flow: which is the static code analysis system to understand true user intent and\
    if possible (and permission of the user) optimise the logic.
"""
# Some parts of the code are based on the pytorch nn.Module class
# pytorch license: https://github.com/pytorch/pytorch/blob/master/LICENSE
# modifications: research@nimblebox.ai 2022

import os
import jinja2
import inspect
from typing import Iterable, List
from collections import OrderedDict

import nbox.utils as U
from nbox.utils import logger
from nbox.init import nbox_ws_v1
from nbox.network import deploy_job, Schedule, deploy_serving
from nbox.framework.on_functions import get_nbx_flow
from nbox.framework import AirflowMixin, PrefectMixin
from nbox.hyperloop.job_pb2 import Job as JobProto, Resource
from nbox.hyperloop.dag_pb2 import DAG, Flowchart, Node, RunStatus
from nbox.hyperloop.serve_pb2 import Serving
from nbox.nbxlib.tracer import Tracer
from nbox.messages import get_current_timestamp
from nbox.sub_utils.latency import log_latency
from nbox.version import __version__


class Operator():
  _version: int = 1 # always try to keep this an i32
  node = Node()
  source_edges: List[Node] = None
  _inputs = []

  def __init__(self) -> None:
    """Create an operator, which abstracts your code into sharable, bulding blocks which
    can then deployed on either NBX-Jobs or NBX-Deploy.
    
    Usage:

    .. code-block:: python
      
      class MyOperator(Operator):
        def __init__(self, ...):
          ... # initialisation of job happens here

          # use prebuilt operators to define the entire process
          from .nbxlib.ops import Shell
          self.download_binary = Shell("wget https://nbox.ai/{hash}")

          # keep a library of organisation wide operators
          from .nbx_internal.operators import TrainGPT
          self.train_model: Operator = TrainGPT(...)

        def forward(self, ...):
          # pass any inputs you want at runtime
          ... # execute code in any arbitrary order, free from DAGs

          self.download_binary(hash="my_binary") # pass relevant data at runtime
          self.train_model() # run any operation and get full visibility on platform

      # to convert operator is 
      job: Operator = MyOperator(...)

      # deploy this as a batch process
      job.deploy()
    """
    self._operators = OrderedDict() # {name: operator}
    self._op_trace = []
    self._tracer: Tracer = None

  def __remote_init__(self):
    """User can overwrite this function, this will be called only when running on remote.
    This helps in with things like creating the models can caching them in self, instead
    of ``lru_cache`` in forward."""
    pass

  # mixin/

  to_airflow_operator = AirflowMixin.to_airflow_operator
  to_airflow_dag = AirflowMixin.to_airflow_dag
  from_airflow_operator = classmethod(AirflowMixin.from_airflow_operator)
  from_airflow_dag = classmethod(AirflowMixin.from_airflow_dag)
  to_prefect_task = PrefectMixin.to_prefect_task
  to_prefect_flow = PrefectMixin.to_prefect_flow
  from_prefect_task = classmethod(PrefectMixin.from_prefect_task)
  from_prefect_flow = classmethod(PrefectMixin.from_prefect_flow)

  # /mixin

  # information passing/

  def __repr__(self):
    # from torch.nn.Module
    def _addindent(s_, numSpaces):
      s = s_.split('\n')
      # don't do anything for single-line stuff
      if len(s) == 1:
        return s_
      first = s.pop(0)
      s = [(numSpaces * ' ') + line for line in s]
      s = '\n'.join(s)
      s = first + '\n' + s
      return s

    # We treat the extra repr like the sub-module, one item per line
    extra_lines = []
    extra_repr = ""
    # empty string will be split into list ['']
    if extra_repr:
      extra_lines = extra_repr.split('\n')
    child_lines = []
    for key, module in self._operators.items():
      mod_str = repr(module)
      mod_str = _addindent(mod_str, 2)
      child_lines.append('(' + key + '): ' + mod_str)
    lines = extra_lines + child_lines

    main_str = self.__class__.__name__ + '('
    if lines:
      # simple one-liner info, which most builtin Modules will use
      if len(extra_lines) == 1 and not child_lines:
        main_str += extra_lines[0]
      else:
        main_str += '\n  ' + '\n  '.join(lines) + '\n'

    main_str += ')'
    return main_str

  def __setattr__(self, key, value: 'Operator'):
    obj = getattr(self, key, None)
    if key != "forward" and obj is not None and callable(obj):
      raise AttributeError(f"cannot assign {key} as it is already a method")
    if isinstance(value, Operator):
      if not "_operators" in self.__dict__:
        raise AttributeError("cannot assign operator before Operator.__init__() call")
      if key in self.__dict__ and key not in self._operators:
        raise KeyError(f"attribute '{key}' already exists")
      self._operators[key] = value
    self.__dict__[key] = value

  def propagate(self, **kwargs):
    """Set kwargs for each child in the Operator"""
    for k, v in kwargs.items():
      setattr(self, k, v)
    for c in self.children:
      c.propagate(**kwargs)

  def thaw(self, job: JobProto):
    """Load JobProto into this Operator"""
    nodes = job.dag.flowchart.nodes
    edges = job.dag.flowchart.edges
    for _id, node in nodes.items():
      name = node.name
      if name.startswith("self."):
        name = name[5:]
      if hasattr(self, name):
        op: 'Operator' = getattr(self, name)
        op.propagate(
          node = node,
          source_edges = list(filter(
            lambda x: edges[x].target == node.id, edges.keys()
          ))
        )

  def operators(self):
    r"""Returns an iterator over all operators in the job."""
    for _, module in self.named_operators():
      yield module

  def named_operators(self, memo = None, prefix: str = '', remove_duplicate: bool = True):
    r"""Returns an iterator over all modules in the network, yielding both the name of the module
    as well as the module itself."""
    if memo is None:
      memo = set()
    if self not in memo:
      if remove_duplicate:
        memo.add(self)
      yield prefix, self
      for name, module in self._operators.items():
        if module is None:
          continue
        submodule_prefix = prefix + ('.' if prefix else '') + name
        for m in module.named_operators(memo, submodule_prefix, remove_duplicate):
          yield m

  @property
  def children(self) -> Iterable['Operator']:
    """Get children of the operator."""
    return self._operators.values()

  @property
  def inputs(self):
    args = inspect.getfullargspec(self.forward).args
    try:
      args.remove('self')
    except:
      raise ValueError("forward function must have 'self' as first argument")
    if self._inputs:
      args += self._inputs
    return args

  def __call__(self, *args, **kwargs):
    # Type Checking and create input dicts
    inputs = self.inputs
    len_inputs = len(args) + len(kwargs)
    if len_inputs > len(inputs):
      raise ValueError(f"Number of arguments ({len(inputs)}) does not match number of inputs ({len_inputs})")
    elif len_inputs < len(args):
      raise ValueError(f"Need at least arguments ({len(args)}) but got ({len_inputs})")

    input_dict = {}
    for i, arg in enumerate(args):
      input_dict[self.inputs[i]] = arg
    for key, value in kwargs.items():
      if key in inputs:
        input_dict[key] = value

    logger.debug(f"Calling operator '{self.__class__.__name__}': {self.node.id}")
    _ts = get_current_timestamp()
    self.node.run_status.CopyFrom(RunStatus(start = _ts, inputs = {k: str(type(v)) for k, v in input_dict.items()}))
    if self._tracer != None:
      self._tracer(self.node)

    # ---- USER SEPERATION BOUNDARY ---- #

    with log_latency(f"{self.__class__.__name__}-forward"):
      out = self.forward(*args, **kwargs)

    # ---- USER SEPERATION BOUNDARY ---- #
    outputs = {}
    if out is None:
      outputs = {"out_0": str(type(None))}
    elif isinstance(out, dict):
      outputs = {k: str(type(v)) for k, v in out.items()}
    elif isinstance(out, (list, tuple)):
      outputs = {f"out_{i}": str(type(v)) for i, v in enumerate(out)}
    else:
      outputs = {"out_0": str(type(out))}

    logger.debug(f"Ending operator '{self.__class__.__name__}': {self.node.id}")
    _ts = get_current_timestamp()
    self.node.run_status.MergeFrom(RunStatus(end = _ts, outputs = outputs,))
    if self._tracer != None:
      self._tracer(self.node)

    return out

  def forward(self):
    raise NotImplementedError("User must implement forward()")

  # nbx/
  def _get_dag(self) -> DAG:
    """Get the DAG for this Operator including all the nested ones."""
    dag = get_nbx_flow(self.forward)
    all_child_nodes = {}
    all_edges = {}
    for child_id, child_node in dag.flowchart.nodes.items():
      name = child_node.name
      if name.startswith("self."):
        name = name[5:]
      operator_name = "CodeBlock" # default
      cls_item = getattr(self, name, None)
      if cls_item and cls_item.__class__.__base__ == Operator:
        # this node is an operator
        operator_name = cls_item.__class__.__name__
        child_dag: DAG = cls_item._get_dag() # call this function recursively

        # update the child nodes with parent node id
        for _child_id, _child_node in child_dag.flowchart.nodes.items():
          if _child_node.parent_node_id == "":
            _child_node.parent_node_id = child_id # if there is already a parent_node_id set is child's child
          all_child_nodes[_child_id] = _child_node
          all_edges.update(child_dag.flowchart.edges)
      
      # update the child nodes name with the operator name
      child_node.operator = operator_name

    # update the root dag with new children and edges
    _nodes = {k:v for k,v in dag.flowchart.nodes.items()}
    _edges = {k:v for k,v in dag.flowchart.edges.items()}
    _nodes.update(all_child_nodes)
    _edges.update(all_edges)

    # because updating map in protobuf is hard
    dag.flowchart.CopyFrom(Flowchart(nodes = _nodes, edges = _edges))
    return dag

  def deploy(
    self,
    init_folder: str,
    job_id_or_name: str,
    workspace_id: str = None,
    schedule: Schedule = None,
    resource: Resource = None,
    *,
    _unittest = False
  ):
    return deploy_job(
      init_folder = init_folder,
      job_id_or_name = job_id_or_name,
      dag = self._get_dag(),
      workspace_id = workspace_id,
      schedule = schedule,
      resource = resource,
      _unittest = _unittest
    )

  def serve(
    self,
    init_folder: str,
    deployment_id_or_name: str,
    workspace_id: str = None,
    resource: Resource = None,
    wait_for_deployment: bool = True,
    *,
    _unittest = False,
  ):
    """Serve your operator as an API endpoint.
    
    DO NOT CALL THIS DIRECTLY, use `nbx serve new` CLI command instead.

    EXPERIMENTAL: can break anytime
    """
    init_folder = os.path.abspath(init_folder)

    # raise NotImplementedError(f"In-progress will be released in v1.0.0 (currently {__version__})")
    if workspace_id == None:
      stub_all_depl = nbox_ws_v1.user.deployments
    else:
      stub_all_depl = nbox_ws_v1.workspace.u(workspace_id).deployments
    logger.debug(f"deployments stub: {stub_all_depl}")

    # filter and get "id" and "name"
    all_deployments = stub_all_depl()
    deployments = list(filter(
      lambda x: x["deployment_id"] == deployment_id_or_name or x["deployment_name"] == deployment_id_or_name,
      all_deployments
    ))
    if len(deployments) == 0:
      logger.warning(f"No deployment found with id '{deployment_id_or_name}', creating new with name!")
      deployment_id = None
      deployment_name = deployment_id_or_name
    elif len(deployments) > 1:
      raise ValueError(f"Multiple deployments found for '{deployment_id_or_name}', try passing ID")
    else:
      data = deployments[0]
      deployment_id = data["deployment_id"]
      deployment_name = data["deployment_name"]

    logger.info(f"Deployment name: {deployment_name}")
    logger.info(f"Deployment ID: {deployment_id}")

    # create a serve proto and use that to serve the model using NBX-Infra
    _starts = get_current_timestamp()
    serving_proto = Serving(
      name = deployment_name,
      created_at = _starts,
      resource = Resource(
        cpu = "100m",         # 100mCPU
        memory = "200Mi",     # MiB
        disk_size = "1Gi",    # GiB
      ) if resource == None else resource
    )

    if workspace_id != None:
      serving_proto.workspace_id = workspace_id
    if deployment_id != None:
      serving_proto.id = deployment_id

    # create the runner stub: in case of jobs it will be python3 exe.py run
    import inspect
    from textwrap import dedent

    def get_fn_base_models(fn) -> List[str]:
      import ast
      if type(fn) == str:
        fn = ast.parse(fn)
      
      for node in fn.body:
        if type(node) == ast.FunctionDef:
          args: ast.arguments = node.args
          all_args = [] # tuple of name, type (if any) and default value
          for arg in args.args[1:]: # first one is always self
            all_args.append(arg.arg)
          if args.kwonlyargs:
            for arg in args.kwonlyargs:
              all_args.append(arg.arg)
          if args.vararg:
            all_args.append(args.vararg.arg)
          if args.kwarg:
            all_args.append(args.kwarg.arg)
      
      strings = [f"{x}: Any = None" for x in all_args]
      return strings

    forward_code = inspect.getsource(self.forward)
    strings = get_fn_base_models(dedent(forward_code))

    py_data = dict(
      project_name = os.path.split(init_folder)[-1],
      created_time = _starts.ToDatetime().strftime("%Y-%m-%d %H:%M:%S"),
      email_id = None,
      operator_name = self.__class__.__name__,
      base_model_strings = strings
    )
    py_f_data = {k:v for k,v in py_data.items() if v is not None}
    assets = U.join(U.folder(__file__), "assets")
    path = U.join(assets, "job_serve.jinja")
    server_path = U.join(init_folder, f"server.py")
    with open(path, "r") as f, open(server_path, "w") as f2:
      f2.write(jinja2.Template(f.read()).render(**py_f_data))

    # zip tje folder
    zip_path = self.zip(init_folder)

    if _unittest:
      return serving_proto

    return deploy_serving(
      export_model_path = zip_path,
      stub_all_depl = stub_all_depl,
      wait_for_deployment = wait_for_deployment
    )

  # /nbx
