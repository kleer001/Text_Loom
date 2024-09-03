import importlib
import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum, auto
import uuid
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple
from UndoManager import UndoManager

def generate_node_types():
    node_types = {}
    nodes_dir = Path(__file__).parent / "nodes"
    for file in nodes_dir.glob("*_node.py"):
        node_type_name = file.stem.replace("_node", "").upper()
        node_types[node_type_name] = node_type_name.lower()
    return node_types


class NodeType(Enum):
    pass


NodeType = Enum("NodeType", generate_node_types(), type=NodeType)

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

    def children(self) -> Tuple["Node", ...]:
        """Returns a tuple of the list of nodes it's connected to on its output."""
        return tuple(self._children)

    @classmethod
    def create_node(
        cls, node_type: NodeType, node_name: Optional[str] = None
    ) -> "Node":
        """
        Creates a node of the specified type.

        Args:
            node_type (NodeType): The type of node to create.
            node_name (Optional[str]): The name for the new node. If None, a default name will be generated.

        Returns:
            Node: The newly created node.

        Raises:
            ImportError: If the module for the specified node type cannot be imported.
            AttributeError: If the node class cannot be found in the imported module.
        """
        base_name = node_name or f"{node_type.value}"
        new_name = base_name
        counter = 1

        while f"/{new_name}" in NodeEnvironment.nodes:
            match = re.match(r"(.+)_(\d+)$", new_name)
            if match:
                base_name, counter = match.groups()
                counter = int(counter) + 1
            new_name = f"{base_name}_{counter}"
            counter += 1

        new_path = f"/{new_name}"

        try:
            module_name = f"nodes.{node_type.value}_node"
            module = importlib.import_module(module_name)
            node_class_name = f"{node_type.value.capitalize()}Node"
            node_class = getattr(module, node_class_name)

            new_node = node_class(new_name, new_path, (0.0, 0.0), node_type)
            new_node._session_id = new_node._generate_unique_session_id()
            NodeEnvironment.nodes[new_path] = new_node
            return new_node
        except ImportError:
            raise ImportError(
                f"Could not import module for node type: {node_type.value}"
            )
        except AttributeError:
            raise AttributeError(
                f"Could not find node class for node type: {node_type.value}"
            )
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
        """Returns a tuple of the nodes connected to this node's input."""
        return tuple(self._inputs.values())

    def outputs(self) -> Tuple[NodeConnection, ...]:
        """Returns a tuple of the nodes connected to this node's output."""
        return tuple(conn for conns in self._outputs.values() for conn in conns)

    def set_input(
        self, input_index: str, input_node: "Node", output_index: str
    ) -> None:
        """Connects an input of this node to an output of another node."""
        if input_index in self._inputs:
            self._remove_connection(self._inputs[input_index])
        connection = NodeConnection(input_node, self, output_index, input_index)
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

    def lastCookTime(self) -> float:
        """Returns the duration of the node’s last cook in milliseconds. Returns a 0 if the node cannot be cooked, doesn’t need to be cooked, is bypassed, or locked"""
        return self._last_cook_time

    def cook(self, force: bool = False) -> None:
        """Asks or forces the node to re-cook."""
        # Add cooking logic here (not provided in this context)
        if force:
            self.set_state(NodeState.UNCOOKED)

    def needsToCook(self) -> bool:
        """Asks if the node needs to re-cook."""
        return self._is_time_dependent and (
            self.get_state() == NodeState.UNCOOKED or force
        )

    def cookCount(self) -> int:
        """Returns the number of times this node has cooked in the current session."""
        return self._cook_count

    def inputsWithIndices(self, use_names: bool = False) -> Sequence[Tuple["Node", Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected input of this node."""
        if not use_names:
            return list((node, output_index, self._inputs[output_index].input_index()) for node, output_index in self._inputs.items())
        else:
            # Assuming input_names() and output_names() methods are implemented as expected
            input_dict = self.input_names()
            return [(node, output_name, self._inputs[output_index].input_index()) for node, output_name in input_dict.items()]

    def outputsWithIndices(self, use_names: bool = False) -> Sequence[Tuple["Node", Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected output of this node."""
        if not use_names:
            return list((node, input_index, self._inputs[output_index].output_index()) for input_index, (node, output_index) in self._outputs.items())
        else:
            # Assuming input_names() and output_names() methods are implemented as expected
            output_dict = self.output_names()
            return [(node, output_name, self._inputs[output_index].output_index()) for output_name, (node, output_index) in output_dict.items()]


    def __repr__(self) -> str:
        """Returns a string representation of the Node."""
        return (
            f"Node(name='{self.name()}', type={self._node_type}, path='{self.path()}')"
        )



