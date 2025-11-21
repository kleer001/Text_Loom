import hashlib
import time
import json
from typing import List, Dict
from collections import Counter
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType


class CountNode(Node):
    """A node that performs counting and statistical operations on text lists.

    This node can count items, deduplicate lists, find unique counts, and provide
    word/character frequency analysis. Output can be formatted as plain numbers,
    labeled text, or JSON.

    Attributes:
        stat_mode (str): The statistical operation to perform.
            Options: "count", "deduplicate", "word_freq", "char_freq"
        count_what (str): What to count for "count" mode.
            Options: "items", "words", "characters", "lines"
        preserve_order (bool): For deduplication, whether to preserve original order
        top_n (int): For frequency modes, return only top N most frequent (0 = all)
        case_sensitive (bool): Whether to treat text as case-sensitive
        format_output (str): How to format the output.
            Options: "plain", "labeled", "json"
        enabled (bool): If True, performs operation; otherwise passes through

    Input:
        List[str]: A list of strings to analyze

    Output:
        List[str]: Results formatted according to format_output parameter

    Example:
        >>> node = CountNode("counter", "/root", NodeType.COUNT)
        >>> node.parms()["stat_mode"].set("count")
        >>> node.parms()["count_what"].set("items")
        >>> # Input: ["a", "b", "c"] -> Output: ["3"]
    """

    GLYPH = '#'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None

        self._parms.update({
            "stat_mode": Parm("stat_mode", ParameterType.MENU, self),
            "count_what": Parm("count_what", ParameterType.MENU, self),
            "preserve_order": Parm("preserve_order", ParameterType.TOGGLE, self),
            "top_n": Parm("top_n", ParameterType.INT, self),
            "case_sensitive": Parm("case_sensitive", ParameterType.TOGGLE, self),
            "format_output": Parm("format_output", ParameterType.MENU, self),
            "enabled": Parm("enabled", ParameterType.TOGGLE, self),
        })

        # Set defaults
        self._parms["stat_mode"].set("count")
        self._parms["count_what"].set("items")
        self._parms["preserve_order"].set(True)
        self._parms["top_n"].set(0)
        self._parms["case_sensitive"].set(False)
        self._parms["format_output"].set("plain")
        self._parms["enabled"].set(True)

    def _count_items(self, data: List[str]) -> int:
        """Count the number of items in the list."""
        return len(data)

    def _count_words(self, data: List[str]) -> int:
        """Count total words across all items."""
        total = 0
        for item in data:
            total += len(item.split())
        return total

    def _count_characters(self, data: List[str]) -> int:
        """Count total characters across all items."""
        return sum(len(item) for item in data)

    def _count_lines(self, data: List[str]) -> int:
        """Count total lines across all items."""
        total = 0
        for item in data:
            total += item.count('\n') + 1
        return total

    def _deduplicate(self, data: List[str], preserve_order: bool,
                     case_sensitive: bool) -> List[str]:
        """Remove duplicate items from the list."""
        if not case_sensitive:
            # Track original case versions
            seen = {}
            result = []
            for item in data:
                key = item.lower()
                if key not in seen:
                    seen[key] = item
                    if preserve_order:
                        result.append(item)
            if preserve_order:
                return result
            else:
                return sorted(seen.values())
        else:
            if preserve_order:
                seen = set()
                result = []
                for item in data:
                    if item not in seen:
                        seen.add(item)
                        result.append(item)
                return result
            else:
                return sorted(list(set(data)))

    def _word_frequency(self, data: List[str], top_n: int,
                       case_sensitive: bool) -> Dict[str, int]:
        """Calculate word frequency across all items."""
        words = []
        for item in data:
            words.extend(item.split())

        if not case_sensitive:
            words = [w.lower() for w in words]

        counter = Counter(words)
        if top_n > 0:
            return dict(counter.most_common(top_n))
        return dict(counter)

    def _char_frequency(self, data: List[str], top_n: int,
                       case_sensitive: bool) -> Dict[str, int]:
        """Calculate character frequency across all items."""
        chars = []
        for item in data:
            if not case_sensitive:
                chars.extend(item.lower())
            else:
                chars.extend(item)

        counter = Counter(chars)
        if top_n > 0:
            return dict(counter.most_common(top_n))
        return dict(counter)

    def _format_count(self, count: int, format_mode: str, label: str) -> List[str]:
        """Format a count value according to format_output."""
        if format_mode == "plain":
            return [str(count)]
        elif format_mode == "labeled":
            return [f"{label}: {count}"]
        elif format_mode == "json":
            return [json.dumps({"count": count, "label": label})]
        return [str(count)]

    def _format_list(self, items: List[str], format_mode: str) -> List[str]:
        """Format a list of items according to format_output."""
        if format_mode == "plain":
            return items
        elif format_mode == "labeled":
            return [f"Item {i+1}: {item}" for i, item in enumerate(items)]
        elif format_mode == "json":
            return [json.dumps({"items": items, "count": len(items)})]
        return items

    def _format_frequency(self, freq: Dict[str, int], format_mode: str) -> List[str]:
        """Format frequency data according to format_output."""
        if format_mode == "plain":
            return [f"{key}: {value}" for key, value in freq.items()]
        elif format_mode == "labeled":
            return [f"Frequency - {key}: {value}" for key, value in freq.items()]
        elif format_mode == "json":
            return [json.dumps(freq)]
        return [f"{key}: {value}" for key, value in freq.items()]

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        # Get parameters
        enabled = self._parms["enabled"].eval()
        stat_mode = self._parms["stat_mode"].eval()
        count_what = self._parms["count_what"].eval()
        preserve_order = self._parms["preserve_order"].eval()
        top_n = self._parms["top_n"].eval()
        case_sensitive = self._parms["case_sensitive"].eval()
        format_output = self._parms["format_output"].eval()

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

            if stat_mode == "count":
                if count_what == "items":
                    count = self._count_items(input_data)
                    result = self._format_count(count, format_output, "Item count")
                elif count_what == "words":
                    count = self._count_words(input_data)
                    result = self._format_count(count, format_output, "Word count")
                elif count_what == "characters":
                    count = self._count_characters(input_data)
                    result = self._format_count(count, format_output, "Character count")
                elif count_what == "lines":
                    count = self._count_lines(input_data)
                    result = self._format_count(count, format_output, "Line count")

            elif stat_mode == "deduplicate":
                deduped = self._deduplicate(input_data, preserve_order, case_sensitive)
                result = self._format_list(deduped, format_output)

            elif stat_mode == "word_freq":
                freq = self._word_frequency(input_data, top_n, case_sensitive)
                result = self._format_frequency(freq, format_output)

            elif stat_mode == "char_freq":
                freq = self._char_frequency(input_data, top_n, case_sensitive)
                result = self._format_frequency(freq, format_output)

            self._output = result

        # Update hashes for caching
        param_str = f"{enabled}{stat_mode}{count_what}{preserve_order}{top_n}{case_sensitive}{format_output}"
        self._param_hash = self._calculate_hash(param_str)
        self._input_hash = self._calculate_hash(str(input_data))

        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        """Check if node needs to recook based on parameter or input changes."""
        if super().needs_to_cook():
            return True

        try:
            enabled = self._parms["enabled"].raw_value()
            stat_mode = self._parms["stat_mode"].raw_value()
            count_what = self._parms["count_what"].raw_value()
            preserve_order = self._parms["preserve_order"].raw_value()
            top_n = self._parms["top_n"].raw_value()
            case_sensitive = self._parms["case_sensitive"].raw_value()
            format_output = self._parms["format_output"].raw_value()

            param_str = f"{enabled}{stat_mode}{count_what}{preserve_order}{top_n}{case_sensitive}{format_output}"
            new_param_hash = self._calculate_hash(param_str)

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
        return {0: "Statistics Output"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}
