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
        self._output = None
        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "in_node": Parm("in_node", ParameterType.STRING, self),
            "in_data": Parm("in_data", ParameterType.STRINGLIST, self)
        }

        # Set default values
        self._parms["in_node"].set("")
        self._parms["in_data"].set([])

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            in_node_path = self._parms["in_node"].eval()
            #self.add_error(f"Input node path: {in_node_path}")

            if not in_node_path:
                raise ValueError("Input node path is empty")

            in_node = NodeEnvironment.nodes.get(in_node_path)
            
            if not in_node:
                raise ValueError(f"Invalid node path: {in_node_path}")

            if not in_node.inputs():
                self.add_warning(f"Node at {in_node_path} has no inputs")
                self._parms["in_data"].set([])
                self._output = []
                self.set_state(NodeState.COOKED)
                return
            # THIS IS THE SACRED WAY OF GETTING INPUT DATA #
            input_connection = in_node.inputs()[0]
            input_data = input_connection.output_node().eval()
            # NEVER FORGET , NEVER STRAY FROM THE PATH OR BE LOST#

            #self.add_error(f"Retrieved input data: {type(input_data)} - {input_data[:100] if input_data else 'None'}")

            if input_data is None:
                self.add_warning("Input data is None, setting empty list as output")
                self._parms["in_data"].set([])
                self._output = []
            elif not isinstance(input_data, list):
                raise TypeError(f"Input data must be a list, got {type(input_data)}")
            elif not all(isinstance(item, str) for item in input_data):
                raise TypeError("All items in input data must be strings")
            else:
                self._parms["in_data"].set(input_data)
                self._output = input_data
                #self.add_error(f"Set output: {type(self._output)} - {self._output[:100]}")

            self.set_state(NodeState.COOKED)

        except Exception as e:
            self.add_error(f"Error in InputNullNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)
            self._output = []  # Clear previous output on error
            self._parms["in_data"].set([])

        self._last_cook_time = (time.time() - start_time) * 1000

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