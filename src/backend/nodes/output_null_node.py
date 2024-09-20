import hashlib
import time
from typing import List, Dict, Any
from base_classes import Node, NodeType, NodeState
from parm import Parm, ParameterType

class OutputNullNode(Node):
    """
    A node that mirrors its input to an output parameter.

    This node is typically used inside a Looper Node, but can function independently.
    It takes a list of strings as input and mirrors it to the out_data parameter.

    Attributes:
        _input_hash (str): Hash of the last processed input.
        _last_input_size (int): Size of the last processed input.

    Parameter: 
        out_date (STRINGLIST) : duplication of this node's input
    """

    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._last_input_size = 0

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "out_data": Parm("out_data", ParameterType.STRINGLIST, self)
        }

        # Set default value
        self._parms["out_data"].set([])
        
    def cook(self, force: bool = False) -> None:
        self.add_error(f"Starting cook for {self.name}")
        self.cook_dependencies()
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            input_data = self.inputs()[0].output_node().eval() if self.inputs() else None
            self.add_error(f"Input data: {type(input_data)} - {input_data[:100] if input_data else 'None'}")

            if input_data is None:
                self.add_warning("Input data is None, setting empty list as output")
                self._parms["out_data"].set([])
                self._output = []
            elif not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
                raise TypeError("Input data must be a list of strings")
            else:
                self._parms["out_data"].set(input_data)
                self._output = input_data
                #self.add_error(f"Set output: {type(self._output)} - {self._output[:100]}")

            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error in NullNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            current_input = self.inputs()[0].output_node().eval() if self.inputs() else []
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
        return {"input": "Input Data"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Output Data"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}