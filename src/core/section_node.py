from typing import List, Dict, Any, Optional, Tuple
import hashlib
import time
import re
import os
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
import json

class SectionNode(Node):
    r"""
    A node that sections input text based on prefix matching patterns.

    Separates input text into three outputs based on two prefix patterns.
    Lines matching either prefix are routed to corresponding outputs,
    with unmatched lines sent to the third output.

    Prefix Pattern Types:
        1. Wildcard Patterns:
            * Matches any sequence of characters
            ? Matches exactly one character
            Examples:
            - "Q*" matches "Q:", "Query", "Question"
            - "Speaker?" matches "Speaker1", "Speaker2"
            - "*Bot" matches "ChatBot", "TestBot"

        2. Regex Patterns (starting with ^):
            Supports full regex matching
            Example: "^Chapter\d+" matches "Chapter1", "Chapter22"

        3. Shortcut Patterns (starting with @):
            Predefined regex patterns from a configuration file
            Example: "@scene" might match scene headings

    Parameters:
        prefix1 (str): First prefix to match
        prefix2 (str): Second prefix to match
        delimiter (str): Separates prefix from content (default: ":")
        trim_prefix (bool): Removes prefix when True
        enabled (bool): Enables/disables node functionality

    Inputs:
        input (List[str]): Strings to process

    Outputs:
        output[0]: Lines matching first prefix
        output[1]: Lines matching second prefix
        output[2]: Unmatched lines

    Example Usage (Simple):
        Input: ["Q: What time?", "A: 3 PM", "Note: check later"]
        prefix1 = "Q*"
        prefix2 = "A*"
        Output[0]: ["What time?"]
        Output[1]: ["3 PM"]
        Output[2]: ["Note: check later"]

    Example Usage (Complex):
        Input: [
            "INT. COFFEE SHOP - DAY",
            "DETECTIVE SMITH: Hello",
            "Q: First question",
            "(looking around)",
            "A: Detailed answer"
        ]
        prefix1 = "@scene"
        prefix2 = "Q*"
        Output[0]: ["COFFEE SHOP - DAY"]
        Output[1]: ["First question"]
        Output[2]: ["DETECTIVE SMITH: Hello", "(looking around)", "A: Detailed answer"]

    Notes:
        - Whitespace around prefixes and delimiters is normalized
        - Empty outputs contain [""] rather than []
        - Wildcard patterns are converted to regex internally
        - Delimiter within prefix is treated as part of the prefix
    """

    GLYPH = '§'
    SINGLE_OUTPUT = False
    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None
        self._output = [[], [], []]

        self._parms.update({
            "prefix1": Parm("prefix1", ParameterType.STRING, self),
            "prefix2": Parm("prefix2", ParameterType.STRING, self),
            "trim_prefix": Parm("trim_prefix", ParameterType.TOGGLE, self),
            "regex_file": Parm("regex_file", ParameterType.STRING, self),
        })

        self._parms["prefix1"].set("Interviewer")
        self._parms["prefix2"].set("Participant")
        self._parms["trim_prefix"].set(True)
        self._parms["regex_file"].set("regex.dat.json")

    def _process_sections(self, input_list: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Processes input list using two prefix patterns.

        Applies first and second prefix patterns to input list,
        handling cases of invalid or missing prefixes.

        Returns:
        - Matches for first prefix
        - Matches for second prefix
        - Unmatched lines
        """

        prefix1 = self._parms["prefix1"].eval().strip()
        prefix2 = self._parms["prefix2"].eval().strip()

        matches1, non_matches1 = self._process_pattern(input_list, prefix1)
        matches2, non_matches2 = self._process_pattern(input_list, prefix2)

        # If first prefix is invalid (returns full non-matches)
        if not matches1 and len(non_matches1) == len(input_list):
            matches1 = [""]
            non_matches1 = input_list

        # If second prefix is invalid (returns full non-matches)
        if not matches2 and len(non_matches2) == len(input_list):
            matches2 = [""]
            non_matches2 = input_list

        # Convert non_matches to sets for faster lookup (stripped versions)
        non_matches1_set = set(non_matches1)
        non_matches2_set = set(non_matches2)

        # Determine unmatched lines - strip input lines for comparison
        unmatched = [line.strip() for line in input_list if line.strip() in non_matches1_set and line.strip() in non_matches2_set]

        # If unmatched is empty, use non_matches from the first non-invalid pattern
        if not unmatched:
            unmatched = non_matches1 if len(non_matches1) < len(input_list) else non_matches2

        matches1 = matches1 if matches1 else [""]
        matches2 = matches2 if matches2 else [""]

        return matches1, matches2, unmatched


    def _process_pattern(self, input_list: List[str], prefix: str) -> Tuple[List[str], List[str]]:
        """
        Routes input list processing to appropriate pattern matching method.

        Detects pattern type by prefix:
        - Regex patterns (starts with ^)
        - Shortcut patterns (starts with @)
        - Wildcard patterns (default)

        Returns:
        - Matching lines
        - Non-matching lines
        """
        if prefix.startswith('^'):
            return self._regex_pattern(input_list, prefix)
        elif prefix.startswith('@'):
            return self._shortcut_pattern(input_list, prefix)
        else:
            return self._wildcard_pattern(input_list, prefix)



    def _wildcard_pattern(self, input_list: List[str], prefix: str) -> Tuple[List[str], List[str]]:
        """
        Matches lines using wildcard (*,?) pattern with optional delimiter.

        Converts wildcard to regex pattern.
        Supports optional prefix trimming.

        Returns:
        - Lines matching wildcard pattern
        - Lines not matching pattern
        """
        trim_prefix = self._parms["trim_prefix"].eval()

        def pattern_to_regex(pattern: str) -> str:
            # Escape regex special chars, then convert wildcards
            pattern = re.escape(pattern)
            pattern = pattern.replace(r'\*', '.*').replace(r'\?', '.')
            # Match the pattern followed by optional whitespace
            return rf'^{pattern}\s*'

        pattern = pattern_to_regex(prefix)
        matches = []
        non_matches = []

        for line in input_list:
            line = line.strip()
            # Normalize whitespace
            clean_line = ' '.join(line.split())

            match = re.match(pattern, clean_line)
            if match:
                content = clean_line[len(match.group(0)):] if trim_prefix else line
                matches.append(content.strip())
            else:
                non_matches.append(line)

        return matches, non_matches

    def _regex_pattern(self, input_list: List[str], prefix: str) -> Tuple[List[str], List[str]]:
        """
        Matches lines using full regex pattern.

        Uses regex pattern directly after removing ^ prefix.
        Supports optional prefix trimming.

        Returns:
        - Lines matching regex pattern
        - Lines not matching pattern
        """
        trim_prefix = self._parms["trim_prefix"].eval()
        pattern = prefix[1:]  # Remove the ^ trigger

        matches = []
        non_matches = []

        for line in input_list:
            line = line.strip()
            clean_line = ' '.join(line.split())

            match = re.match(pattern, clean_line)
            if match:
                content = clean_line[len(match.group(0)):] if trim_prefix else line
                matches.append(content.strip())
            else:
                non_matches.append(line)

        return matches, non_matches

    def _shortcut_pattern(self, input_list: List[str], prefix: str) -> Tuple[List[str], List[str]]:
        """
        Matches lines using predefined regex patterns from configuration.

        Loads patterns from regex configuration file.
        Handles missing or undefined shortcut patterns.

        Returns:
        - Lines matching shortcut pattern
        - Lines not matching pattern
        """
        trim_prefix = self._parms["trim_prefix"].eval()
        regex_file = self._parms["regex_file"].eval()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        regex_file_path = os.path.join(current_dir, regex_file)

        try:
            with open(regex_file_path, 'r') as f:
                regex_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.add_error(f"Failed to load regex file {regex_file_path}: {str(e)}")
            return [""], input_list

        if not prefix.startswith('@'):
            return [], input_list

        if prefix not in regex_data:
            print(f"Warning: Shortcut {prefix} not found in regex file")
            self.add_warning(f"Shortcut {prefix} not found in regex file")
            return [""], input_list

        pattern = regex_data[prefix]["pattern"]
        pattern = pattern.encode().decode('unicode-escape')

        matches = []
        non_matches = []

        for line in input_list:
            line = line.strip()
            match = re.match(pattern, line)
            if match:
                content = line[match.end():] if trim_prefix and prefix.startswith('@scene') else line
                matches.append(content.strip())
            else:
                non_matches.append(line)

        if not matches:
            matches = [""]

        return matches, non_matches

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()
        self._output = [[], [], []]  # Clear outputs at start

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

            for output_idx in [0, 1, 2]:
                if output_idx in self._outputs:
                    for conn in self._outputs[output_idx]:
                        conn.input_node().set_state(NodeState.UNCOOKED)

        self._param_hash = self._calculate_hash(
            str(enabled) +
            self._parms["prefix1"].eval() +
            self._parms["prefix2"].eval() +
            str(self._parms["trim_prefix"].eval()) +
            self._parms["regex_file"].eval()
        )
        self._input_hash = self._calculate_hash(str(input_data))

        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        enabled = self._parms["enabled"].eval()
        new_param_hash = self._calculate_hash(
            str(enabled) +
            self._parms["prefix1"].eval() +
            self._parms["prefix2"].eval() +
            str(self._parms["trim_prefix"].eval()) +
            self._parms["regex_file"].eval()
        )

        input_data = []
        if self.inputs():
            input_node = self.inputs()[0].output_node()
            raw_input = input_node.eval(requesting_node=self)
            if isinstance(raw_input, list) and all(isinstance(x, str) for x in raw_input):
                input_data = raw_input

        new_input_hash = self._calculate_hash(str(input_data))

        if new_input_hash != self._input_hash:
            return True

        if new_param_hash != self._param_hash:
            return True
            
        return False

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