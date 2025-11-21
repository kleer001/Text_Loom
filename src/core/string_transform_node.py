import hashlib
import time
import re
from typing import List, Dict
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType


class StringTransformNode(Node):
    """A node that performs various string transformations on text.

    This node applies text transformations including find/replace, regex operations,
    case transformations, and whitespace normalization to each item in the input list.

    Attributes:
        operation (str): The transformation operation to perform.
            Options: "find_replace", "regex_replace", "case_transform",
                     "whitespace_normalize", "trim"
        find_text (str): Text to find (for find_replace and regex_replace operations)
        replace_text (str): Text to replace with
        use_regex (bool): Whether to use regex for find/replace
        case_sensitive (bool): Whether find/replace is case-sensitive
        case_mode (str): Case transformation mode.
            Options: "upper", "lower", "title", "capitalize"
        trim_mode (str): Whitespace trimming mode.
            Options: "both", "start", "end", "none"
        normalize_spaces (bool): If True, collapses multiple spaces to single space
        enabled (bool): If True, performs transformation; otherwise passes through

    Input:
        List[str]: A list of strings to transform

    Output:
        List[str]: A list of transformed strings

    Example:
        >>> node = StringTransformNode("transform", "/root", NodeType.STRING_TRANSFORM)
        >>> node.parms()["operation"].set("case_transform")
        >>> node.parms()["case_mode"].set("upper")
        >>> # Input: ["hello", "world"] -> Output: ["HELLO", "WORLD"]
    """

    GLYPH = '⎔'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None

        self._parms.update({
            "operation": Parm("operation", ParameterType.MENU, self),
            "find_text": Parm("find_text", ParameterType.STRING, self),
            "replace_text": Parm("replace_text", ParameterType.STRING, self),
            "use_regex": Parm("use_regex", ParameterType.TOGGLE, self),
            "case_sensitive": Parm("case_sensitive", ParameterType.TOGGLE, self),
            "case_mode": Parm("case_mode", ParameterType.MENU, self),
            "trim_mode": Parm("trim_mode", ParameterType.MENU, self),
            "normalize_spaces": Parm("normalize_spaces", ParameterType.TOGGLE, self),
            "enabled": Parm("enabled", ParameterType.TOGGLE, self),
        })

        # Set defaults
        self._parms["operation"].set("find_replace")
        self._parms["find_text"].set("")
        self._parms["replace_text"].set("")
        self._parms["use_regex"].set(False)
        self._parms["case_sensitive"].set(True)
        self._parms["case_mode"].set("upper")
        self._parms["trim_mode"].set("both")
        self._parms["normalize_spaces"].set(False)
        self._parms["enabled"].set(True)

    def _apply_find_replace(self, text: str, find: str, replace: str,
                           use_regex: bool, case_sensitive: bool) -> str:
        """Apply find/replace operation to text."""
        if not find:
            return text

        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                return re.sub(find, replace, text, flags=flags)
            except re.error as e:
                self.add_warning(f"Regex error: {str(e)}")
                return text
        else:
            if case_sensitive:
                return text.replace(find, replace)
            else:
                # Case-insensitive replace
                pattern = re.escape(find)
                return re.sub(pattern, replace, text, flags=re.IGNORECASE)

    def _apply_case_transform(self, text: str, mode: str) -> str:
        """Apply case transformation to text."""
        if mode == "upper":
            return text.upper()
        elif mode == "lower":
            return text.lower()
        elif mode == "title":
            return text.title()
        elif mode == "capitalize":
            return text.capitalize()
        return text

    def _apply_trim(self, text: str, mode: str) -> str:
        """Apply whitespace trimming to text."""
        if mode == "both":
            return text.strip()
        elif mode == "start":
            return text.lstrip()
        elif mode == "end":
            return text.rstrip()
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Collapse multiple spaces to single space."""
        return re.sub(r'\s+', ' ', text)

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        # Get parameters
        enabled = self._parms["enabled"].eval()
        operation = self._parms["operation"].eval()
        find_text = self._parms["find_text"].eval()
        replace_text = self._parms["replace_text"].eval()
        use_regex = self._parms["use_regex"].eval()
        case_sensitive = self._parms["case_sensitive"].eval()
        case_mode = self._parms["case_mode"].eval()
        trim_mode = self._parms["trim_mode"].eval()
        normalize_spaces = self._parms["normalize_spaces"].eval()

        # Get input data
        input_data = []
        if self.inputs():
            raw_input = self.inputs()[0].output_node().eval(requesting_node=self)
            if isinstance(raw_input, list):
                input_data = [str(item) for item in raw_input]

        if not enabled or not input_data:
            self._output = input_data
        else:
            result = []
            for item in input_data:
                transformed = item

                # Apply the selected operation
                if operation == "find_replace" or operation == "regex_replace":
                    transformed = self._apply_find_replace(
                        transformed, find_text, replace_text, use_regex, case_sensitive
                    )
                elif operation == "case_transform":
                    transformed = self._apply_case_transform(transformed, case_mode)
                elif operation == "trim":
                    transformed = self._apply_trim(transformed, trim_mode)
                elif operation == "whitespace_normalize":
                    transformed = self._normalize_whitespace(transformed)

                # Apply normalize_spaces if enabled (can be combined with other operations)
                if normalize_spaces and operation != "whitespace_normalize":
                    transformed = self._normalize_whitespace(transformed)

                result.append(transformed)

            self._output = result

        # Update hashes for caching
        param_str = f"{enabled}{operation}{find_text}{replace_text}{use_regex}{case_sensitive}{case_mode}{trim_mode}{normalize_spaces}"
        self._param_hash = self._calculate_hash(param_str)
        self._input_hash = self._calculate_hash(str(input_data))

        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        """Check if node needs to recook based on parameter or input changes."""
        if super().needs_to_cook():
            return True

        try:
            # Build parameter hash
            enabled = self._parms["enabled"].raw_value()
            operation = self._parms["operation"].raw_value()
            find_text = self._parms["find_text"].raw_value()
            replace_text = self._parms["replace_text"].raw_value()
            use_regex = self._parms["use_regex"].raw_value()
            case_sensitive = self._parms["case_sensitive"].raw_value()
            case_mode = self._parms["case_mode"].raw_value()
            trim_mode = self._parms["trim_mode"].raw_value()
            normalize_spaces = self._parms["normalize_spaces"].raw_value()

            param_str = f"{enabled}{operation}{find_text}{replace_text}{use_regex}{case_sensitive}{case_mode}{trim_mode}{normalize_spaces}"
            new_param_hash = self._calculate_hash(param_str)

            # Check input hash
            input_data = []
            if self.inputs():
                input_data = self.inputs()[0].output_node().get_output()
            new_input_hash = self._calculate_hash(str(input_data))

            return new_input_hash != self._input_hash or new_param_hash != self._param_hash
        except Exception:
            return True

    def _calculate_hash(self, content: str) -> str:
        """Calculate MD5 hash of content."""
        return hashlib.md5(content.encode()).hexdigest()

    def input_names(self) -> Dict[int, str]:
        return {0: "Input Text"}

    def output_names(self) -> Dict[int, str]:
        return {0: "Transformed Text"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}
