from typing import Any, Dict, List, Optional, Tuple
from base_classes import Node, NodeType, NodeState

class NullNode(Node):
    """
    Represents a Null Node in the workspace.
    
    The Null Node is a simple pass-through node that doesn't modify its input.
    It has a single input and can connect its output to multiple other nodes.
    """

    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, position=[0, 0], node_type=NodeType.NULL):
        """
        Initialize a new NullNode.

        Args:
            name (str): The name of the node.
            path (str): The path of the node in the workspace hierarchy.
            position (Tuple[float, float]): The initial position of the node (x, y).
            node_type (NodeType): The type of the node (should be NodeType.NULL).
        """
        super().__init__(name, path, position, node_type)
        self._input_value: Optional[List[str]] = None

    def cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        try:
            if self.inputs():
                input_data = self.inputs()[0].eval()
                if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
                    raise TypeError("Input data must be a list of strings")
                self._input_value = input_data
            else:
                self._input_value = []
            self.set_state(NodeState.UNCHANGED)
        except Exception as e:
            self.add_error(f"Error in NullNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

    def eval(self) -> Optional[List[str]]:
        """
        Get the output value of the Null Node.

        Returns:
            Optional[List[str]]: The unmodified input value.
        """
        return self._input_value

