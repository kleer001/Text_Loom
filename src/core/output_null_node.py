import hashlib
import time
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState, NodeEnvironment
from core.parm import Parm, ParameterType

class OutputNullNode(Node):
    """A node that mirrors its input to an output parameter.

    This node is typically used inside a Looper Node, but can function independently.
    It takes a list of strings as input and mirrors it to the out_data parameter,
    accumulating results across loop iterations.

    Attributes:
        out_data (List[str]): Accumulated output data from all loop iterations.
        feedback_mode (bool): Enables feedback loop behavior.
        cook_loops (bool): When True, forces cooking of input on each loop iteration.
        in_node (str): Path to the parent looper node.

    Example:
        >>> output_null = Node.create_node(NodeType.OUTPUT_NULL)
        >>> # Typically created automatically inside a Looper Node
        >>> # Input: ['result1', 'result2']
        >>> # After first iteration: out_data = ['result1', 'result2']
        >>> # After second iteration: out_data = ['result1', 'result2', 'result3', 'result4']

    Note:
        Unlike other nodes, OutputNullNode accumulates data by extending the
        out_data list with each cook operation. This allows looper constructs
        to collect results from multiple iterations. The node is time-dependent
        and will always recook when requested.
    """

    GLYPH = '◁'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = True
        self._input_hash = None
        self._last_input_size = 0
        self._parent_looper = True

        self._parms.update({
            "out_data": Parm("out_data", ParameterType.STRINGLIST, self),
            "feedback_mode": Parm("feedback_mode", ParameterType.TOGGLE, self),
            "cook_loops": Parm("cook_loops", ParameterType.TOGGLE, self),
            "in_node": Parm("in_node", ParameterType.STRING, self),
        })

        self._parms["out_data"].set([])
        self._parms["feedback_mode"].set(False)
        self._parms["cook_loops"].set(False)
        self._parms["in_node"].set("")
        
    def _internal_cook(self) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            input_node = self.inputs()[0].output_node() if self.inputs() else None
            
            parent_path = self._parms["in_node"].eval()
            parent_node = NodeEnvironment.nodes.get(parent_path)
            cook_loops = parent_node._parms["cook_loops"].eval() if parent_node else False
            
            if input_node:
                if cook_loops:
                    input_data = input_node.eval(requesting_node=self)
                else:
                    input_data = input_node.get_output(requesting_node=self)
            else:
                input_data = None
                
            #print(f"Input data for outputnull:", input_data)

            if input_data is None:
                self.add_warning("Input data is None, setting empty list as output")
                self._parms["out_data"].set([])
                self._output = []
            elif not isinstance(input_data, list):
                raise TypeError("Input data must be a list")
            else:
                current_data = self._parms["out_data"].raw_value()
                if not isinstance(current_data, list):
                    current_data = []

                if all(isinstance(x, str) for x in input_data):
                    current_data.extend(input_data)
                else:
                    self.add_warning(f"Received non-string data: {input_data}")
                    current_data.extend(str(x) for x in input_data if x)

                self._parms["out_data"].set(current_data)
                self._output = current_data

            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error in OutputNullNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000


    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def input_names(self) -> Dict[int, str]:
        return {0: "Input Data"}

    def output_names(self) -> Dict[int, str]:
        return {0: "Output Data"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}