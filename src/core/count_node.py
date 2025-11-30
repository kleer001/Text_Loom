import hashlib
import time
import json
from typing import Dict
from collections import Counter
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.enums import FunctionalGroup


class CountNode(Node):
    """A node that performs counting and statistical operations on text lists.

    Provides counting operations (items, words, characters, lines), deduplication with
    order preservation, and frequency analysis for words and characters. Results can be
    formatted as plain text, labeled output, or JSON for downstream processing.

    Attributes:
        stat_mode (str): Determines the statistical operation to perform. Options:
            "count" (counts based on count_what parameter), "deduplicate" (removes
            duplicate items from list), "word_freq" (analyzes word frequency across
            all input items), "char_freq" (analyzes character frequency).
        count_what (str): When stat_mode is "count", specifies what to count. Options:
            "items" (total number of list items), "words" (total word count across
            all items), "characters" (total character count), "lines" (total line
            count including newlines + 1 per item).
        preserve_order (bool): When True in deduplicate mode, maintains the original
            order of first occurrences. When False, sorts deduplicated items
            alphabetically.
        top_n (int): For frequency modes, limits output to top N most frequent items.
            Set to 0 for unlimited (all items).
        case_sensitive (bool): When True, treats uppercase and lowercase as distinct
            in deduplication and frequency analysis. When False, normalizes to lowercase.
        format_output (str): Determines output format. Options: "plain" (simple values
            or key: value for frequencies), "labeled" (descriptive labels like
            "Items count: 5"), "json" (JSON formatted output for programmatic processing).
        enabled (bool): Enables/disables the node's functionality.

    Example:
        >>> node = Node.create_node(NodeType.COUNT, node_name="counter")
        >>> node._parms["stat_mode"].set("count")
        >>> node._parms["count_what"].set("words")
        >>> node._parms["format_output"].set("plain")
        >>> node.cook()
        # Outputs total word count as a string

    Note:
        **Statistical Modes:**
        *   "count": Counts items, words, characters, or lines based on count_what
        *   "deduplicate": Removes duplicate items (optionally preserving order)
        *   "word_freq": Analyzes word frequency across all input items
        *   "char_freq": Analyzes character frequency across all input items

        **Count Types:**
        *   "items": Total number of list items
        *   "words": Total word count (whitespace splitting)
        *   "characters": Total character count across all items
        *   "lines": Total line count (counts newlines + 1 per item)

        **Format Options:**
        *   "plain": Simple values ["4"] or ["word: 5", "hello: 3"]
        *   "labeled": Descriptive ["Items count: 4"] or ["Item 1: value"]
        *   "json": JSON format for programmatic processing

        **Input:**
        *   `List[str]`: Collection of text items to analyze

        **Output:**
        *   `List[str]`: Statistical results (format depends on stat_mode and format_output)

        **Edge Cases:**
        *   Word counting uses simple whitespace splitting
        *   Line counting includes implicit final line (count of newlines + 1 per item)
        *   Deduplication with preserve_order=False uses alphabetical sorting
        *   Frequency analysis with top_n=0 returns all items sorted by frequency
        *   Case-insensitive mode normalizes text to lowercase for comparison
    """

    GLYPH = '#'
    GROUP = FunctionalGroup.LIST
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    COUNTERS = {
        'items': lambda data: len(data),
        'words': lambda data: sum(len(item.split()) for item in data),
        'characters': lambda data: sum(len(item) for item in data),
        'lines': lambda data: sum(item.count('\n') + 1 for item in data)
    }

    FORMATTERS = {
        'plain': lambda v, l=None: [str(v)] if isinstance(v, int) else ([f"{k}: {c}" for k, c in v.items()] if isinstance(v, dict) else v),
        'labeled': lambda v, l=None: [f"{l}: {v}"] if isinstance(v, int) else ([f"Item {i+1}: {item}" for i, item in enumerate(v)] if isinstance(v, list) else [f"Frequency - {k}: {c}" for k, c in v.items()]),
        'json': lambda v, l=None: [json.dumps({"count": v, "label": l})] if isinstance(v, int) else ([json.dumps({"items": v, "count": len(v)})] if isinstance(v, list) else [json.dumps(v)])
    }

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

        self._parms["stat_mode"].set("count")
        self._parms["count_what"].set("items")
        self._parms["preserve_order"].set(True)
        self._parms["top_n"].set(0)
        self._parms["case_sensitive"].set(False)
        self._parms["format_output"].set("plain")
        self._parms["enabled"].set(True)

    def _deduplicate(self, data, preserve_order, case_sensitive):
        normalizer = (lambda x: x) if case_sensitive else str.lower
        if preserve_order:
            seen = set()
            return [item for item in data if not (normalizer(item) in seen or seen.add(normalizer(item)))]
        seen = {normalizer(item): item for item in data}
        return sorted(seen.values())

    def _frequency(self, items, top_n):
        counter = Counter(items)
        return dict(counter.most_common(top_n) if top_n > 0 else counter)

    def _get_input_data(self):
        if not self.inputs():
            return []
        raw = self.inputs()[0].output_node().eval(requesting_node=self)
        return [str(item) for item in raw] if isinstance(raw, list) else []

    def _compute_param_hash(self, accessor='eval'):
        getter = lambda k: getattr(self._parms[k], accessor)()
        keys = ['enabled', 'stat_mode', 'count_what', 'preserve_order', 'top_n', 'case_sensitive', 'format_output']
        return hashlib.md5(''.join(str(getter(k)) for k in keys).encode()).hexdigest()

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        p = lambda k: self._parms[k].eval()
        input_data = self._get_input_data()

        if not p('enabled') or not input_data:
            self._output = input_data
        else:
            mode = p('stat_mode')
            fmt = p('format_output')

            if mode == 'count':
                count = self.COUNTERS[p('count_what')](input_data)
                result = self.FORMATTERS[fmt](count, f"{p('count_what').capitalize()} count")
            elif mode == 'deduplicate':
                deduped = self._deduplicate(input_data, p('preserve_order'), p('case_sensitive'))
                result = self.FORMATTERS[fmt](deduped)
            elif mode == 'word_freq':
                words = [w if p('case_sensitive') else w.lower() for item in input_data for w in item.split()]
                result = self.FORMATTERS[fmt](self._frequency(words, p('top_n')))
            elif mode == 'char_freq':
                chars = [c if p('case_sensitive') else c.lower() for item in input_data for c in item]
                result = self.FORMATTERS[fmt](self._frequency(chars, p('top_n')))
            else:
                result = input_data

            self._output = result

        self._param_hash = self._compute_param_hash()
        self._input_hash = hashlib.md5(str(input_data).encode()).hexdigest()
        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True
        try:
            return (self._compute_param_hash('raw_value') != self._param_hash or
                    hashlib.md5(str(self._get_input_data()).encode()).hexdigest() != self._input_hash)
        except Exception:
            return True

    def input_names(self) -> Dict[int, str]:
        return {0: "Input Text"}

    def output_names(self) -> Dict[int, str]:
        return {0: "Statistics Output"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}
