import hashlib
import time
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType

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
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = True
        self._input_hash = None
        self._last_input_size = 0
        self._parent_looper = True

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "out_data": Parm("out_data", ParameterType.STRINGLIST, self),
            "feedback_mode": Parm("feedback_mode", ParameterType.TOGGLE, self),
        }

        # Set default value
        self._parms["out_data"].set([])
        self._parms["feedback_mode"].set(False)
        
    def _internal_cook(self) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            # Don't eval() again - just get the output directly since dependencies are already cooked
            input_node = self.inputs()[0].output_node() if self.inputs() else None
            input_data = input_node.get_output() if input_node else None
            print(f"Input data for outputnull:", input_data)

            if input_data is None:
                self.add_warning("Input data is None, setting empty list as output")
                self._parms["out_data"].set([])
                self._output = []
            elif not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
                raise TypeError("Input data must be a list of strings")
            else:
                current_data = self._parms["out_data"].raw_value()
                if isinstance(current_data, list):
                    if self._parms["feedback_mode"].eval():
                        new_data = input_data
                    else:
                        current_data.append(input_data)
                        new_data = current_data
                else:
                    new_data = [input_data]
                
                self._parms["out_data"].set(new_data)
                self._output = input_data
                print("from-", self.name(), " set output:", self._output)

            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000


    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def eval(self, force: bool = True ) -> List[str]:
        # always cook because we always want output for each iteration
        return self._output

    def input_names(self) -> Dict[str, str]:
        return {"input": "Input Data"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Output Data"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}