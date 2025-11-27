import hashlib
import time
import re
from typing import Dict
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.enums import FunctionalGroup


class StringTransformNode(Node):
    """Performs string transformations on text items.

    Applies various text transformations including find/replace operations,
    regex-based substitutions, case transformations, whitespace normalization,
    and trimming to each item in the input list.

    Attributes:
        GLYPH (str): Display glyph '⎔'
        SINGLE_INPUT (bool): Accepts single input connection
        SINGLE_OUTPUT (bool): Produces single output connection
    """

    GLYPH = '⎔'
    GROUP = FunctionalGroup.TEXT
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    CASE_TRANSFORMS = {
        'upper': str.upper,
        'lower': str.lower,
        'title': str.title,
        'capitalize': str.capitalize
    }

    TRIM_MODES = {
        'both': str.strip,
        'start': str.lstrip,
        'end': str.rstrip
    }

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

        self._parms["operation"].set("find_replace")
        self._parms["find_text"].set("")
        self._parms["replace_text"].set("")
        self._parms["use_regex"].set(False)
        self._parms["case_sensitive"].set(True)
        self._parms["case_mode"].set("upper")
        self._parms["trim_mode"].set("both")
        self._parms["normalize_spaces"].set(False)
        self._parms["enabled"].set(True)

    def _find_replace(self, text: str, find: str, replace: str, use_regex: bool, case_sensitive: bool) -> str:
        if not find:
            return text

        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            return re.sub(re.escape(find) if not use_regex else find, replace, text, flags=flags)
        except re.error as e:
            self.add_warning(f"Regex error: {str(e)}")
            return text

    def _transform_item(self, text: str, operation: str, **params) -> str:
        transforms = {
            'find_replace': lambda t: self._find_replace(t, params['find'], params['replace'],
                                                         params['use_regex'], params['case_sensitive']),
            'regex_replace': lambda t: self._find_replace(t, params['find'], params['replace'],
                                                          params['use_regex'], params['case_sensitive']),
            'case_transform': lambda t: self.CASE_TRANSFORMS.get(params['case_mode'], lambda x: x)(t),
            'trim': lambda t: self.TRIM_MODES.get(params['trim_mode'], lambda x: x)(t),
            'whitespace_normalize': lambda t: re.sub(r'\s+', ' ', t)
        }

        result = transforms.get(operation, lambda t: t)(text)
        return re.sub(r'\s+', ' ', result) if params.get('normalize_spaces') and operation != 'whitespace_normalize' else result

    def _get_input_data(self):
        if not self.inputs():
            return []
        raw = self.inputs()[0].output_node().eval(requesting_node=self)
        return [str(item) for item in raw] if isinstance(raw, list) else []

    def _compute_param_hash(self, accessor='eval'):
        getter = lambda k: getattr(self._parms[k], accessor)()
        keys = ['enabled', 'operation', 'find_text', 'replace_text', 'use_regex',
                'case_sensitive', 'case_mode', 'trim_mode', 'normalize_spaces']
        return hashlib.md5(''.join(str(getter(k)) for k in keys).encode()).hexdigest()

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        p = lambda k: self._parms[k].eval()
        input_data = self._get_input_data()

        self._output = input_data if not p('enabled') or not input_data else [
            self._transform_item(item, p('operation'),
                find=p('find_text'), replace=p('replace_text'),
                use_regex=p('use_regex'), case_sensitive=p('case_sensitive'),
                case_mode=p('case_mode'), trim_mode=p('trim_mode'),
                normalize_spaces=p('normalize_spaces'))
            for item in input_data
        ]

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
        return {0: "Transformed Text"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}
