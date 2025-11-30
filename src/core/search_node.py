import hashlib
import time
import re
from typing import Dict, Tuple
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.enums import FunctionalGroup


class SearchNode(Node):
    """A node that searches and filters text items based on patterns and keywords.

    Supports multiple search modes (contains, exact, starts_with, ends_with, regex)
    and can combine multiple keywords with AND/OR/NOT boolean logic. Provides dual
    outputs for matching and non-matching items, making it ideal for filtering and
    routing text through node graphs.

    Attributes:
        search_text (str): The search term(s) to match against. Multiple terms can be
            separated by commas or spaces. Each term is treated according to the
            boolean_mode setting.
        search_mode (str): Determines how to match search terms. Options: "contains"
            (item contains term anywhere), "exact" (item equals term), "starts_with"
            (item starts with term), "ends_with" (item ends with term), "regex"
            (term is regular expression).
        case_sensitive (bool): When True, matches are case-sensitive. When False,
            ignores case differences.
        boolean_mode (str): Controls how multiple search terms are combined. Options:
            "OR" (matches items matching ANY term), "AND" (matches items matching ALL
            terms), "NOT" (matches items matching NONE of the terms).
        invert_match (bool): When True, inverts the matching logic (matching items go
            to non-matching output and vice versa).
        enabled (bool): Enables/disables the node's functionality.

    Example:
        >>> node = Node.create_node(NodeType.SEARCH, node_name="filter")
        >>> node._parms["search_text"].set("apple, banana")
        >>> node._parms["search_mode"].set("contains")
        >>> node._parms["boolean_mode"].set("OR")
        >>> node.cook()
        # Matches items containing either "apple" or "banana"

    Note:
        **Search Modes:**
        *   "contains": Item contains the search term anywhere
        *   "exact": Item exactly equals the search term
        *   "starts_with": Item starts with the search term
        *   "ends_with": Item ends with the search term
        *   "regex": Search term is interpreted as a regular expression

        **Boolean Logic:**
        *   "OR": Matches items that match ANY search term
        *   "AND": Matches items that match ALL search terms
        *   "NOT": Matches items that match NONE of the search terms

        **Input:**
        *   `List[str]`: Collection of text items to search/filter

        **Outputs:**
        *   Output 0 (Matching): Items that match the search criteria
        *   Output 1 (Non-Matching): Items that don't match the search criteria
        *   Output 2 (Empty): Always empty list (reserved for future use)

        **Edge Cases:**
        *   Multiple search terms in search_text are split by commas or whitespace
        *   Empty search_text matches nothing (all items go to non-matching output)
        *   Invalid regex patterns generate warnings and fail to match
        *   Case-insensitive mode converts both text and terms to lowercase
        *   Combining invert_match with boolean_mode allows complex filtering logic
    """

    GLYPH = '🔍'
    GROUP = FunctionalGroup.LIST
    SINGLE_INPUT = True
    SINGLE_OUTPUT = False

    MATCHERS = {
        'contains': lambda text, term: term in text,
        'exact': lambda text, term: text == term,
        'starts_with': str.startswith,
        'ends_with': str.endswith
    }

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None
        self._output = [[], [], []]

        self._parms.update({
            "search_text": Parm("search_text", ParameterType.STRING, self),
            "search_mode": Parm("search_mode", ParameterType.MENU, self),
            "case_sensitive": Parm("case_sensitive", ParameterType.TOGGLE, self),
            "boolean_mode": Parm("boolean_mode", ParameterType.MENU, self),
            "invert_match": Parm("invert_match", ParameterType.TOGGLE, self),
            "enabled": Parm("enabled", ParameterType.TOGGLE, self),
        })

        self._parms["search_text"].set("")
        self._parms["search_mode"].set("contains")
        self._parms["case_sensitive"].set(False)
        self._parms["boolean_mode"].set("OR")
        self._parms["invert_match"].set(False)
        self._parms["enabled"].set(True)

    def _matches_term(self, text: str, term: str, mode: str, case_sensitive: bool) -> bool:
        if not case_sensitive:
            text, term = text.lower(), term.lower()

        if mode == 'regex':
            try:
                return bool(re.search(term, text, 0 if case_sensitive else re.IGNORECASE))
            except re.error as e:
                self.add_warning(f"Invalid regex: {e}")
                return False

        return self.MATCHERS.get(mode, lambda t, r: False)(text, term)

    def _filter_items(self, items, terms, mode, case_sensitive, boolean_mode, invert) -> Tuple:
        if not terms:
            return (items, []) if not invert else ([], items)

        evaluators = {
            'AND': lambda item: all(self._matches_term(item, t, mode, case_sensitive) for t in terms),
            'OR': lambda item: any(self._matches_term(item, t, mode, case_sensitive) for t in terms),
            'NOT': lambda item: not any(self._matches_term(item, t, mode, case_sensitive) for t in terms)
        }

        matcher = evaluators.get(boolean_mode, lambda item: False)
        matching, non_matching = [], []

        for item in items:
            (matching if matcher(item) != invert else non_matching).append(item)

        return matching, non_matching

    def _get_input_data(self):
        if not self.inputs():
            return []
        raw = self.inputs()[0].output_node().eval(requesting_node=self)
        return [str(item) for item in raw] if isinstance(raw, list) else []

    def _compute_param_hash(self, accessor='eval'):
        getter = lambda k: getattr(self._parms[k], accessor)()
        keys = ['enabled', 'search_text', 'search_mode', 'case_sensitive', 'boolean_mode', 'invert_match']
        return hashlib.md5(''.join(str(getter(k)) for k in keys).encode()).hexdigest()

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        p = lambda k: self._parms[k].eval()
        input_data = self._get_input_data()

        if not p('enabled') or not input_data:
            self._output = [input_data, [], []]
        else:
            terms = [t.strip() for t in re.split(r'[,\s]+', p('search_text')) if t.strip()]
            matching, non_matching = self._filter_items(
                input_data, terms, p('search_mode'),
                p('case_sensitive'), p('boolean_mode'), p('invert_match')
            )
            self._output = [matching, non_matching, []]

            for output_idx in [0, 1]:
                if output_idx in self._outputs:
                    for conn in self._outputs[output_idx]:
                        conn.input_node().set_state(NodeState.UNCOOKED)

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
        return {0: "Input List"}

    def output_names(self) -> Dict[int, str]:
        return {
            0: "Matching Items",
            1: "Non-Matching Items",
            2: "Empty"
        }

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {
            0: "List[str]",
            1: "List[str]",
            2: "List[str]"
        }
