import importlib
import re
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum, auto
from pathlib import Path, PurePosixPath
from typing import Any, ClassVar, Dict, List, Callable
from typing import Optional, Set, Tuple, Sequence, Union
import time
from UndoManager import UndoManager



_node_types = None

def generate_node_types():
    global _node_types
    if _node_types is None:
        node_types = {}
        nodes_dir = Path(__file__).parent / "nodes"
        for file in nodes_dir.glob("*_node.py"):
            node_type_name = file.stem.replace("_node", "").upper()
            node_types[node_type_name] = file.stem.replace("_node", "")
        _node_types = node_types
    return _node_types

import inspect
import traceback

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



class NodeType(Enum):
    pass

NodeType = Enum("NodeType", generate_node_types(), type=NodeType)

class NodeEnvironment:
    _instance = None
    nodes: Dict[str, 'Node'] = {}

    def __init__(self):
        self._node_created_callbacks = []
        self._creating_node = False  # Flag to prevent recursive calls
        self.root = PurePosixPath("/")
        self.current_node = None
        self.globals = self._build_globals()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodeEnvironment, cls).__new__(cls)
            cls._instance.root = PurePosixPath("/")
            cls._instance.current_node = None
            cls._instance.globals = cls._instance._build_globals()
        return cls._instance

    def _build_globals(self) -> Dict[str, Any]:
        return {
            'Node': Node,
            'NodeType': NodeType,
            'current_node': self.current_node,
            'NodeEnvironment': NodeEnvironment,
        }

    def get_namespace(self):
        return {
            'current_node': self.current_node,
            **self.globals
        }

    def execute(self, code):
        try:
            local_vars = {}
            exec(code, self.get_namespace(), local_vars)
            # Update the current namespace with any new variables
            self.globals.update(local_vars)
            # Return the last defined variable or expression result
            return local_vars.get('_') if '_' in local_vars else None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def inspect(self):
        print("NodeEnvironment state:")
        print(f"Nodes: {self.nodes}")
        print(f"Globals: {self.globals}")

    @classmethod
    def list_nodes(cls) -> list[str]:
        return list(cls.nodes.keys())
    
    @classmethod
    def node_exists(cls, node_name: str) -> bool:
        return node_name in cls.nodes
    
    @classmethod
    def add_node(cls, node: 'Node'):
        if cls.get_instance()._creating_node:
            return
        cls.get_instance()._creating_node = True
        cls.nodes[node.path()] = node    
        # Call post-registration initialization, for looper node internal node creation
        if hasattr(node.__class__, 'post_registration_init'):
            node.__class__.post_registration_init(node)
        
        cls.get_instance()._creating_node = False

    @classmethod
    def node_from_name(cls, node_name: str) -> Optional['Node']:
        if node_name in cls.nodes:
            return cls.nodes[node_name]
        for path, node in cls.nodes.items(): #because of synsugar to work with only names, not paths
            if node_name == path.split('/')[-1]:
                return node
        return None



class NetworkItemType(Enum):
    """Enum representing types of network entities."""

    NODE = "node"
    CONNECTION = "connection"


class NetworkEntity(ABC):
    """
    Abstract base class for network entities in the procedural text generation application.

    This class serves as the foundation for all network-related objects, providing
    a common interface and shared functionality.

    Attributes:
        _instance_count (ClassVar[int]): Class variable to keep track of instances.

    """

    _instance_count: ClassVar[int] = 0

    def __init__(self) -> None:
        """
        Initialize a new NetworkEntity instance.

        Increments the instance count upon creation.
        """
        self.__class__._instance_count += 1

    @abstractmethod
    def network_item_type(self) -> NetworkItemType:
        """
        Return the type of network entity.

        Returns:
            NetworkItemType: An enum value representing the type of network entity.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement network_item_type method")

    @classmethod
    def get_instance_count(cls) -> int:
        """
        Get the total number of instances created for this class.

        Returns:
            int: The number of instances.
        """
        return cls._instance_count

    def __repr__(self) -> str:
        """
        Return a string representation of the NetworkEntity.

        Returns:
            str: A string representation of the object.
        """
        return f"{self.__class__.__name__}(type={self.network_item_type().name})"

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the NetworkEntity.

        Returns:
            str: A string description of the object.
        """
        return f"{self.__class__.__name__} of type {self.network_item_type().name}"


class NetworkItemType(Enum):
    NODE = auto()
    CONNECTION = auto()


class InternalPath:
    def __init__(self, path: str):
        self.path = self._normalize_path(path)

    def _normalize_path(self, path: str) -> str:
        return "/" + "/".join(part for part in path.split("/") if part)

    def parent(self) -> "InternalPath":
        parent_path = "/".join(self.path.split("/")[:-1])
        return InternalPath(parent_path if parent_path else "/")

    def name(self) -> str:
        return self.path.split("/")[-1]

    def relative_to(self, other: "InternalPath") -> str:
        self_parts = self.path.split("/")
        other_parts = other.path.split("/")

        # Find common prefix
        i = 0
        while (
            i < len(self_parts)
            and i < len(other_parts)
            and self_parts[i] == other_parts[i]
        ):
            i += 1

        up_count = len(other_parts) - i
        down_parts = self_parts[i:]

        relative_parts = [".."] * up_count + down_parts
        return "/".join(relative_parts) if relative_parts else "."

    def __str__(self) -> str:
        return self.path


class MobileItem(NetworkEntity):
    """
    Represents a mobile item in the network, inheriting from NetworkEntity.

    This class provides functionality for named, selectable, colored, and
    positionable items within the network.

    Attributes:
        _name (str): The name of the item.
        _path (InternalPath): The full path of the item in the internal network.
        _selected (bool): Whether the item is currently selected.
        _color (Tuple[float, float, float]): The color of the item (RGB, 0-1 range).
        _position (Tuple[float, float]): The x, y position of the item.
        _session_id (str): A unique identifier for the session.

    Class Attributes:session 
        _existing_session_ids (Set[int]): A set of all existing session IDs.
        all_MobileItems : A global list of nodes for UndoManager
    """

    _existing_session_ids: Set[int] = set()
    all_MobileItems = []

    def __init__(self, name: str, path: str, position=[0.0, 0.0]) -> None:
        """
        Initialize a new MobileItem.

        Args:
            name (str): The name of the item.
            path (str): The full path of the item in the internal network.
            position (Tuple[float, float]): The initial x, y position of the item.
        """


        MobileItem.all_MobileItems.append(self)
        UndoManager().undo_stack.append((self.delete, ()))
        UndoManager().redo_stack.clear()                    

        super().__init__()
        self._name: str = name
        self._path: InternalPath = InternalPath(path)
        self._selected: bool = False
        self._color: Tuple[float, float, float] = (1.0, 1.0, 1.0)  # Default to white
        self._position: Tuple[float, float] = position
        self._session_id: int = self._generate_unique_session_id()

    def delete(self):
        if self in MobileItem.all_MobileItems:
            MobileItem.all_MobileItems.remove(self)
            state = self.__dict__.copy()
            UndoManager().undo_stack.append((MobileItem.recreate, (state,)))
            UndoManager().redo_stack.clear()
            del self

    @classmethod
    def recreate(cls, state):
        new_MobileItem = cls.__new__(cls)
        new_MobileItem.__dict__.update(state)
        cls.all_MobileItems.append(new_MobileItem)
        UndoManager().undo_stack.append((new_MobileItem.delete, ()))
        UndoManager().redo_stack.clear()
        return new_MobileItem

    def name(self) -> str:
        """Get the name of the item."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the item. Args: name (str): The new name for the item."""
        # Update the name
        self._name = name


    def path(self) -> str:
        """Get the full path of the item in the internal network."""
        return str(self._path)

    def session_id(self) -> str:
        """Get the unique session ID of the item."""
        return self._session_id

    @classmethod
    def bulk_add(cls, items: List[Dict[str, Any]]) -> List["MobileItem"]:
        """
        Create multiple MobileItem instances in bulk.

        This method efficiently creates multiple MobileItem instances,
        ensuring unique session IDs for all new items.

        Args:
            items (List[Dict[str, Any]]): A list of dictionaries, each containing the parameters for a new MobileItem.

        Returns:
            List[MobileItem]: A list of newly created MobileItem instances.

        Raises:
            RuntimeError: If unable to generate unique session IDs for all items.
        """
        new_items = []
        new_session_ids = set()

        def create_item(item_data: Dict[str, Any]) -> "MobileItem":
            new_item = cls(
                name=item_data["name"],
                path=item_data["path"],
                position=item_data["position"],
            )
            new_session_ids.add(new_item.session_id())
            return new_item

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            future_to_item = {
                executor.submit(create_item, item): item for item in items
            }
            for future in as_completed(future_to_item):
                new_items.append(future.result())

        # Check for uniqueness across all new and existing session IDs
        if len(new_session_ids) != len(items) or not new_session_ids.isdisjoint(
            cls._existing_session_ids
        ):
            raise RuntimeError("Failed to generate unique session IDs for all items")

        # If all checks pass, update the existing session IDs
        cls._existing_session_ids.update(new_session_ids)

        return new_items

    @classmethod
    def _generate_unique_session_id(cls) -> int:
        """
        Generate a unique integer session ID.

        Returns:
            int: A unique session ID.

        Raises:
            RuntimeError: If unable to generate a unique ID after 100 attempts.
        """
        for _ in range(100):  # Limit attempts to prevent infinite loop
            new_id = cls._generate_session_id()
            if new_id not in cls._existing_session_ids:
                cls._existing_session_ids.add(new_id)
                return new_id
        raise RuntimeError("Unable to generate a unique session ID")

    @staticmethod
    def _generate_session_id() -> int:
        """Generate an integer session ID using UUID."""
        return uuid.uuid4().int & ((1 << 63) - 1)  # Ensure it fits in a 64-bit signed integer

    def __repr__(self) -> str:
        """Return a string representation of the MobileItem."""
        return f"MobileItem(name='{self._name}', path='{self._path}', position={self._position})"

    def network_item_type(self) -> NetworkItemType:
        """
        Implement the abstract method from NetworkEntity.

        Returns:
            NetworkItemType: The type of this network item (always NODE for MobileItem).
        """
        return NetworkItemType.NODE

    def __del__(self) -> None:
        """
        Clean up when the object is deleted.

        Removes the session ID from the set of existing IDs.
        """
        self._existing_session_ids.discard(self._session_id)
        # TODO Add undo logic


from typing import Optional

from base_classes import NetworkEntity, NetworkItemType


class NodeConnection(NetworkEntity):
    """
    Represents a connection between two nodes in the network.

    This class inherits from NetworkEntity and provides information about
    the connection between an output of one node and an input of another node.
    """

    def __init__(
        self,
        output_node: "Node",
        input_node: "Node",
        output_index: int,
        input_index: int,
    ):
        super().__init__()
        self._output_node: "Node" = output_node
        self._input_node: "Node" = input_node
        self._output_index: int = output_index
        self._input_index: int = input_index
        self._selected: bool = False

    def output_node(self) -> "Node":
        """Returns the node on the output side of this connection."""
        return self._output_node

    def input_node(self) -> "Node":
        """Returns the node on the input side of this connection."""
        return self._input_node

    def output_index(self) -> int:
        """Returns the index of the output connection on the output node."""
        return self._output_index

    def input_index(self) -> int:
        """Returns the index of the input connection on the input node."""
        return self._input_index

    def output_name(self) -> str:
        """Returns the name of the output connection on the output node."""
        return self._output_node.output_names()[self._output_index]

    def input_name(self) -> str:
        """Returns the name of the input connection on the input node."""
        return self._input_node.input_names()[self._input_index]

    def output_data_type(self) -> str:
        """Returns the data type of the output connection on the output node."""
        return self._output_node.output_data_types()[self._output_index]

    def input_data_type(self) -> str:
        """Returns the data type of the input connection on the input node."""
        return self._input_node.input_data_types()[self._input_index]

    def is_selected(self) -> bool:
        """Returns True if the connection is selected, False otherwise."""
        return self._selected

    def set_selected(self, selected: bool = True) -> None:
        """Selects or deselects this connection."""
        self._selected = selected
        # TODO Add undo logic

    def network_item_type(self) -> NetworkItemType:
        """Implement the abstract method from NetworkEntity."""
        return NetworkItemType.CONNECTION

    def __repr__(self) -> str:
        """Returns a string representation of the NodeConnection."""
        return (
            f"NodeConnection(output_node={self._output_node.name()}, "
            f"input_node={self._input_node.name()}, "
            f"output_index={self._output_index}, "
            f"input_index={self._input_index})"
        )


import importlib
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class NodeState(Enum):
    COOKING = "cooking"
    UNCHANGED = "unchanged"
    UNCOOKED = "uncooked"
    COOKED = "cooked"


class Node(MobileItem):
    """
    Represents a Node in the workspace, inheriting from MobileItem.
    This class implements the Composite pattern, allowing for a hierarchical structure of nodes.
    It also implements the Observer pattern for NodeConnections.
    """


    def __init__(
        self, name: str, path: str, position: List[float], node_type: NodeType
    ):
        super().__init__(name, path, position)
        self._node_type: NodeType = node_type
        self._children: List["Node"] = []
        self._depth = self._calculate_depth()
        self._inputs: Dict[str, NodeConnection] = {}
        self._outputs: Dict[str, List[NodeConnection]] = {}
#        self._comment: str = ""
        self._state: NodeState = NodeState.UNCOOKED
        self._errors: List[str] = []
        self._warnings: List[str] = []
        self._is_time_dependent = False  # New attribute for time-dependent nodes
        self._last_cook_time = 0.0  # New attribute for last cook duration
        self._cook_count = 0  # New attribute for cooking count
        # self._messages: List[str] = []

    def node_path(self) -> str:
        """Returns the current location in the hierarchy of the workspace."""
        return self.path()

    def _calculate_depth(self) -> int:
            """Calculate the depth of this looper node based on its path."""
            return (self.path().count('/') + 1)

    def children(self) -> Tuple["Node", ...]:
        """Returns a tuple of the list of nodes it's connected to on its output."""
        return tuple(self._children)

    @classmethod
    def create_node(cls, node_type: NodeType, node_name: Optional[str] = None, parent_path: str = "/") -> "Node":
        """
        Creates a node of the specified type.

        Args:
            node_type (NodeType): The type of node to create.
            node_name (Optional[str]): The name for the new node. If None, a default name will be generated.
            parent_path (str): The path where the new node should be created. Defaults to root "/".

        Returns:
            Node: The newly created node.

        Raises:
            ImportError: If the module for the specified node type cannot be imported.
            AttributeError: If the node class cannot be found in the imported module.
            ValueError: If the specified parent path does not exist.
        """
        # Validate parent path
        if parent_path != "/" and not NodeEnvironment.node_exists(parent_path):
            raise ValueError(f"Parent path '{parent_path}' does not exist.")

        base_name = node_name or f"{node_type.value}"
        new_name = base_name
        counter = 1

        while f"{parent_path}/{new_name}" in NodeEnvironment.nodes:
            match = re.match(r"(.+)_(\d+)$", new_name)
            if match:
                base_name, counter = match.groups()
                counter = int(counter) + 1
            new_name = f"{base_name}_{counter}"
            counter += 1

        new_path = f"{parent_path.rstrip('/')}/{new_name}"

        try:
            module_name = f"nodes.{node_type.value}_node"
            module = importlib.import_module(module_name)
            
            # Convert snake_case to PascalCase and remove '_node' suffix
            class_name = ''.join(word.capitalize() for word in node_type.value.split('_'))
            node_class = getattr(module, f"{class_name}Node")

            new_node = node_class(new_name, new_path, node_type)
            new_node._session_id = new_node._generate_unique_session_id()
            NodeEnvironment.add_node(new_node)  # Use the new add_node method
            #print("Created new node: ",new_node.name(), new_node, " - at: ", parent_path)

            # Call post-registration initialization
            if hasattr(new_node.__class__, 'post_registration_init'):
                new_node.__class__.post_registration_init(new_node)

            return new_node
        except ImportError:
            raise ImportError(f"Could not import module for node type: {node_type.value}")
        except AttributeError:
            raise AttributeError(f"Could not find node class for node type: {node_type.value}")
        # TODO Add undo logic

    def destroy(self) -> None:
        """Deletes this node and its connections."""
        for connection in list(self.inputs()) + list(self.outputs()):
            self._remove_connection(connection)
        if self.parent():
            self.parent()._children.remove(self)
        # TODO Add undo logic


    def type(self) -> NodeType:
        """Returns the NodeType for this node."""
        return self._node_type

    def inputs(self) -> Tuple[NodeConnection, ...]:
        """Returns a tuple of the NodeConnections connected to this node's input."""
        return tuple(self._inputs.values())

    def input_nodes(self) -> List['Node']:
        """
        Returns a list of all nodes connected to this node's inputs.
            """
        return [conn.output_node() for conn in self.inputs()]

    def outputs(self) -> Tuple["Node", ...]:
        """Returns a tuple of the nodes connected to this node's output."""
        return tuple(conn.input_node() for conns in self._outputs.values() for conn in conns)

    def set_input(self, input_index: int, input_node: "Node", output_index: str = "output") -> None:
        """Connects an input of this node to an output of another node."""
        if hasattr(self, 'SINGLE_INPUT') and self.SINGLE_INPUT and self._inputs:
            self.add_warning(f"Node type {self.__class__.__name__} accepts only one input. Existing input will be replaced.")
            self._remove_connection(next(iter(self._inputs.values())))

        if input_index in self._inputs:
            self._remove_connection(self._inputs[input_index])

        connection = NodeConnection(input_node, self, output_index, input_index)
        print("New Connection: from input ", self.name(), " to output: ", input_node.name())
        self._inputs[input_index] = connection
        input_node._outputs.setdefault(output_index, []).append(connection)
        # TODO Add undo logic

    def remove_input(self, input_index: str) -> None:
        """Removes the connection to the specified input."""
        if input_index in self._inputs:
            self._remove_connection(self._inputs[input_index])
        # TODO Add undo logic

    def _remove_connection(self, connection: NodeConnection) -> None:
        """Removes a connection from both nodes it connects."""
        if connection.input_index() in self._inputs:
            del self._inputs[connection.input_index()]
        if connection.output_index() in connection.output_node()._outputs:
            connection.output_node()._outputs[connection.output_index()].remove(
                connection
            )
        # TODO Add undo logic

    def state(self) -> NodeState:
        """Returns the current state of the node."""
        return self._state

    def set_state(self, state: NodeState) -> None:
        """Sets the state of the node."""
        self._state = state
        # TODO Add undo logic

    def errors(self) -> Tuple[str, ...]:
        """Returns a tuple of error messages associated with this node."""
        return tuple(self._errors)

    def add_error(self, error: str) -> None:
        """Adds an error message to this node."""
        self._errors.append(error)
        # TODO Add undo logic

    def clear_errors(self) -> None:
        """Clears all error messages from this node."""
        self._errors.clear()
        # TODO Add undo logic

    def warnings(self) -> Tuple[str, ...]:
        """Returns a tuple of warning messages associated with this node."""
        return tuple(self._warnings)

    def add_warning(self, warning: str) -> None:
        """Adds a warning message to this node."""
        self._warnings.append(warning)
        # TODO Add undo logic

    def clear_warnings(self) -> None:
        """Clears all warning messages from this node."""
        self._warnings.clear()
        # TODO Add undo logic

    def input_names(self) -> Dict[str, str]:
        """Returns a dictionary of input names for this node type."""
        return {}  # To be implemented by subclasses

    def output_names(self) -> Dict[str, str]:
        """Returns a dictionary of output names for this node type."""
        return {}  # To be implemented by subclasses

    def input_data_types(self) -> Dict[str, str]:
        """Returns a dictionary of input data types for this node type."""
        return {}  # To be implemented by subclasses

    def output_data_types(self) -> Dict[str, str]:
        """Returns a dictionary of output data types for this node type."""
        return {}  # To be implemented by subclasses

    def network_item_type(self) -> NetworkItemType:
        """Implement the abstract method from NetworkEntity."""
        return NetworkItemType.NODE

    def isTimeDependent(self) -> bool:
        """Return whether the node is time dependent."""
        return self._is_time_dependent

    def cook_dependencies(self) -> List['Node']:
        """
        Gathers all input nodes that this node depends on into a list in the correct order (furthest nodes first).
        The actual cooking is deferred and should be handled later by the last node in the chain.
        Returns a list of nodes in the correct order they should be cooked.
        """
        nodes_to_cook: List[Node] = []
        visited_nodes: Set[Node] = set()  # To track nodes that are already processed

        def dfs(node: Node):
            if node in visited_nodes:
                return
            # First mark this node as visited to avoid cyclic dependencies
            visited_nodes.add(node)

            # Recursively process all input nodes (depth-first)
            for input_node in node.input_nodes():
                dfs(input_node)

            # Once all dependencies are processed, add the current node to the cook list
            if node.needs_to_cook():
                nodes_to_cook.append(node)
                #print(f"Adding {node.name()} to the cook list from {self.name()}")
            #else:
                #print(f"{node.name()} does not need to cook from {self.name()}")

        # Start the DFS from the current node's inputs
        for input_node in self.input_nodes():
            dfs(input_node)
        #print("nodes to cook: \n",nodes_to_cook)
        return nodes_to_cook  # Return the nodes in the correct order (DFS ensures furthest nodes first)



    def cook(self, force: bool = False) -> None:
        """
        Public cook method which includes dependency handling and core cooking logic.
        This method should be called externally and will manage dependency cooking before
        executing the core logic of this node.
        """
        print(f"☀ Starting cook for {self.name()}")

        # Gather the list of dependencies that need to be cooked
        dependencies = self.cook_dependencies()

        # # Cook each node in the dependency list using their internal cook method
        for node in dependencies:
            print(f"Cooking {node.name()} via _internal_cook() from {self.name()}")
            node._internal_cook()

        # Now, execute the internal cooking logic for this node after dependencies are cooked
        self._internal_cook()



    def last_cook_time(self) -> float:
        """Returns the duration of the node’s last cook in milliseconds. Returns a 0 if the node cannot be cooked, doesn’t need to be cooked, is bypassed, or locked"""
        return self._last_cook_time

    def needs_to_cook(self) -> bool:
        """
        Determines if the node needs to be cooked.
        This method should be overridden by subclasses to implement specific logic.
        """
        return self._is_time_dependent or self.state() != NodeState.UNCHANGED

    def cook_count(self) -> int:
        """Returns the number of times this node has cooked in the current session."""
        return self._cook_count


    def inputs_with_indices(self, use_names: bool = False) -> Sequence[Tuple["Node", Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected input of this node."""
        result = []
        for input_index, connection in self._inputs.items():
            output_node = connection.output_node()
            output_index = connection.output_index()
            if use_names:
                input_name = self.input_names().get(input_index, input_index)
                output_name = output_node.output_names().get(output_index, output_index)
                result.append((output_node, output_name, input_name))
            else:
                result.append((output_node, output_index, input_index))
        return result


    def outputs_with_indices(self, use_names: bool = False) -> Sequence[Tuple["Node", Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected output of this node."""
        result = []
        for output_index, connections in self._outputs.items():
            for connection in connections:
                input_node = connection.input_node()
                input_index = connection.input_index()
                if use_names:
                    output_name = self.output_names().get(output_index, output_index)
                    input_name = input_node.input_names().get(input_index, input_index)
                    result.append((input_node, output_name, input_name))
                else:
                    result.append((input_node, output_index, input_index))
        return result

    def eval(self):
        # implement in class as a simple return of the
        # state of the self._output after previous cooking
        
        pass

    def __repr__(self) -> str:
        """Returns a string representation of the Node."""
        return (
            f"Node(name='{self.name()}', type={self._node_type}, path='{self.path()}')"
        )



