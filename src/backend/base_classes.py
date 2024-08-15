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