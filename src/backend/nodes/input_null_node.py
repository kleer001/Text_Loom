import hashlib
import time
from typing import List, Dict, Any, Optional
from base_classes import Node, NodeType, NodeState, NodeEnvironment
from parm import Parm, ParameterType

class InputNullNode(Node):
    """
    A node that retrieves input from another specified node.

    This node is typically used inside a Looper Node, but can function independently.
    It retrieves the input value of another node specified by the in_node parameter.

    Attributes:
        _input_hash (str): Hash of the last processed input.
        _last_input_size (int): Size of the last processed input.
    Parameters: 
        in_node (STRING) : path to the node
        in_data (STRINGLIST) : data from that node
    """

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._last_input_size = 0

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "in_node": Parm("in_node", ParameterType.STRING, self),
            "in_data": Parm("in_data", ParameterType.STRINGLIST, self)
        }

        # Set default values
        self._parms["in_node"].set("")
        self._parms["in_data"].set([])

    def cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            in_node_path = self._parms["in_node"].eval()
            in_node = NodeEnvironment.nodes.get(in_node_path)

            if not in_node:
                raise ValueError(f"Invalid node path: {in_node_path}")

            if not in_node.inputs():
                raise ValueError(f"Node at {in_node_path} has no inputs")

            input_data = in_node.inputs()[0].output_data()

            if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
                raise TypeError("Input data must be a list of strings")

            self._parms["in_data"].set(input_data)
            self._output = input_data
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error processing input: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            in_node_path = self._parms["in_node"].eval()
            in_node = NodeEnvironment.nodes.get(in_node_path)

            if not in_node or not in_node.inputs():
                return True

            current_input = in_node.inputs()[0].output_node().eval()
            current_size = sum(len(s.encode('utf-8')) for s in current_input)

            if current_size != self._last_input_size:
                return True

            if current_size < 10 * 1024 * 1024:  # 10MB
                return True

            current_hash = self._calculate_hash(str(current_input))
            if current_hash != self._input_hash:
                return True

            return False

        except Exception:
            return True

    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def eval(self) -> List[str]:
        if self.state() != NodeState.UNCHANGED:
            self.cook()
        return self._output

    def input_names(self) -> Dict[str, str]:
        return {}  # This node has no inputs

    def output_names(self) -> Dict[str, str]:
        return {"output": "Output Data"}

    def input_data_types(self) -> Dict[str, str]:
        return {}  # This node has no inputs

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}