from typing import List, Dict, Any, Optional, Tuple
import hashlib
import time
import re
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType

class SectionNode(Node):
    """
    A node that sections input text based on prefixes, supporting wildcards and custom delimiters.
    
    This node takes a list of strings as input and separates them into three outputs based on
    prefix matching patterns. Each line is matched against two prefix patterns and sorted into
    the corresponding output. Lines that don't match either prefix go to the unmatched output.

    Prefix Patterns:
        - Support exact string matching: "Speaker", "Q", "A"
        - Support wildcards:
            * matches any sequence of characters
            ? matches exactly one character
        - Examples:
            "Q*" matches "Q:", "Query:", "Question:"
            "Speaker?" matches "Speaker1:", "Speaker2:", "SpeakerA:"
            "*Bot" matches "ChatBot:", "TestBot:"
    
    Parameters:
        prefix1 (str): First prefix to match (with optional wildcards)
        prefix2 (str): Second prefix to match (with optional wildcards)
        delimiter (str): Character(s) that separate prefix from content (default: ":")
        trim_prefix (bool): When True, removes prefix and delimiter from matched lines
        enabled (bool): Enables/disables the node's functionality
    
    Inputs:
        input (List[str]): List of strings to process

    Outputs:
        output[0]: Lines matching prefix1
        output[1]: Lines matching prefix2
        output[2]: Unmatched lines
    
    Example Usage:
        # Basic Q&A sectioning
        prefix1 = "Q"
        prefix2 = "A"
        Input: ["Q: What time is it?", "A: 3 PM", "Note: check later"]
        Output[0]: ["What time is it?"]
        Output[1]: ["3 PM"]
        Output[2]: ["Note: check later"]

        # Interview transcript with wildcards
        prefix1 = "Speaker?"  # Matches Speaker1, Speaker2, etc.
        prefix2 = "*viewer"   # Matches Interviewer, Reviewer, etc.
        delimiter = ":"
        Input: ["Speaker1: Hello", "Interviewer: Hi", "Random text"]
        Output[0]: ["Hello"]
        Output[1]: ["Hi"]
        Output[2]: ["Random text"]

    Notes:
        - Whitespace around prefixes and delimiters is normalized
        - Empty outputs contain [""] rather than []
        - Wildcard patterns are converted to simple regex patterns internally
        - If the delimiter appears in the prefix itself, it will be treated as a delimiter
    """

    SINGLE_OUTPUT = False
    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None
        self._output = [[], [], []]

        self._parms: Dict[str, Parm] = {
            "enabled": Parm("enabled", ParameterType.TOGGLE, self),
            "prefix1": Parm("prefix1", ParameterType.STRING, self),
            "prefix2": Parm("prefix2", ParameterType.STRING, self),
            "delimiter": Parm("delimiter", ParameterType.STRING, self),
            "trim_prefix": Parm("trim_prefix", ParameterType.TOGGLE, self),
        }

        self._parms["enabled"].set(True)
        self._parms["prefix1"].set("Interviewer")
        self._parms["prefix2"].set("Participant")
        self._parms["delimiter"].set(":")
        self._parms["trim_prefix"].set(True)

    def _process_sections(self, input_list: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Processes input strings and sections them based on prefix patterns.

        Takes a list of strings and divides them into three groups based on prefix matching.
        Handles wildcard patterns in prefixes (* for any sequence, ? for single character)
        and normalizes whitespace. Lines matching first prefix pattern go to first output,
        lines matching second prefix pattern go to second output, and unmatched lines go
        to third output.

        Args:
            input_list (List[str]): List of strings to section

        Returns:
            Tuple[List[str], List[str], List[str]]: Three lists containing:
                - Lines matching first prefix pattern (trimmed if trim_prefix is True)
                - Lines matching second prefix pattern (trimmed if trim_prefix is True)
                - Unmatched lines

        Example:
            input_list = ["Q1: Hello", "A1: Hi", "Other"]
            prefix1 = "Q?"
            prefix2 = "A?"
            delimiter = ":"
            Returns: (["Hello"], ["Hi"], ["Other"])
        """
        prefix1 = self._parms["prefix1"].eval().strip()
        prefix2 = self._parms["prefix2"].eval().strip()
        delimiter = self._parms["delimiter"].eval()
        trim_prefix = self._parms["trim_prefix"].eval()
        
        # Convert wildcards to regex patterns
        def pattern_to_regex(pattern: str) -> str:
            pattern = re.escape(pattern)  # Escape special regex chars
            pattern = pattern.replace('\\*', '.*').replace('\\?', '.')
            return f'^{pattern}\\{delimiter}'
        
        pattern1 = pattern_to_regex(prefix1)
        pattern2 = pattern_to_regex(prefix2)
        
        matches1 = []
        matches2 = []
        unmatched = []
        
        for line in input_list:
            line = line.strip()
            clean_line = ' '.join(line.split())
            
            if re.match(pattern1, clean_line):
                content = line[line.find(delimiter) + 1:] if trim_prefix else line
                matches1.append(content.strip())
            elif re.match(pattern2, clean_line):
                content = line[line.find(delimiter) + 1:] if trim_prefix else line
                matches2.append(content.strip())
            else:
                unmatched.append(line)
                
        return matches1, matches2, unmatched

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        enabled = self._parms["enabled"].eval()
        
        input_data = []
        if self.inputs():
            input_node = self.inputs()[0].output_node()
            raw_input = input_node.eval(requesting_node=self)
            if isinstance(raw_input, list) and all(isinstance(x, str) for x in raw_input):
                input_data = raw_input
            else:
                self.add_error("Input must be List[str]")

        if enabled and input_data and not self.errors():
            section1, section2, unmatched = self._process_sections(input_data)
            self._output = [section1, section2, unmatched]
            
            # Update connected output nodes for each output index
            for output_idx in [0, 1, 2]:  # For all three section outputs
                if output_idx in self._outputs:
                    for conn in self._outputs[output_idx]:
                        conn.input_node().set_state(NodeState.UNCOOKED)
        else:
            self._output = [[], [], []]

        self._param_hash = self._calculate_hash(
            str(enabled) + 
            self._parms["prefix1"].eval() + 
            self._parms["prefix2"].eval() + 
            self._parms["delimiter"].eval() +
            str(self._parms["trim_prefix"].eval())
        )
        self._input_hash = self._calculate_hash(str(input_data))
        
        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True
                
        try:
            enabled = self._parms["enabled"].eval()
            new_param_hash = self._calculate_hash(
                str(enabled) + 
                self._parms["prefix1"].eval() + 
                self._parms["prefix2"].eval() + 
                str(self._parms["trim_prefix"].eval())
            )

            input_data = []
            if self.inputs():
                input_node = self.inputs()[0].output_node()
                raw_input = input_node.eval(requesting_node=self)
                if isinstance(raw_input, list) and all(isinstance(x, str) for x in raw_input):
                    input_data = raw_input

            new_input_hash = self._calculate_hash(str(input_data))
            return new_input_hash != self._input_hash or new_param_hash != self._param_hash
        except Exception:
            return True

    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def input_names(self) -> Dict[str, str]:
        return {"0": "Input Text"}

    def output_names(self) -> Dict[str, str]:
        return {
            "0": "First Section",
            "1": "Second Section",
            "2": "Unmatched"
        }

    def input_data_types(self) -> Dict[str, str]:
        return {"0": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {
            "0": "List[str]",
            "1": "List[str]",
            "2": "List[str]"
        }