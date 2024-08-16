from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import final

class NetworkItemType(Enum):
    """Enum representing the types of network items."""
    NODE = auto()
    CONNECTION = auto()

class NetworkEntity(ABC):
    """
    Abstract base class representing a network entity.
    
    This class serves as the foundation for all network-related objects
    in the procedural text generation application. It defines the basic
    interface that all network entities must implement.

    Attributes:
        None

    Methods:
        networkItemType: Returns the type of the network entity.
    """

    @abstractmethod
    def networkItemType(self) -> NetworkItemType:
        """
        Get the type of this network entity.

        Returns:
            NetworkItemType: An enum value representing the type of this network entity.
        """
        pass

    @final
    def __repr__(self) -> str:
        """
        Return a string representation of the NetworkEntity.

        Returns:
            str: A string representation of the object.
        """
        return f"{self.__class__.__name__}(type={self.networkItemType().name})"

    def __eq__(self, other: object) -> bool:
        """
        Check if this NetworkEntity is equal to another object.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if not isinstance(other, NetworkEntity):
            return NotImplemented
        return self.networkItemType() == other.networkItemType()

    def __hash__(self) -> int:
        """
        Generate a hash value for this NetworkEntity.

        Returns:
            int: A hash value for the object.
        """
        return hash((self.__class__, self.networkItemType()))
    

from typing import List, Tuple, Optional, ClassVar, Set, Iterable
import random
import string
import weakref
from abc import ABC, abstractmethod

class MobileItem(NetworkEntity):
    """
    Represents a mobile item in the network, inheriting from NetworkEntity.
    
    This class provides basic functionality for items that can be moved,
    named, selected, and colored within the network.
    """

    _instances: ClassVar[Set[weakref.ref]] = set()
    _session_ids: ClassVar[Set[str]] = set()

    def __init__(self, name: str, position: List[float], color: Optional[List[float]] = None, session_id: Optional[str] = None):
        """
        Initialize a MobileItem.

        Args:
            name (str): The name of the item.
            position (List[float]): The initial position [x, y] of the item.
            color (Optional[List[float]]): The color of the item as [r, g, b], each 0-1. Defaults to None.
            session_id (Optional[str]): A pre-existing session ID. If None, a new one will be generated.
        """
        self._name: str = name
        self._position: List[float] = position
        self._color: List[float] = color or [0.5, 0.5, 0.5]  # Default to gray if no color provided
        self._selected: bool = False
        self._session_id: str = session_id if session_id else self._generate_unique_session_id()
        
        self._instances.add(weakref.ref(self))
        self._session_ids.add(self._session_id)

    def name(self) -> str:
        """Get the name of this item."""
        return self._name

    def setName(self, name: str) -> None:
        """
        Set the name of this item.

        Args:
            name (str): The new name for the item.
        """
        self._name = name

    @abstractmethod
    def path(self) -> str:
        """
        Get the full path of this item in the network.

        Returns:
            str: The full path starting with /.

        Note: This method must be implemented by subclasses to provide the correct path.
        """
        pass

    @abstractmethod
    def relativePathTo(self, base_node: 'MobileItem') -> str:
        """
        Get the relative path to another node from this one.

        Args:
            base_node (MobileItem): The base node to calculate the relative path from.

        Returns:
            str: The relative path.

        Note: This method must be implemented by subclasses to provide the correct relative path.
        """
        pass

    def isSelected(self) -> bool:
        """Check if this item is selected."""
        return self._selected

    def setSelected(self, select: bool = True) -> None:
        """
        Select or deselect this item.

        Args:
            select (bool): True to select, False to deselect. Defaults to True.
        """
        self._selected = select

    def color(self) -> List[float]:
        """Get the color of this item."""
        return self._color.copy()

    def setColor(self, color: List[float]) -> None:
        """
        Set the color of this item.

        Args:
            color (List[float]): The new color as [r, g, b], each 0-1.
        """
        if len(color) != 3 or not all(0 <= c <= 1 for c in color):
            raise ValueError("Color must be a list of 3 floats between 0 and 1")
        self._color = color

    def sessionId(self) -> str:
        """Get the unique session ID of this item."""
        return self._session_id

    def position(self) -> List[float]:
        """Get the position of this item."""
        return self._position.copy()

    def setPosition(self, xy: List[float]) -> None:
        """
        Set the position of this item.

        Args:
            xy (List[float]): The new position [x, y].
        """
        if len(xy) != 2:
            raise ValueError("Position must be a list of 2 floats")
        self._position = xy

    def move(self, xy: List[float]) -> None:
        """
        Move this item by the given increments.

        Args:
            xy (List[float]): The increments [dx, dy] to move by.
        """
        if len(xy) != 2:
            raise ValueError("Movement must be a list of 2 floats")
        self._position[0] += xy[0]
        self._position[1] += xy[1]

    @classmethod
    def _generate_unique_session_id(cls) -> str:
        """Generate a unique 8-digit base62 session ID."""
        while True:
            session_id = cls._generate_session_id()
            if session_id not in cls._session_ids:
                return session_id

    @staticmethod
    def _generate_session_id() -> str:
        """Generate an 8-digit base62 session ID."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(8))

    @classmethod
    def bulk_add(cls, items: Iterable['MobileItem']) -> None:
        """
        Add multiple MobileItems at once, ensuring unique session IDs.

        Args:
            items (Iterable[MobileItem]): An iterable of MobileItems to add.
        """
        new_session_ids = set(item.sessionId() for item in items)
        conflicting_ids = new_session_ids.intersection(cls._session_ids)

        for item in items:
            if item.sessionId() in conflicting_ids:
                new_id = cls._generate_unique_session_id()
                item._session_id = new_id
            cls._instances.add(weakref.ref(item))
            cls._session_ids.add(item.sessionId())

    def __del__(self):
        """Remove this instance from the set of instances when it's deleted."""
        self._instances.discard(weakref.ref(self))
        self._session_ids.discard(self._session_id)

    def __repr__(self) -> str:
        """Return a string representation of the MobileItem."""
        return f"{self.__class__.__name__}(name='{self._name}', position={self._position}, color={self._color}, session_id='{self._session_id}')"

    @abstractmethod
    def networkItemType(self) -> NetworkItemType:
        """
        Get the type of this network entity.

        Returns:
            NetworkItemType: An enum value representing the type of this network entity.
        """
        pass


    from typing import List, Tuple, Optional, Dict
from base_classes import MobileItem, NetworkItemType

class Node(MobileItem):
    def __init__(self, name: str, position: List[float], node_type: 'NodeType', color: Optional[List[float]] = None):
        super().__init__(name, position, color)
        self._node_type: 'NodeType' = node_type
        self._inputs: List[Optional['NodeConnection']] = []
        self._outputs: List['NodeConnection'] = []
        self._comment: str = ""
        self._is_current: bool = False
        self._errors: List[str] = []
        self._warnings: List[str] = []
        self._messages: List[str] = []

    def node_path(self) -> str:
        path = f"/{self.name()}"
        parent = self.parent()
        while parent:
            path = f"/{parent.name()}" + path
            parent = parent.parent()
        return path

    def children(self) -> Tuple['Node', ...]:
        return tuple(conn.inputNode() for conn in self._outputs)

    def createNode(self, node_type_name: str, node_name: Optional[str] = None) -> 'Node':
        # This would need to be implemented based on your node creation system
        # It should check against available node types in the nodes/ directory
        raise NotImplementedError("createNode() needs to be implemented")

    def destroy(self) -> None:
        for conn in self._inputs + self._outputs:
            conn.destroy()
        # Additional cleanup as needed

    def isCurrent(self) -> bool:
        return self._is_current

    def setCurrent(self, is_current: bool = True) -> None:
        self._is_current = is_current

    def type(self) -> 'NodeType':
        return self._node_type

    def childrenType(self) -> Tuple['NodeType', ...]:
        return tuple(child.type() for child in self.children())

    def inputs(self) -> Tuple[Optional['Node'], ...]:
        return tuple(conn.outputNode() if conn else None for conn in self._inputs)

    def outputs(self) -> Tuple['Node', ...]:
        return tuple(conn.inputNode() for conn in self._outputs)

    def setInput(self, input_index: int, output_node: 'Node', output_index: int = 0) -> None:
        while len(self._inputs) <= input_index:
            self._inputs.append(None)
        if self._inputs[input_index]:
            self._inputs[input_index].destroy()
        self._inputs[input_index] = NodeConnection(output_node, self, output_index, input_index)

    def setNextInput(self, output_node: 'Node', output_index: int = 0) -> None:
        next_input = self._inputs.index(None) if None in self._inputs else len(self._inputs)
        self.setInput(next_input, output_node, output_index)

    def createInputNode(self, input_index: int, node_type_name: str, node_name: Optional[str] = None) -> 'Node':
        new_node = self.createNode(node_type_name, node_name)
        self.setInput(input_index, new_node)
        return new_node

    def inputNames(self) -> Tuple[str, ...]:
        return self._node_type.inputNames()

    def outputNames(self) -> Tuple[str, ...]:
        return self._node_type.outputNames()

    def comment(self) -> str:
        return self._comment

    def setComment(self, comment: str) -> None:
        self._comment = comment

    def appendComment(self, comment: str) -> None:
        self._comment += comment

    def errors(self) -> Tuple[str, ...]:
        return tuple(self._errors)

    def warnings(self) -> Tuple[str, ...]:
        return tuple(self._warnings)

    def messages(self) -> Tuple[str, ...]:
        return tuple(self._messages)

    def networkItemType(self) -> NetworkItemType:
        return NetworkItemType.NODE

    def __repr__(self) -> str:
        return f"Node(name='{self.name()}', type='{self._node_type}', position={self.position()})"

class NodeConnection:
    def __init__(self, output_node: 'Node', input_node: 'Node', output_index: int, input_index: int):
        self._output_node = output_node
        self._input_node = input_node
        self._output_index = output_index
        self._input_index = input_index
        self._selected = False

        if self._output_node == self._input_node:
            print("Warning: Connection creates a cycle. Deleting connection.")
            self.destroy()

    def outputNode(self) -> 'Node':
        return self._output_node

    def inputNode(self) -> 'Node':
        return self._input_node

    def outputIndex(self) -> int:
        return self._output_index

    def inputIndex(self) -> int:
        return self._input_index

    def outputName(self) -> str:
        return self._output_node.outputNames()[self._output_index]

    def inputName(self) -> str:
        return self._input_node.inputNames()[self._input_index]

    def outputDataType(self) -> str:
        return self._output_node.type().outputTypes()[self._output_index]

    def inputDataType(self) -> str:
        return self._input_node.type().inputTypes()[self._input_index]

    def isSelected(self) -> bool:
        return self._selected

    def setSelected(self, selected: bool = True) -> None:
        self._selected = selected

    def destroy(self) -> None:
        if self in self._output_node._outputs:
            self._output_node._outputs.remove(self)
        if self._input_node._inputs[self._input_index] == self:
            self._input_node._inputs[self._input_index] = None

    def __repr__(self) -> str:
        return f"NodeConnection(output={self._output_node.name()}[{self._output_index}], input={self._input_node.name()}[{self._input_index}])"
