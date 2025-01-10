from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from pathlib import Path, PurePosixPath
from core.enums import NodeType
import traceback
import inspect
if TYPE_CHECKING:
    from core.node import Node
from core.internal_path import InternalPath

_node_types = None

def generate_node_types():
    global _node_types
    if _node_types is None:
        node_types = {}
        # Look in the same directory as this file
        core_dir = Path(__file__).parent
        for file in core_dir.glob("*_node.py"):
            node_type_name = file.stem.replace("_node", "").upper()
            # Just store the base name, not the full path
            node_types[node_type_name] = file.stem.replace("_node", "")
        _node_types = node_types
    return _node_types

def OperationFailed(message: str):
    stack = traceback.extract_stack()[:-1]  # Remove the last entry (this function call)
    caller_frame = inspect.currentframe().f_back
    func_name = caller_frame.f_code.co_name
    line_no = caller_frame.f_lineno
    file_name = caller_frame.f_code.co_filename

    print(f"OperationFailed: {message}")
    print(f"  In function: {func_name}")
    print(f"  File: {file_name}")
    print(f"  Line: {line_no}")
    print("\nStack Trace:")
    for filename, line, func, code in stack:
        print(f"  File: {filename}, Line: {line}, in {func}")
        if code:
            print(f"    {code.strip()}")
    print()  # Add an empty line for better readability

class NodeEnvironment:

    """
    NodeEnvironment: A singleton class managing the lifecycle and organization of nodes in a hierarchical node graph system.

    This class serves as the central registry and manager for all nodes in the application, maintaining their 
    relationships, paths, and execution environment. It implements the singleton pattern to ensure a single, 
    consistent state across the entire application.

    Key Features:
        - Hierarchical Node Management:
            * Maintains nodes in a tree-like structure using POSIX-style paths
            * Handles node creation, deletion, and path updates
            * Prevents duplicate node names through automatic renaming
        
        - Node Registration and Lookup:
            * Tracks all active nodes in the system
            * Provides methods to find nodes by name or path
            * Supports post-registration initialization for specialized node types
        
        - Environment Control:
            * Manages global execution environment for nodes
            * Provides isolated namespace for code execution
            * Maintains reference to current active node

    Core Methods:
        add_node(node): 
            Registers a new node in the environment
            Handles post-registration initialization
        
        remove_node(node_path):
            Recursively removes a node and all its children
            Cleans up associated resources
        
        update_node_path(old_path, new_parent_path):
            Relocates nodes within the hierarchy
            Handles path conflicts through automatic renaming
            Updates all child nodes' paths accordingly
        
        flush_all_nodes():
            Completely resets the environment
            Removes all nodes except root
            Rebuilds global execution context

    Path Management:
        - Uses POSIX-style paths (e.g., '/parent/child')
        - Maintains unique paths through automatic renaming
        - Handles path updates for entire node subtrees
        
    Safety Features:
        - Prevents root node deletion
        - Validates parent paths before node relocation
        - Handles naming conflicts automatically
        - Maintains node hierarchy integrity
        
    Error Handling:
        - Provides detailed error traces through OperationFailed
        - Validates paths and node existence
        - Maintains environment stability during operations

    Example Usage:
        >>> env = NodeEnvironment.get_instance()
        >>> env.add_node(some_node)  # Registers a new node
        >>> node = env.node_from_name("myNode")  # Retrieves a node
        >>> env.update_node_path("/old/path", "/new/parent")  # Relocates a node
        >>> env.flush_all_nodes()  # Resets environment

    Notes:
        - Always use get_instance() to obtain the NodeEnvironment instance
        - Node paths must be unique within the environment
        - Child nodes' paths are automatically updated when parent nodes move
        - The root path ('/') is protected and cannot be deleted
        - Node names may be modified during path updates to maintain uniqueness
    """

    _instance = None
    nodes: Dict[str, 'Node'] = {}

    def __init__(self):
        self._node_created_callbacks = []
        self._creating_node = False
        self.root = PurePosixPath('/')
        self.current_node: Optional['Node'] = None 
        self.globals = self._build_globals()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodeEnvironment, cls).__new__(cls)
            cls._instance.root = PurePosixPath('/')
            cls._instance.current_node = None
            cls._instance.globals = cls._instance._build_globals()
        return cls._instance

    def _build_globals(self) -> Dict[str, Any]:
        from core.node import Node
        return {
            'Node': Node,
            'NodeType': NodeType,
            'current_node': self.current_node,
            'NodeEnvironment': NodeEnvironment
        }

    def get_namespace(self):
        return {'current_node': self.current_node, **self.globals}

    def execute(self, code):
        try:
            local_vars = {}
            exec(code, self.get_namespace(), local_vars)
            self.globals.update(local_vars)
            return local_vars.get('_') if '_' in local_vars else None
        except Exception as e:
            print(f'Error: {str(e)}')
            return None

    def inspect(self):
        print('NodeEnvironment state:')
        print(f'Nodes: {self.nodes}')
        print(f'Globals: {self.globals}')

    @classmethod
    def list_nodes(cls) ->list[str]:
        return list(cls.nodes.keys())

    @classmethod
    def node_exists(cls, node_name: str) ->bool:
        return node_name in cls.nodes

    @classmethod
    def add_node(cls, node: 'Node') -> None:
        if cls.get_instance()._creating_node:
            return
        cls.get_instance()._creating_node = True
        cls.nodes[node.path()] = node
        if hasattr(node.__class__, 'post_registration_init'):
            node.__class__.post_registration_init(node)
        cls.get_instance()._creating_node = False

    @classmethod
    def node_from_name(cls, node_name: str) ->Optional['Node']:
        if node_name in cls.nodes:
            return cls.nodes[node_name]
        for path, node in cls.nodes.items():
            if node_name == path.split('/')[-1]:
                return node
        return None

    @classmethod
    def remove_node(cls, node_path: str) ->None:
        if node_path == '/':
            return
        nodes_to_remove = [path for path in cls.nodes.keys() if path.
            startswith(node_path)]
        nodes_to_destroy = [(path, cls.nodes[path]) for path in nodes_to_remove
            ]
        for path, node in nodes_to_destroy:
            node.destroy()

    @classmethod
    def remove_node_from_dictionary(cls, node_path: str) ->None:
        if node_path == '/':
            return
        cls.nodes.pop(node_path)

    @classmethod
    def flush_all_nodes(cls):
        nodes_to_destroy = [(path, cls.nodes[path]) for path in cls.nodes.
            keys() if path != '/']
        for path, node in nodes_to_destroy:
            node.destroy()
        cls.get_instance().current_node = None
        cls.get_instance().globals = cls.get_instance()._build_globals()

    @classmethod
    def update_node_path(cls, old_path: str, new_parent_path: str) ->Tuple[
        str, bool]:
        if new_parent_path != '/' and not cls.node_exists(new_parent_path):
            raise ValueError(f"Parent path '{new_parent_path}' does not exist")
        node = cls.nodes.get(old_path)
        if not node:
            raise ValueError(f"Node at path '{old_path}' does not exist")
        old_name = old_path.split('/')[-1]
        base_name = old_name
        counter = 1
        while True:
            new_name = base_name if counter == 1 else f'{base_name}_{counter}'
            new_path = f"{new_parent_path.rstrip('/')}/{new_name}"
            if new_path not in cls.nodes or new_path == old_path:
                break
            counter += 1
        path_updates = {}
        children = [p for p in cls.nodes if p.startswith(old_path + '/')]
        path_updates[old_path] = new_path
        for child_path in children:
            relative_path = child_path[len(old_path):]
            path_updates[child_path] = new_path + relative_path
        nodes_copy = {}
        for old_p, new_p in path_updates.items():
            node = cls.nodes[old_p]
            node._path = InternalPath(new_p)
            if old_p == old_path:
                node._name = new_name
            nodes_copy[new_p] = node
        for old_p in path_updates:
            del cls.nodes[old_p]
        cls.nodes.update(nodes_copy)
        return new_path, new_name != base_name
