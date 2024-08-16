from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import ClassVar

class NetworkItemType(Enum):
    """Enum representing types of network entities."""
    NODE = auto()
    CONNECTION = auto()

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


from typing import List, Tuple, Optional, Set, Dict, Any
from base64 import b64encode
from os import urandom
from concurrent.futures import ThreadPoolExecutor, as_completed

class InternalPath:
    def __init__(self, path: str):
        self.path = self._normalize_path(path)

    def _normalize_path(self, path: str) -> str:
        return '/' + '/'.join(part for part in path.split('/') if part)

    def parent(self) -> 'InternalPath':
        parent_path = '/'.join(self.path.split('/')[:-1])
        return InternalPath(parent_path if parent_path else '/')

    def name(self) -> str:
        return self.path.split('/')[-1]

    def relative_to(self, other: 'InternalPath') -> str:
        self_parts = self.path.split('/')
        other_parts = other.path.split('/')
        
        # Find common prefix
        i = 0
        while i < len(self_parts) and i < len(other_parts) and self_parts[i] == other_parts[i]:
            i += 1
        
        up_count = len(other_parts) - i
        down_parts = self_parts[i:]
        
        relative_parts = ['..'] * up_count + down_parts
        return '/'.join(relative_parts) if relative_parts else '.'

    def __str__(self) -> str:
        return self.path


from typing import List, Tuple, Optional, Set, Dict, Any
from base64 import b64encode
from os import urandom
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod
from enum import Enum, auto

class NetworkItemType(Enum):
    NODE = auto()
    CONNECTION = auto()

class NetworkEntity(ABC):
    @abstractmethod
    def network_item_type(self) -> NetworkItemType:
        pass

class InternalPath:
    def __init__(self, path: str):
        self.path = self._normalize_path(path)

    def _normalize_path(self, path: str) -> str:
        return '/' + '/'.join(part for part in path.split('/') if part)

    def parent(self) -> 'InternalPath':
        parent_path = '/'.join(self.path.split('/')[:-1])
        return InternalPath(parent_path if parent_path else '/')

    def name(self) -> str:
        return self.path.split('/')[-1]

    def relative_to(self, other: 'InternalPath') -> str:
        self_parts = self.path.split('/')
        other_parts = other.path.split('/')
        
        # Find common prefix
        i = 0
        while i < len(self_parts) and i < len(other_parts) and self_parts[i] == other_parts[i]:
            i += 1
        
        up_count = len(other_parts) - i
        down_parts = self_parts[i:]
        
        relative_parts = ['..'] * up_count + down_parts
        return '/'.join(relative_parts) if relative_parts else '.'

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
        _position (List[float, float]): The x, y position of the item.
        _session_id (str): A unique 8-digit base62 identifier for the session.
    
    Class Attributes:
        _existing_session_ids (Set[str]): A set of all existing session IDs.
    """

    _existing_session_ids: Set[str] = set()

    def __init__(self, name: str, path: str, position: List[float, float]) -> None:
        """
        Initialize a new MobileItem.
        
        Args:
            name (str): The name of the item.
            path (str): The full path of the item in the internal network.
            position (List[float, float]): The initial x, y position of the item.
        """
        super().__init__()
        self._name: str = name
        self._path: InternalPath = InternalPath(path)
        self._selected: bool = False
        self._color: Tuple[float, float, float] = (1.0, 1.0, 1.0)  # Default to white
        self._position: List[float, float] = position
        self._session_id: str = self._generate_unique_session_id()

    def name(self) -> str:
        """Get the name of the item."""
        return self._name

    def set_name(self, name: str) -> None:
        """
        Set the name of the item.
        
        Args:
            name (str): The new name for the item.
        """
        self._name = name

    def path(self) -> str:
        """Get the full path of the item in the internal network."""
        return str(self._path)

    def relative_path_to(self, base_node: 'MobileItem') -> str:
        """
        Get the relative path to another node from this one.
        
        Args:
            base_node (MobileItem): The node to calculate the relative path to.
        
        Returns:
            str: The relative path between the two nodes.
        """
        return self._path.relative_to(base_node._path)

    def is_selected(self) -> bool:
        """Check if the item is selected."""
        return self._selected

    def set_selected(self, selected: bool = True) -> None:
        """
        Select or deselect the item.
        
        Args:
            selected (bool): True to select, False to deselect. Defaults to True.
        """
        self._selected = selected

    def color(self) -> Tuple[float, float, float]:
        """Get the color of the item."""
        return self._color

    def set_color(self, color: Tuple[float, float, float]) -> None:
        """
        Set the color of the item.
        
        Args:
            color (Tuple[float, float, float]): The new color (RGB, 0-1 range).
        
        Raises:
            ValueError: If the color values are not in the range [0, 1].
        """
        if not all(0 <= c <= 1 for c in color):
            raise ValueError("Color values must be between 0 and 1")
        self._color = color

    def session_id(self) -> str:
        """Get the unique session ID of the item."""
        return self._session_id

    def position(self) -> List[float, float]:
        """Get the current position of the item."""
        return self._position

    def set_position(self, xy: List[float, float]) -> None:
        """
        Set the position of the item.
        
        Args:
            xy (List[float, float]): The new x, y position.
        """
        self._position = xy

    def move(self, xy: List[float, float]) -> None:
        """
        Move the item by the given increments.
        
        Args:
            xy (List[float, float]): The x, y increments to move by.
        """
        self._position[0] += xy[0]
        self._position[1] += xy[1]

    @classmethod
    def bulk_add(cls, items: List[Dict[str, Any]]) -> List['MobileItem']:
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

        def create_item(item_data: Dict[str, Any]) -> 'MobileItem':
            new_item = cls(
                name=item_data['name'],
                path=item_data['path'],
                position=item_data['position']
            )
            new_session_ids.add(new_item.session_id())
            return new_item

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            future_to_item = {executor.submit(create_item, item): item for item in items}
            for future in as_completed(future_to_item):
                new_items.append(future.result())

        # Check for uniqueness across all new and existing session IDs
        if len(new_session_ids) != len(items) or not new_session_ids.isdisjoint(cls._existing_session_ids):
            raise RuntimeError("Failed to generate unique session IDs for all items")

        # If all checks pass, update the existing session IDs
        cls._existing_session_ids.update(new_session_ids)

        return new_items

    @classmethod
    def _generate_unique_session_id(cls) -> str:
        """
        Generate a unique 8-digit base62 session ID.
        
        Returns:
            str: A unique session ID.
        
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
    def _generate_session_id() -> str:
        """Generate an 8-digit base62 session ID."""
        return b64encode(urandom(6)).decode('ascii')[:8]

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


from typing import Optional
from base_classes import NetworkEntity, NetworkItemType

class NodeConnection(NetworkEntity):
    """
    Represents a connection between two nodes in the network.
    
    This class inherits from NetworkEntity and provides information about
    the connection between an output of one node and an input of another node.
    """

    def __init__(self, output_node: 'Node', input_node: 'Node', 
                 output_index: str, input_index: str):
        super().__init__()
        self._output_node: 'Node' = output_node
        self._input_node: 'Node' = input_node
        self._output_index: str = output_index
        self._input_index: str = input_index
        self._selected: bool = False

    def output_node(self) -> 'Node':
        """Returns the node on the output side of this connection."""
        return self._output_node

    def input_node(self) -> 'Node':
        """Returns the node on the input side of this connection."""
        return self._input_node

    def output_index(self) -> str:
        """Returns the index of the output connection on the output node."""
        return self._output_index

    def input_index(self) -> str:
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

    def network_item_type(self) -> NetworkItemType:
        """Implement the abstract method from NetworkEntity."""
        return NetworkItemType.CONNECTION

    def __repr__(self) -> str:
        """Returns a string representation of the NodeConnection."""
        return (f"NodeConnection(output_node={self._output_node.name()}, "
                f"input_node={self._input_node.name()}, "
                f"output_index={self._output_index}, "
                f"input_index={self._input_index})")


from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from base_classes import MobileItem, NetworkEntity, NetworkItemType

class NodeState(Enum):
    COOKING = "cooking"
    UNCHANGED = "unchanged"
    UNCOOKED = "uncooked"

class NodeConnection(NetworkEntity):
    # ... (NodeConnection class implementation as provided earlier)

class Node(MobileItem):
    """
    Represents a Node in the workspace, inheriting from MobileItem.
    
    This class implements the Composite pattern, allowing for a hierarchical
    structure of nodes. It also implements the Observer pattern for NodeConnections.
    """

    def __init__(self, name: str, path: str, position: List[float, float], node_type_name: str):
        super().__init__(name, path, position)
        self._node_type_name: str = node_type_name
        self._children: List['Node'] = []
        self._inputs: Dict[str, NodeConnection] = {}
        self._outputs: Dict[str, List[NodeConnection]] = {}
        self._comment: str = ""
        self._state: NodeState = NodeState.UNCOOKED
        self._errors: List[str] = []
        self._warnings: List[str] = []
        self._messages: List[str] = []

    def node_path(self) -> str:
        """Returns the current location in the hierarchy of the workspace."""
        return self.path()

    def children(self) -> Tuple['Node', ...]:
        """Returns a tuple of the list of nodes it's connected to on its output."""
        return tuple(self._children)

    def create_node(self, node_type_name: str, node_name: Optional[str] = None) -> 'Node':
        """
        Creates a node of the specified type as a child of this node.
        
        This method could be extended to use a Factory pattern for creating
        different types of nodes.
        """
        # TODO: Implement node factory
        new_node = Node(node_name or f"{node_type_name}_{len(self._children)}", 
                        f"{self.node_path()}/{node_name or node_type_name}",
                        [0, 0],  # Default position
                        node_type_name)
        self._children.append(new_node)
        return new_node

    def destroy(self) -> None:
        """Deletes this node and its connections."""
        for connection in list(self.inputs()) + list(self.outputs()):
            self._remove_connection(connection)
        # Additional cleanup logic here
        # TODO: Remove this node from its parent's children list

    def is_current(self) -> bool:
        """Returns whether this node has been selected."""
        return self.is_selected()

    def set_current(self, is_current: bool = True) -> None:
        """Set or unset this node as selected for editing."""
        self.set_selected(is_current)

    def type(self) -> str:
        """Returns the node type name for this node."""
        # TODO: Return a NodeType object instead of a string
        return self._node_type_name

    def children_type(self) -> Tuple[str, ...]:
        """Returns the node types of the children of this node."""
        # TODO: Return NodeType objects instead of strings
        return tuple(child.type() for child in self._children)

    def inputs(self) -> Tuple[NodeConnection, ...]:
        """Returns a tuple of the nodes connected to this node's input."""
        return tuple(self._inputs.values())

    def outputs(self) -> Tuple[NodeConnection, ...]:
        """Returns a tuple of the nodes connected to this node's output."""
        return tuple(conn for conns in self._outputs.values() for conn in conns)

    def set_input(self, input_index: str, input_node: 'Node', output_index: str) -> None:
        """
        Set the output connection of another node to the numbered input connector of this node.
        """
        if input_index in self._inputs:
            self._remove_connection(self._inputs[input_index])
        
        new_connection = NodeConnection(input_node, self, output_index, input_index)
        self._inputs[input_index] = new_connection
        input_node._outputs.setdefault(output_index, []).append(new_connection)
        self._on_connection_changed(new_connection)

    def set_next_input(self, input_node: 'Node', output_index: str) -> None:
        """
        Connect the output connector from another node into the first unconnected input connector of this node.
        """
        available_inputs = set(self.input_names()) - set(self._inputs.keys())
        if not available_inputs:
            raise ValueError("No available input connections")
        next_input = min(available_inputs)
        self.set_input(next_input, input_node, output_index)

    def create_input_node(self, input_index: str, node_type_name: str, node_name: Optional[str] = None) -> 'Node':
        """Create a new node and connect it to one of this node's inputs."""
        new_node = self.create_node(node_type_name, node_name)
        self.set_input(input_index, new_node, "0")  # Assuming "0" is a valid output index
        return new_node

    def input_names(self) -> Tuple[str, ...]:
        """Returns a tuple of all the input names for this node."""
        # TODO: Implement input name logic based on node type
        return tuple()

    def output_names(self) -> Tuple[str, ...]:
        """Returns a tuple of all the output names for this node."""
        # TODO: Implement output name logic based on node type
        return tuple()

    def input_data_types(self) -> Dict[str, str]:
        """Returns a dictionary of input names to their data types."""
        # TODO: Implement input data type logic based on node type
        return {}

    def output_data_types(self) -> Dict[str, str]:
        """Returns a dictionary of output names to their data types."""
        # TODO: Implement output data type logic based on node type
        return {}

    def comment(self) -> str:
        """Returns the node's comment string."""
        return self._comment

    def set_comment(self, comment: str) -> None:
        """Set the node's comment string."""
        self._comment = comment

    def append_comment(self, comment: str) -> None:
        """Appends the given text to the comment on this node."""
        self._comment += comment

    def errors(self) -> Tuple[str, ...]:
        """Return the text of any errors from the last cook of this node."""
        return tuple(self._errors)

    def warnings(self) -> Tuple[str, ...]:
        """Return the text of any warnings from the last cook of this node."""
        return tuple(self._warnings)

    def messages(self) -> Tuple[str, ...]:
        """Return the text of any messages from the last cook of this node."""
        return tuple(self._messages)

    def _remove_connection(self, connection: NodeConnection) -> None:
        """Remove a connection from this node."""
        if connection.input_node() == self:
            del self._inputs[connection.input_index()]
        elif connection.output_node() == self:
            self._outputs[connection.output_index()].remove(connection)
            if not self._outputs[connection.output_index()]:
                del self._outputs[connection.output_index()]
        self._on_connection_changed(connection, removed=True)

    def _on_connection_changed(self, connection: NodeConnection, removed: bool = False) -> None:
        """Observer method called when a connection is added or removed."""
        # Implement any necessary logic here, e.g., updating node state
        self._state = NodeState.UNCOOKED

    def network_item_type(self) -> NetworkItemType:
        """Implement the abstract method from NetworkEntity."""
        return NetworkItemType.NODE

    def __repr__(self) -> str:
        """Return a string representation of the Node."""
        return f"Node(name='{self._name}', type='{self._node_type_name}', path='{self.node_path()}')"


