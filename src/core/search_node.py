import hashlib
import time
import re
from typing import List, Dict, Tuple
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType


class SearchNode(Node):
    """Searches and filters text items based on patterns and keywords.

    GLYPH: 🔍

    Supports multiple search modes (contains, exact, starts_with, ends_with, regex).
    Can combine multiple keywords with AND/OR logic.
    Provides two outputs: matching items and non-matching items.
    """

    GLYPH = '🔍'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = False

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

    def _parse_search_terms(self, search_text: str) -> List[str]:
        terms = [t.strip() for t in re.split(r'[,\s]+', search_text) if t.strip()]
        return terms

    def _matches_term(self, text: str, term: str, mode: str,
                     case_sensitive: bool) -> bool:
        if not case_sensitive:
            text = text.lower()
            term = term.lower()

        if mode == "contains":
            return term in text
        elif mode == "exact":
            return text == term
        elif mode == "starts_with":
            return text.startswith(term)
        elif mode == "ends_with":
            return text.endswith(term)
        elif mode == "regex":
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                return bool(re.search(term, text, flags=flags))
            except re.error:
                self.add_warning(f"Invalid regex pattern: {term}")
                return False
        return False

    def _item_matches(self, item: str, terms: List[str], mode: str,
                     case_sensitive: bool, boolean_mode: str) -> bool:
        if not terms:
            return True

        if boolean_mode == "AND":
            return all(self._matches_term(item, term, mode, case_sensitive)
                      for term in terms)
        elif boolean_mode == "OR":
            return any(self._matches_term(item, term, mode, case_sensitive)
                      for term in terms)
        elif boolean_mode == "NOT":
            return not any(self._matches_term(item, term, mode, case_sensitive)
                          for term in terms)
        return False

    def _filter_items(self, items: List[str], search_text: str, mode: str,
                     case_sensitive: bool, boolean_mode: str,
                     invert_match: bool) -> Tuple[List[str], List[str]]:
        terms = self._parse_search_terms(search_text)

        matching = []
        non_matching = []

        for item in items:
            matches = self._item_matches(item, terms, mode, case_sensitive, boolean_mode)

            if invert_match:
                matches = not matches

            if matches:
                matching.append(item)
            else:
                non_matching.append(item)

        return matching, non_matching

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        enabled = self._parms["enabled"].eval()
        search_text = self._parms["search_text"].eval()
        search_mode = self._parms["search_mode"].eval()
        case_sensitive = self._parms["case_sensitive"].eval()
        boolean_mode = self._parms["boolean_mode"].eval()
        invert_match = self._parms["invert_match"].eval()

        input_data = []
        if self.inputs():
            raw_input = self.inputs()[0].output_node().eval(requesting_node=self)
            if isinstance(raw_input, list):
                input_data = [str(item) for item in raw_input]

        if not enabled or not input_data:
            self._output = [input_data, [], []]
        else:
            matching, non_matching = self._filter_items(
                input_data, search_text, search_mode,
                case_sensitive, boolean_mode, invert_match
            )
            self._output = [matching, non_matching, []]

            for output_idx in [0, 1]:
                if output_idx in self._outputs:
                    for conn in self._outputs[output_idx]:
                        conn.input_node().set_state(NodeState.UNCOOKED)

        param_str = f"{enabled}{search_text}{search_mode}{case_sensitive}{boolean_mode}{invert_match}"
        self._param_hash = self._calculate_hash(param_str)
        self._input_hash = self._calculate_hash(str(input_data))

        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            enabled = self._parms["enabled"].raw_value()
            search_text = self._parms["search_text"].raw_value()
            search_mode = self._parms["search_mode"].raw_value()
            case_sensitive = self._parms["case_sensitive"].raw_value()
            boolean_mode = self._parms["boolean_mode"].raw_value()
            invert_match = self._parms["invert_match"].raw_value()

            param_str = f"{enabled}{search_text}{search_mode}{case_sensitive}{boolean_mode}{invert_match}"
            new_param_hash = self._calculate_hash(param_str)

            input_data = []
            if self.inputs():
                input_data = self.inputs()[0].output_node().get_output()
            new_input_hash = self._calculate_hash(str(input_data))

            return new_input_hash != self._input_hash or new_param_hash != self._param_hash
        except Exception:
            return True

    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

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
