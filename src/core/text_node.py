import hashlib
import time
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.loop_manager import LoopManager

class TextNode(Node):
    """
    A node that manipulates text strings with advanced list support.

    Takes a list of strings as input and either appends or prepends text based on the node's parameters.
    The text_string parameter supports both plain strings and Python-style list syntax:

    Plain string: "hello" -> creates ["hello"]
    List syntax: ["first", "second"] -> creates ["first", "second"]

    List Syntax Details:
    - Uses Python-style list notation with square brackets
    - Strings must be quoted with either single (') or double (") quotes
    - Mixed quote types are supported: ["first", 'second']
    - Supports escaped quotes: ["escaped\\"quote"]
    - Empty strings are preserved: ["", "test", ""]
    - Empty list [] creates [""]
    - Invalid syntax falls back to treating input as plain string

    Parameters:
    text_string: The text to process. Accepts plain string or list syntax
    pass_through: When True, processes input data. When False, uses only text_string
    per_item: When True, applies each text string to every input item
            When False, concatenates lists of strings
    prefix: When True, adds text before input. When False, adds after

    Input: List[str]
    Output: List[str]
    """

    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None

        self._parms: Dict[str, Parm] = {
            "text_string": Parm("text_string", ParameterType.STRING, self),
            "pass_through": Parm("pass_through", ParameterType.TOGGLE, self),
            "per_item": Parm("per_item", ParameterType.TOGGLE, self),
            "prefix": Parm("prefix", ParameterType.TOGGLE, self),
        }

        self._parms["text_string"].set("")
        self._parms["pass_through"].set(True)
        self._parms["per_item"].set(True)
        self._parms["prefix"].set(False)

    def _parse_string_list(self, s: str) -> list[str]:

        """
        Parses a text string as either a plain string or a Python-style list of strings.
        
        Supports:
        - Python list syntax: ["item1", "item2"]
        - Mixed quotes: ["item1", 'item2']
        - Escaped quotes: ["escaped\"quote"]
        - Empty strings: ["", "test", ""]
        - Empty lists: [] -> [""]
        
        Fallback behavior:
        - Invalid syntax (unclosed quotes, bad escapes) -> treats entire input as plain string
        - Unmatched brackets -> treats entire input as plain string
        - Plain string without brackets -> returns single-item list
        
        Args:
            s: Input string to parse
            
        Returns:
            list[str]: Parsed strings as list. Always returns at least a single item list.
        """  

        if not (s.startswith('[') and s.endswith(']')):
            return [s]
            
        result = []
        s = s[1:-1].strip()
        if not s:
            return ['']
            
        current = []
        in_string = False
        quote_char = None
        escape = False
        
        try:
            for c in s:
                if escape:
                    current.append(c)
                    escape = False
                    continue
                    
                if c == '\\':
                    escape = True
                    continue
                    
                if c in ['"', "'"]:
                    if not in_string:
                        in_string = True
                        quote_char = c
                    elif c == quote_char:
                        in_string = False
                        quote_char = None
                    else:
                        current.append(c)
                elif c == ',' and not in_string:
                    result.append(''.join(current))
                    current = []
                elif c.isspace() and not in_string:
                    continue
                else:
                    current.append(c)
                    
            if escape or in_string:  # Invalid syntax
                return [s]
                
            if current:
                result.append(''.join(current))
                
            return [x for x in result if x or x == '']  # Preserve empty strings
            
        except:
            return [s]

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        self._is_time_dependent = self._parms["text_string"].is_expression()

        pass_through = self._parms["pass_through"].eval()
        per_item = self._parms["per_item"].eval()
        text_string = self._parms["text_string"].eval()
        prefix = self._parms["prefix"].eval()

        input_data = []
        if pass_through and self.inputs():
            input_data = self.inputs()[0].output_node().eval(requesting_node=self)
            if not isinstance(input_data, list):
                input_data = []

        parsed_strings = self._parse_string_list(text_string)
        
        if pass_through and input_data:
            if per_item:
                result = []
                for item in input_data:
                    for parsed in parsed_strings:
                        result.append(f"{parsed}{item}" if prefix else f"{item}{parsed}")
            else:
                result = parsed_strings + input_data if prefix else input_data + parsed_strings
        else:
            result = parsed_strings

        self._output = result
        self._param_hash = self._calculate_hash(text_string + str(per_item))
        self._input_hash = self._calculate_hash(str(input_data)) if pass_through and input_data else None
        self.set_state(NodeState.UNCHANGED)

        self._last_cook_time = (time.time() - start_time) * 1000

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
        if self._is_time_dependent:
            return True
        try:
            pass_through = self._parms["pass_through"].raw_value()
            text_string = self._parms["text_string"].raw_value()
            prefix = self._parms["prefix"].raw_value()
            per_item = self._parms["per_item"].raw_value()
            new_param_hash = self._calculate_hash(text_string + str(prefix) + str(per_item))

            if pass_through:
                input_data = self.inputs()[0].output_node().eval() if self.inputs() else []
                new_input_hash = self._calculate_hash(str(input_data))
                return new_input_hash != self._input_hash or new_param_hash != self._param_hash
            else:
                return new_param_hash != self._param_hash
        except Exception:
            return True
    
    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    