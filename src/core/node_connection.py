from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING, Union
import uuid
from .enums import NetworkItemType
from .network_entity import NetworkEntity

class NodeConnection(NetworkEntity):
    """
    Represents a connection between two nodes in the network.

    This class inherits from NetworkEntity and provides information about
    the connection between an output of one node and an input of another node.
    """

    # Class variable to track all connection session IDs
    _existing_session_ids: Set[str] = set()

    def __init__(self, output_node: 'Node', input_node: 'Node',
        output_index: Union[int, str], input_index: Union[int, str]):
        super().__init__()
        self._output_node: 'Node' = output_node
        self._input_node: 'Node' = input_node
        # Store indices as-is (can be int or str depending on node type)
        self._output_index: Union[int, str] = output_index
        self._input_index: Union[int, str] = input_index
        self._selected: bool = False

        # Generate unique session ID for this connection
        self._session_id: str = self._generate_unique_session_id()

    def output_node(self) ->'Node':
        """Returns the node on the output side of this connection."""
        return self._output_node

    def input_node(self) ->'Node':
        """Returns the node on the input side of this connection."""
        return self._input_node

    def output_index(self) -> Union[int, str]:
        """Returns the index of the output connection on the output node."""
        return self._output_index

    def input_index(self) -> Union[int, str]:
        """Returns the index of the input connection on the input node."""
        return self._input_index

    def output_name(self) ->str:
        """Returns the name of the output connection on the output node."""
        return self._output_node.output_names()[self._output_index]

    def input_name(self) ->str:
        """Returns the name of the input connection on the input node."""
        return self._input_node.input_names()[self._input_index]

    def output_data_type(self) ->str:
        """Returns the data type of the output connection on the output node."""
        return self._output_node.output_data_types()[self._output_index]

    def input_data_type(self) ->str:
        """Returns the data type of the input connection on the input node."""
        return self._input_node.input_data_types()[self._input_index]

    def is_selected(self) ->bool:
        """Returns True if the connection is selected, False otherwise."""
        return self._selected

    def set_selected(self, selected: bool=True) ->None:
        """Selects or deselects this connection."""
        self._selected = selected

    def session_id(self) -> str:
        """Returns the unique session ID for this connection."""
        return self._session_id

    @classmethod
    def _generate_unique_session_id(cls) -> str:
        """
        Generate a unique string session ID.

        Returns:
            str: A unique session ID (UUID as string).

        Raises:
            RuntimeError: If unable to generate a unique ID after 100 attempts.
        """
        for attempt in range(100):
            new_id = cls._generate_session_id()
            if new_id not in cls._existing_session_ids:
                cls._existing_session_ids.add(new_id)
                return new_id

        raise RuntimeError('Unable to generate a unique session ID for connection')

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a string session ID using UUID."""
        return str(uuid.uuid4())

    def network_item_type(self) ->NetworkItemType:
        """Implement the abstract method from NetworkEntity."""
        return NetworkItemType.CONNECTION

    def remove_connection(self) ->None:
        output_node = self._output_node
        input_node = self._input_node
        output_idx = self._output_index
        input_idx = self._input_index
        output_name = self.output_name()
        input_name = self.input_name()
        if output_name in output_node.outputs():
            output_connections = output_node.outputs()[output_name]
            if self in output_connections:
                output_connections.remove(self)
        if input_name in input_node.inputs():
            if input_node.inputs()[input_name] == self:
                input_node.inputs()[input_name] = None

        def restore_connection():
            if output_name in output_node.outputs():
                output_node.outputs()[output_name].append(self)
            if input_name in input_node.inputs():
                input_node.inputs()[input_name] = self

    def __del__(self) -> None:
        """Clean up when the connection is deleted."""
        NodeConnection._existing_session_ids.discard(self._session_id)

    def __repr__(self) ->str:
        """Returns a string representation of the NodeConnection."""
        return (
            f'NodeConnection(session_id={self._session_id}, '
            f'output_node={self._output_node.name()}, '
            f'input_node={self._input_node.name()}, '
            f'output_index={self._output_index}, '
            f'input_index={self._input_index})'
            )
