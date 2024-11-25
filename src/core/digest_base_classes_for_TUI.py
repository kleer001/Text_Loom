from enum import Enum
from typing import Dict, List, Optional, Tuple

def generate_node_types():
    global _node_types
    if _node_types is None:
        node_types = {}
        core_dir = Path(__file__).parent
        for file in core_dir.glob("*_node.py"):
            node_type_name = file.stem.replace("_node", "").upper()
            node_types[node_type_name] = file.stem.replace("_node", "")
        _node_types = node_types
    return _node_types

NodeType = Enum("NodeType", generate_node_types(), type=NodeType)

class NodeEnvironment:
    @classmethod
    def get_instance(cls)

    def __new__(cls)

    def __init__(self)

    def _build_globals(self) -> Dict[str, Any]

    def get_namespace(self)

    def execute(self, code)

    def inspect(self)

    @classmethod
    def list_nodes(cls) -> list[str]

    @classmethod
    def node_exists(cls, node_name: str) -> bool

    @classmethod
    def add_node(cls, node: 'Node')

    @classmethod
    def node_from_name(cls, node_name: str) -> Optional['Node']

    @classmethod
    def remove_node(cls, node_path: str) -> None

class NodeState(Enum):
    COOKING = "cooking"
    UNCHANGED = "unchanged"
    UNCOOKED = "uncooked"
    COOKED = "cooked"

class Node:
    def __init__(self, name: str, path: str, position: List[float], node_type: NodeType):
        self._name = name
        self._path = path
        self._position = position
        self._node_type = node_type
        self._selected = False
        self._color = (1.0, 1.0, 1.0)
        self._state = NodeState.UNCOOKED

    def name(self) -> str:
        return self._name

    def create_node(cls, node_type: NodeType, node_name: Optional[str] = None, parent_path: str = "/") -> "Node":

    def set_name(self, name: str) -> None:
        self._name = name

    def path(self) -> str:
        return self._path

    def position(self) -> Tuple[float, float]:
        return tuple(self._position)

    def set_position(self, position: List[float]) -> None:
        self._position = position

    def color(self) -> Tuple[float, float, float]:
        return self._color

    def set_color(self, color: Tuple[float, float, float]) -> None:
        self._color = color

    def is_selected(self) -> bool:
        return self._selected

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def state(self) -> NodeState:
        return self._state

    def set_state(self, state: NodeState) -> None:
        self._state = state

    def node_type(self) -> NodeType:
        return self._node_type

    def inputs(self) -> Dict[str, 'NodeConnection']:
        return self._inputs

    def outputs(self) -> Dict[str, List['NodeConnection']]:
        return self._outputs

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

