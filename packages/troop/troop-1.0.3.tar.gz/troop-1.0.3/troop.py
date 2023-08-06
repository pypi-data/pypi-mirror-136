

from typing import Optional
import networkx as nx
import inspect
import copy
import json
import os
import re

class Worker:
    def __init__(self, name: str):
        self.name = name
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.__dict__.values())

    def __repr__(self):
        return str(self.__dict__.values())

class Colony:
    """The Colony class is the main entity that represents a workflow in colony.
    The colony groups together workers that well perform different tasks as part of the workflow.

    :param name the name of the colony
    :param requirements the path to the requirements file
    """
    def __init__(self, name: str):
        self.name = name
        self.module = None
        self.graph: nx.DiGraph = nx.DiGraph()
        self.exclude_attrs_from_lean_dict = [
            '_lean_dict',
            '_copy_graph',
            'graph',
            'exclude_attrs_from_lean_dict'
        ]
    
    def _next_tasks(self) -> list[Worker]:
        next_tasks = []
        for node in self._copy_graph.nodes:
            if len(nx.ancestors(self._copy_graph, node)) == 0:
                next_tasks.append(self._copy_graph.nodes[node])
        return next_tasks

    def _order_workers(self):
        self._copy_graph = copy.deepcopy(self.graph)
        self.execution_order = []
        tasks = self._next_tasks()
        while len(tasks) > 0:
            self.execution_order.append(tasks)
            for task in tasks:
                self._copy_graph.remove_node(task['name'])
            tasks = self._next_tasks() 
    
    def to_json(self) -> dict:
        self._order_workers()
        self._lean_dict = copy.deepcopy(self.__dict__)
        for exclude_attr in self.exclude_attrs_from_lean_dict:
            self._lean_dict.pop(exclude_attr, None)
        return json.dumps(self._lean_dict)
    
    def get_graph(self) -> nx.DiGraph:
        return self.graph



colony_ctxs: dict[str, Optional[Colony]] = {}

def colony_setup(colony_func: callable):
    global colony_ctxs
    colony_ctx = colony_func()
    colony_ctx.module = colony_func.__module__
    colony_ctxs[colony_ctx.module] = colony_ctx

def worker(task: callable):
    """The worker decoration will designate a python callable as task the belongs to the designated colony.
    :param that colony that this worker will be assigned to
    """
    global colony_ctxs
    
    if colony_ctxs[task.__module__] is not None:
        colony_ctxs[task.__module__].graph.add_node(
            task.__name__, 
            name=task.__name__,
            module=task.__module__
            )
        func_sig = inspect.signature(task)
        for param_name in func_sig.parameters:
            colony_ctxs[task.__module__].graph.add_edge(param_name, task.__name__)
            if not nx.is_directed_acyclic_graph(colony_ctxs[task.__module__].graph):
                colony_ctxs[task.__module__].graph.remove_edge(param_name, task.__name__)
                raise Exception(f'{param_name} -> {task.__name__} introduces a cycle.')
    else:
        raise Exception(f'Cannot register worker {task.__name__} there is no Colony defined. Ensure all workers are defined in the same file as the colony setup')


def extract_colony_data_cmd():
    colony_files = []
    setup_dec_pattern = re.compile('@colony_setup')
    venv_root_pattern = re.compile(f'{os.getcwd()}/venv/')
    for root, dirs, files in os.walk(os.getcwd()):
        if venv_root_pattern.match(root) is None:
            for file in [file for file in files if file.endswith('.py')]:
                with open(root+'/'+file, 'r') as f:
                    if setup_dec_pattern.search(f.read()) is not None:
                        colony_files.append(file)
    
    import_cmd = {}
    import_cmd['cmd'] = 'python' 
    import_cmd['args'] = ['-c']

    cmd_py_str = '"import troop;'
    for file in map(lambda f: f' import {f.replace(".py", "")}; ', colony_files):
        cmd_py_str += file
    cmd_py_str += ' print([troop.colony_ctxs[colony_ctx].to_json() for colony_ctx in troop.colony_ctxs])"'
    import_cmd['args'].append(cmd_py_str)
    print(json.dumps(import_cmd))
