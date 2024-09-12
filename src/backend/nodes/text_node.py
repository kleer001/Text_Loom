import hashlib
import time
from typing import List, Dict, Any
from base_classes import Node, NodeType, NodeState
from parm import Parm, ParameterType

class TextNode(Node):
    """
    A node that appends a text string to a list of input strings.

    This node takes a list of strings as input, appends the contents of the text_string
    parameter to the list, and outputs the resulting list of strings.

    Attributes:
        _input_hash (str): Hash of the last processed input.
        _param_hash (str): Hash of the last processed text_string parameter.
    """

    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "text_string": Parm("text_string", ParameterType.STRING, self)
        }

        # Set default value
        self._parms["text_string"].set("")

    def cook(self, force: bool = False) -> None:
        self.cook_dependencies()  # Cook dependencies first
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            input_data = self.inputs()[0].output_node().eval() if self.inputs() else []
            if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
                raise TypeError("Input data must be a list of strings")

            text_string = self._parms["text_string"].eval()

            new_input_hash = self._calculate_hash(str(input_data))
            new_param_hash = self._calculate_hash(text_string)

            if force or new_input_hash != self._input_hash or new_param_hash != self._param_hash:
                result = input_data + [text_string]
                self._output = result
                self._input_hash = new_input_hash
                self._param_hash = new_param_hash
                self.set_state(NodeState.UNCHANGED)
            else:
                print("Input and parameter unchanged, skipping processing")
                self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error processing text: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds


    def input_names(self) -> Dict[str, str]:
        return {"input": "Input Text"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Output Text"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            input_data = self.inputs()[0].eval() if self.inputs() else []
            text_string = self._parms["text_string"].eval()
            new_input_hash = self._calculate_hash(str(input_data))
            new_param_hash = self._calculate_hash(text_string)
            return new_input_hash != self._input_hash or new_param_hash != self._param_hash
        except Exception:
            return True

    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def eval(self) -> List[str]:
        if self.state() != NodeState.UNCHANGED:
            self.cook()
        return self._output