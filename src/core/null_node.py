from typing import Any, Dict, List, Optional, Tuple
from core.base_classes import Node, NodeType, NodeState

class NullNode(Node):
    """
    Represents a Null Node in the workspace.
    
    The Null Node is a simple pass-through node that doesn't modify its input.
    It has a single input and can connect its output to multiple other nodes.
    """

    GLYPH = '∅'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, position=[0, 0], node_type=NodeType.NULL):
        super().__init__(name, path, position, node_type)
        self._input_value: Optional[List[str]] = None

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        try:
            if self.inputs():
                input_connection = self.inputs()[0]
                input_data = input_connection.output_node().eval(requesting_node=self)  
                
                if isinstance(input_data, list) and all(isinstance(item, str) for item in input_data):
                    self._input_value = input_data
                    self._output = input_data  # Add this line to set the output
                else:
                    raise TypeError("Input data must be a list of strings")
            else:
                self._input_value = []
                self._output = []  # Add this line to set empty output
            
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error in NullNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

