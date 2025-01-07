from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from .enums import NetworkItemType

class NetworkEntity(ABC):
    """
    Abstract base class for network entities in the procedural text generation application.

    This class serves as the foundation for all network-related objects, providing
    a common interface and shared functionality.

    Attributes:
        _instance_count (ClassVar[int]): Class variable to keep track of instances.

    """
    _instance_count: ClassVar[int] = 0

    def __init__(self) ->None:
        """
        Initialize a new NetworkEntity instance.

        Increments the instance count upon creation.
        """
        self.__class__._instance_count += 1

    @abstractmethod
    def network_item_type(self) ->NetworkItemType:
        """
        Return the type of network entity.

        Returns:
            NetworkItemType: An enum value representing the type of network entity.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError(
            'Subclasses must implement network_item_type method')

    @classmethod
    def get_instance_count(cls) ->int:
        """
        Get the total number of instances created for this class.

        Returns:
            int: The number of instances.
        """
        return cls._instance_count

    def __repr__(self) ->str:
        """
        Return a string representation of the NetworkEntity.

        Returns:
            str: A string representation of the object.
        """
        return (
            f'{self.__class__.__name__}(type={self.network_item_type().name})')

    def __str__(self) ->str:
        """
        Return a human-readable string representation of the NetworkEntity.

        Returns:
            str: A string description of the object.
        """
        return (
            f'{self.__class__.__name__} of type {self.network_item_type().name}'
            )
