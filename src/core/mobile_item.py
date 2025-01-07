from abc import ABC, abstractmethod
from enum import Enum, auto
import uuid
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from core.enums import NetworkItemType
from core.internal_path import InternalPath
from core.network_entity import NetworkEntity
from core.node_environment import NodeEnvironment
if TYPE_CHECKING:
    from core.node import Node
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    def __init__(self, name: str, path: str, position=[0.0, 0.0]) ->None:
        """
        Initialize a new MobileItem.

        Args:
            name (str): The name of the item.
            path (str): The full path of the item in the internal network.
            position (Tuple[float, float]): The initial x, y position of the item.
        """
        MobileItem.all_MobileItems.append(self)
        super().__init__()
        self._name: str = name
        self._path: InternalPath = InternalPath(path)
        self._selected: bool = False
        self._color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self._position: Tuple[float, float] = position
        self._session_id: int = self._generate_unique_session_id()

    def delete(self):
        if self in MobileItem.all_MobileItems:
            MobileItem.all_MobileItems.remove(self)
            state = self.__dict__.copy()
            del self

    @classmethod
    def recreate(cls, state):
        new_MobileItem = cls.__new__(cls)
        new_MobileItem.__dict__.update(state)
        cls.all_MobileItems.append(new_MobileItem)
        return new_MobileItem

    def name(self) ->str:
        """Get the name of the item."""
        return self._name

    def set_name(self, name: str) ->None:
        """
        Set the name of the item with uniqueness validation.
        
        Args:
            name (str): The new name for the item
            
        Raises:
            ValueError: If the name would create a duplicate in the current path
        """
        current_path = str(self._path.parent())
        base_name = name
        if re.search('_?\\d+$', base_name):
            new_name = base_name
        else:
            counter = 1
            while True:
                new_name = f'{base_name}_{counter}'
                new_path = f"{current_path.rstrip('/')}/{new_name}"
                if (new_path not in NodeEnvironment.nodes or 
                    NodeEnvironment.nodes[new_path] is self):
                    break
                counter += 1
        self._name = new_name
        self._path = InternalPath(f"{current_path.rstrip('/')}/{new_name}")
        if isinstance(self, Node):
            old_path = str(self._path)
            if old_path in NodeEnvironment.nodes:
                del NodeEnvironment.nodes[old_path]
            NodeEnvironment.nodes[str(self._path)] = self

    def rename(self, new_name: str) ->bool:
        current_path = str(self._path.parent())
        new_path = f"{current_path.rstrip('/')}/{new_name}"
        if new_path in NodeEnvironment.nodes and NodeEnvironment.nodes[new_path
            ] is not self:
            return False
        old_path = str(self._path)
        self._name = new_name
        self._path = InternalPath(new_path)
        if old_path in NodeEnvironment.nodes:
            del NodeEnvironment.nodes[old_path]
        NodeEnvironment.nodes[str(self._path)] = self
        return True

    def path(self) ->str:
        """Get the full path of the item in the internal network."""
        return str(self._path)

    def session_id(self) ->str:
        """Get the unique session ID of the item."""
        return self._session_id

    @classmethod
    def bulk_add(cls, items: List[Dict[str, Any]]) ->List['MobileItem']:
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

        def create_item(item_data: Dict[str, Any]) ->'MobileItem':
            new_item = cls(name=item_data['name'], path=item_data['path'],
                position=item_data['position'])
            new_session_ids.add(new_item.session_id())
            return new_item
        with ThreadPoolExecutor() as executor:
            future_to_item = {executor.submit(create_item, item): item for
                item in items}
            for future in as_completed(future_to_item):
                new_items.append(future.result())
        if len(new_session_ids) != len(items
            ) or not new_session_ids.isdisjoint(cls._existing_session_ids):
            raise RuntimeError(
                'Failed to generate unique session IDs for all items')
        cls._existing_session_ids.update(new_session_ids)
        return new_items

    @classmethod
    def _generate_unique_session_id(cls) ->int:
        """
        Generate a unique integer session ID.

        Returns:
            int: A unique session ID.

        Raises:
            RuntimeError: If unable to generate a unique ID after 100 attempts.
        """
        for _ in range(100):
            new_id = cls._generate_session_id()
            if new_id not in cls._existing_session_ids:
                cls._existing_session_ids.add(new_id)
                return new_id
        raise RuntimeError('Unable to generate a unique session ID')

    @staticmethod
    def _generate_session_id() ->int:
        """Generate an integer session ID using UUID."""
        return uuid.uuid4().int & (1 << 63) - 1

    def __repr__(self) ->str:
        """Return a string representation of the MobileItem."""
        return (
            f"MobileItem(name='{self._name}', path='{self._path}', position={self._position})"
            )

    def network_item_type(self) ->NetworkItemType:
        """
        Implement the abstract method from NetworkEntity.

        Returns:
            NetworkItemType: The type of this network item (always NODE for MobileItem).
        """
        return NetworkItemType.NODE

    def __del__(self) ->None:
        """
        Clean up when the object is deleted.

        Removes the session ID from the set of existing IDs.
        """
        self._existing_session_ids.discard(self._session_id)
