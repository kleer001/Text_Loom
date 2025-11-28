from typing import List, Dict
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.text_utils import parse_list
from core.enums import FunctionalGroup

class MakeListNode(Node):
    """
    A node that takes a string list as input, parses the first item, and outputs a new string list.

    This node uses the parse_list function to split the input string into a list of strings.
    It can optionally limit the number of output items based on the 'limit' and 'max_list' parameters.

    Attributes:
        _is_time_dependent (bool): Always False for this node.

    parse_list: 

    Parse numbered lists from text into a list of strings, supporting both numeric and word-based numbering.

    This function intelligently extracts numbered lists from text while handling various numbering formats
    and multi-line items. It's particularly useful for processing structured text content like meeting notes,
    instructions, or any text containing numbered lists.

    Capabilities:
        - Supports multiple numbering formats:
            * Arabic numerals (1., 2., 3.)
            * Written numbers (one., two., three.)
            * Ordinal numbers (first., second., third.)
            * Compound numbers (twenty-one, ninety-nine)
        - Handles various separators between numbers and text (. : - _ ))
        - Preserves multi-line list items
        - Maintains original text formatting within list items
        - Case-insensitive number word recognition

    Limitations:
        - Only processes the first numbered list encountered in the text
        - Does not count, as such. Any number type (see numbering format) will trigger a split. 
        - Cannot handle nested lists
        - Maximum number support up to thousands
        - Does not preserve the original numbering format
        - Cannot process Roman numerals (i., ii., iii.)
        - Does not handle lettered lists (a., b., c.)

    Args:
        text (str): Input text containing a numbered list

    Returns:
        Union[str, List[str]]: 
            - If a numbered list is found: List of strings, each representing a list item
            - If no list is found or input is not a string: Original text or empty string

    Examples:
        >>> text = '''
        ... Meeting Agenda:
        ... 1. Review previous minutes
        ...    Additional notes about minutes
        ... 2. Discuss new projects
        ... 3. Plan next meeting'''
        >>> parse_list(text)
        ['Review previous minutes Additional notes about minutes',
        'Discuss new projects',
        'Plan next meeting']

        >>> text = '''
        ... Project Steps:
        ... 1 - First: Initialize repository
        ... 2 - Second: Set up environment

        >>> parse_list(text)
        ['-',
        ':',
        'Initialize repository',
        '-',
        ':',
        'Set up environment']

    Notes:
        - List items are assumed to start with a number or number word followed by a separator
        - Subsequent lines without numbers are considered continuation of the previous item
        - The function preserves internal spacing but trims leading/trailing whitespace
        - Non-string inputs return an empty string rather than raising an error
    """

    GLYPH = '≣'
    GROUP = FunctionalGroup.TEXT
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.MAKE_LIST)
        self._is_time_dependent = False

        # Initialize parameters
        self._parms.update({
            "limit": Parm("limit", ParameterType.TOGGLE, self),
            "max_list": Parm("max_list", ParameterType.INT, self),
            "refresh": Parm("refresh", ParameterType.BUTTON, self)
        })

        # Set default values
        self._parms["limit"].set(False)
        self._parms["max_list"].set(5)

        # Set up refresh button callback
        self._parms["refresh"].set_script_callback(self._refresh_callback)

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1

        input_data = self.inputs()[0].output_node().eval(requesting_node=self) if self.inputs() else []
        
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

    def input_names(self) -> Dict[int, str]:
        return {0: "Input String List"}

    def output_names(self) -> Dict[int, str]:
        return {0: "Parsed String List"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True
        
        # Check if input has changed
        input_data = self.inputs()[0].output_node().eval() if self.inputs() else []
        return input_data != self._output