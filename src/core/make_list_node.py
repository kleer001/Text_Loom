from typing import List, Dict
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.text_utils import parse_list

class MakeListNode(Node):
    """
    A node that takes a string list as input, parses the first item, and outputs a new string list.

    This node uses the parse_list function to split the input string into a list of strings.
    It can optionally limit the number of output items based on the 'limit' and 'max_list' parameters.

    Attributes:
        _is_time_dependent (bool): Always False for this node.
    """

    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.MAKE_LIST)
        self._is_time_dependent = False

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "limit": Parm("limit", ParameterType.TOGGLE, self),
            "max_list": Parm("max_list", ParameterType.INT, self),
            "refresh": Parm("refresh", ParameterType.BUTTON, self)
        }

        # Set default values
        self._parms["limit"].set(False)
        self._parms["max_list"].set(5)

        # Set up refresh button callback
        self._parms["refresh"].set_script_callback(self._refresh_callback)

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1

        input_data = self.inputs()[0].output_node().eval() if self.inputs() else []
        
        if not input_data:
            self.add_error("Input data is empty")
            self.set_state(NodeState.UNCOOKED)
            return

        # Process only the first item in the input list
        first_item = input_data[0]
        parsed_list = parse_list(first_item)
        print("::PARSED LIST OF LENGTH ", len(parsed_list))
        
        # Apply limit if enabled
        if self._parms["limit"].eval():
            max_items = self._parms["max_list"].eval()
            parsed_list = parsed_list[:max_items]

        self._output = parsed_list
        self.set_state(NodeState.UNCHANGED)

    def _refresh_callback(self) -> None:
        self.cook(force=True)

    def input_names(self) -> Dict[str, str]:
        return {"input": "Input String List"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Parsed String List"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True
        
        # Check if input has changed
        input_data = self.inputs()[0].output_node().eval() if self.inputs() else []
        return input_data != self._output