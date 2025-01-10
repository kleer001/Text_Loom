from typing import List, Dict, Any, Optional, Tuple
import hashlib
import re
import time
import random
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType

class SplitNode(Node):
    SINGLE_OUTPUT = False
    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = True
        self._input_hash = None
        self._param_hash = None
        self._output = [[], [], []]

        self._parms: Dict[str, Parm] = {
            "enabled": Parm("enabled", ParameterType.TOGGLE, self),
            "split_expr": Parm("split_expr", ParameterType.STRING, self),
        }

        self._parms["enabled"].set(True)
        self._parms["split_expr"].set("")

    def _validate_list_expression(self, expr: str) -> bool:
        return bool(re.match(r'^\[[-\d:]*\]$', expr))

    def _validate_random_expression(self, expr: str) -> bool:
        return bool(re.match(r'^random\((time|\d+)(?:,\d+)?\)$', expr))

    def _process_list_expression(self, expr: str, input_list: List[str]) -> Tuple[List[str], List[str]]:
        try:
            slice_expr = expr[1:-1]  # Remove brackets
            if not slice_expr:
                return [], input_list
                
            parts = slice_expr.split(':')
            
            if len(parts) == 1:
                idx = int(parts[0])
                if -len(input_list) <= idx < len(input_list):
                    item = input_list[idx]
                    # For negative indices, we need to convert to positive
                    pos_idx = idx if idx >= 0 else len(input_list) + idx
                    remainder = input_list[:pos_idx] + input_list[pos_idx + 1:]
                    return [item], remainder
                return [], input_list

            slice_args = [int(x) if x else None for x in parts]
            selected = input_list[slice(*slice_args)]
            
            if not selected:
                return [], input_list
                
            # Create a set of indices that were selected
            slice_obj = slice(*slice_args)
            selected_indices = set(range(*slice_obj.indices(len(input_list))))
            
            # Keep items that weren't selected, maintaining order
            remainder = [x for i, x in enumerate(input_list) if i not in selected_indices]
            
            return list(selected), remainder
        except (ValueError, IndexError):
            return [], input_list
        
    def _process_random_expression(self, expr: str, input_list: List[str]) -> Tuple[List[str], List[str]]:
        try:
            match = re.match(r'^random\((time|\d+)(?:,(\d+))?\)$', expr)
            if not match:
                return [], input_list

            seed_str, count_str = match.groups()
            seed = int(time.time()) if seed_str == 'time' else int(seed_str)
            count = int(count_str) if count_str else 1
            count = min(count, len(input_list))

            rng = random.Random(seed)
            indices = list(range(len(input_list)))
            selected_indices = set(rng.sample(indices, count))
            
            selected = [input_list[i] for i in sorted(selected_indices)]
            remainder = [item for i, item in enumerate(input_list) if i not in selected_indices]

            return selected, remainder
        except (ValueError, IndexError):
            return [], input_list

    def _process_split(self, expr: str, input_list: List[str]) -> Tuple[List[str], List[str]]:
        #print(f"DEBUG _process_split: Expression: {expr}")
        #print(f"DEBUG _process_split: Input list: {input_list}")
        
        if not expr:
            return input_list, []
        
        if self._validate_list_expression(expr):
            result = self._process_list_expression(expr, input_list)
            return result
        elif self._validate_random_expression(expr):
            result = self._process_random_expression(expr, input_list)
            return result
        else:
            return input_list, []
        
    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        enabled = self._parms["enabled"].eval()
        split_expr = self._parms["split_expr"].eval()
        
        input_data = []
        if self.inputs():
            input_node = self.inputs()[0].output_node()
            raw_input = input_node.eval(requesting_node=self)
            if isinstance(raw_input, list) and all(isinstance(x, str) for x in raw_input):
                input_data = raw_input
            else:
                self.add_error("Input must be List[str]")

        if enabled and input_data and not self.errors():
            selected, remainder = self._process_split(split_expr, input_data)
            self._output = [selected, remainder, []]
            
            # Update just the directly connected output nodes
            for output_idx in [0, 1]:  # Only for main and remainder outputs
                if output_idx in self._outputs:
                    for conn in self._outputs[output_idx]:
                        conn.input_node().set_state(NodeState.UNCOOKED)
        else:
            self._output = [input_data if input_data else [], [], []]

        self._param_hash = self._calculate_hash(str(enabled) + split_expr)
        self._input_hash = self._calculate_hash(str(input_data))
        
        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True
                
        try:
            enabled = self._parms["enabled"].eval()  # Changed to eval()
            split_expr = self._parms["split_expr"].eval()  # Changed to eval()
            new_param_hash = self._calculate_hash(str(enabled) + split_expr)

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
        return {"0": "Input List"}

    def output_names(self) -> Dict[str, str]:
        return {
            "0": "Selected Items",
            "1": "Remaining Items",
            "2": "Empty"
        }

    def input_data_types(self) -> Dict[str, str]:
        return {"0": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {
            "0": "List[str]",
            "1": "List[str]",
            "2": "List[str]"
        }