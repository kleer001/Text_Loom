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
        """
        Evaluate and store the input value without modifying it.
        """
        self.set_state(NodeState.COOKING)
        try:
            # Check if there's an input connection
            if self.inputs():
                # Get the NodeConnection object and then evaluate the output node
                input_connection = self.inputs()[0]
                input_data = input_connection.output_node().eval()  # Evaluate the output node of the connection
                
                if isinstance(input_data, list) and all(isinstance(item, str) for item in input_data):
                    self._input_value = input_data  # Valid input data
                else:
                    raise TypeError("Input data must be a list of strings")
            else:
                # No input, set to empty list
                self._input_value = []
            
            # Since it's a pass-through node, no cooking needed, mark as unchanged
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            # Handle errors, reset state to uncooked
            self.add_error(f"Error in NullNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

    def eval(self) -> Optional[List[str]]:
        """
        Get the output value of the Null Node.

        Returns:
            Optional[List[str]]: The unmodified input value.
        """
        return self._input_value

