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

class NodeConnection:
    def __init__(self, output_node: Node, input_node: Node, output_index: int, input_index: int):
        self._output_node = output_node
        self._input_node = input_node
        self._output_index = output_index
        self._input_index = input_index
        self._selected = False

    def input_name(self) -> str:
        return self._input_node.input_names()[self._input_index]

    def output_name(self) -> str:
        return self._output_node.output_names()[self._output_index]

    def is_selected(self) -> bool:
        return self._selected

    def set_selected(self, selected: bool = True) -> None:
        self._selected = selected
