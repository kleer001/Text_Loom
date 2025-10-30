import json
import time
from typing import List, Dict, Any, Union
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType


class JsonNode(Node):
    """
    A node that parses JSON text and extracts data as text lists.

    Takes JSON text as input and extracts values based on a JSONPath-style query.
    All output is returned as List[str] - everything is stringified for text processing.

    Parameters:
    -----------
    json_path : str
        JSONPath or dot notation to extract data.
        Examples: "items", "data.results", "users[*].name"
        Empty string returns entire JSON as formatted text.

    extraction_mode : str
        How to extract data from the resolved path:
        - "array": Extract array items as list
        - "values": Extract object values as list
        - "keys": Extract object keys as list
        - "flatten": Flatten nested structure to single-level list

    format_output : str
        How to format each output item:
        - "raw": Plain values as strings
        - "labeled": Key-value pairs (e.g., "name: Alice")
        - "json": Each item as JSON string

    on_parse_error : str
        How to handle JSON parsing errors:
        - "warn": Log warning, output empty list with single empty string
        - "passthrough": Return original text unchanged
        - "empty": Return list with single empty string

    max_depth : int
        Maximum nesting level to traverse (0 = unlimited).
        Prevents infinite recursion on circular references.

    enabled : bool
        If False, passes through input unchanged.

    Input: List[str] (expects single JSON string)
    Output: List[str] (extracted values as strings)
    """

    GLYPH = '{'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False

        self._parms.update({
            "json_path": Parm("json_path", ParameterType.STRING, self),
            "extraction_mode": Parm("extraction_mode", ParameterType.STRING, self),
            "format_output": Parm("format_output", ParameterType.STRING, self),
            "on_parse_error": Parm("on_parse_error", ParameterType.STRING, self),
            "max_depth": Parm("max_depth", ParameterType.INT, self),
        })

        # Set defaults
        self._parms["json_path"].set("")
        self._parms["extraction_mode"].set("array")
        self._parms["format_output"].set("raw")
        self._parms["on_parse_error"].set("warn")
        self._parms["max_depth"].set(0)

    def _internal_cook(self, force: bool = False) -> None:
        """Process JSON input and extract data based on parameters."""
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            # Get input data
            input_data = [""]
            if self.inputs():
                input_data = self.inputs()[0].output_node().eval(requesting_node=self)

            # Check if enabled
            if not self._parms["enabled"].eval():
                self._output = input_data
                self.set_state(NodeState.UNCHANGED)
                return

            # Get parameters
            json_path = self._parms["json_path"].eval()
            extraction_mode = self._parms["extraction_mode"].eval()
            format_output = self._parms["format_output"].eval()
            on_parse_error = self._parms["on_parse_error"].eval()
            max_depth = self._parms["max_depth"].eval()

            # Get JSON string from input (expect first item)
            json_string = input_data[0] if input_data else ""

            # Parse JSON
            try:
                data = json.loads(json_string)
            except json.JSONDecodeError as e:
                if on_parse_error == "warn":
                    self.add_warning(f"JSON parse error: {str(e)}")
                    self._output = [""]
                elif on_parse_error == "passthrough":
                    self._output = input_data
                else:  # empty
                    self._output = [""]
                self.set_state(NodeState.UNCHANGED)
                self._last_cook_time = (time.time() - start_time) * 1000
                return

            # Extract data based on json_path
            if json_path:
                extracted = self._extract_path(data, json_path)
            else:
                # No path specified, use entire JSON
                extracted = data

            # Process extracted data based on extraction_mode
            result = self._process_extraction(
                extracted, extraction_mode, format_output, max_depth
            )

            self._output = result
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error in JsonNode: {str(e)}")
            self._output = [""]
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000

    def _extract_path(self, data: Any, path: str) -> Any:
        """
        Extract data from JSON using a simplified JSONPath syntax.
        Supports:
        - Dot notation: data.results
        - Array indexing: items[0]
        - Wildcards: users[*].name
        """
        current = data
        parts = self._parse_path(path)

        for part in parts:
            if part == "*":
                # Wildcard - expand current array
                if isinstance(current, list):
                    # Continue with remaining parts for each item
                    remaining_parts = parts[parts.index(part) + 1:]
                    if remaining_parts:
                        results = []
                        for item in current:
                            try:
                                result = self._extract_from_parts(item, remaining_parts)
                                if isinstance(result, list):
                                    results.extend(result)
                                else:
                                    results.append(result)
                            except (KeyError, IndexError, TypeError):
                                continue
                        return results
                    else:
                        return current
                else:
                    raise TypeError(f"Cannot apply wildcard to non-array type")
            elif isinstance(part, int):
                # Array index
                if isinstance(current, list):
                    current = current[part]
                else:
                    raise TypeError(f"Cannot index non-array with [{part}]")
            else:
                # Object key
                if isinstance(current, dict):
                    current = current[part]
                else:
                    raise TypeError(f"Cannot access key '{part}' on non-object")

        return current

    def _extract_from_parts(self, data: Any, parts: List[Union[str, int]]) -> Any:
        """Helper to extract data given a list of path parts."""
        current = data
        for i, part in enumerate(parts):
            if part == "*":
                if isinstance(current, list):
                    # Check if there are remaining parts after this wildcard
                    remaining_parts = parts[i + 1:]
                    if remaining_parts:
                        # Recursively process each item with remaining parts
                        results = []
                        for item in current:
                            try:
                                result = self._extract_from_parts(item, remaining_parts)
                                if isinstance(result, list):
                                    results.extend(result)
                                else:
                                    results.append(result)
                            except (KeyError, IndexError, TypeError):
                                continue
                        return results
                    else:
                        # No more parts, return the array
                        return current
                else:
                    raise TypeError(f"Cannot apply wildcard to non-array")
            elif isinstance(part, int):
                if isinstance(current, list):
                    current = current[part]
                else:
                    raise TypeError(f"Cannot index non-array")
            else:
                if isinstance(current, dict):
                    current = current[part]
                else:
                    raise TypeError(f"Cannot access key on non-object")
        return current

    def _parse_path(self, path: str) -> List[Union[str, int]]:
        """
        Parse a path string into components.
        Examples:
        - "items" -> ["items"]
        - "data.results" -> ["data", "results"]
        - "users[0].name" -> ["users", 0, "name"]
        - "users[*].name" -> ["users", "*", "name"]
        """
        parts = []
        current = ""
        i = 0

        while i < len(path):
            char = path[i]

            if char == ".":
                # Dot separator
                if current:
                    parts.append(current)
                    current = ""
            elif char == "[":
                # Array index or wildcard
                if current:
                    parts.append(current)
                    current = ""

                # Find closing bracket
                j = i + 1
                while j < len(path) and path[j] != "]":
                    j += 1

                if j >= len(path):
                    raise ValueError(f"Unclosed bracket in path: {path}")

                index_str = path[i + 1:j]
                if index_str == "*":
                    parts.append("*")
                else:
                    try:
                        parts.append(int(index_str))
                    except ValueError:
                        raise ValueError(f"Invalid array index: {index_str}")

                i = j  # Skip to closing bracket
            else:
                current += char

            i += 1

        if current:
            parts.append(current)

        return parts

    def _process_extraction(
        self, data: Any, mode: str, format_output: str, max_depth: int
    ) -> List[str]:
        """
        Process extracted data based on extraction mode and format.
        Always returns List[str].
        """
        if mode == "array":
            return self._extract_array(data, format_output)
        elif mode == "values":
            return self._extract_values(data, format_output)
        elif mode == "keys":
            return self._extract_keys(data)
        elif mode == "flatten":
            return self._extract_flatten(data, format_output, max_depth)
        else:
            # Default to array mode
            return self._extract_array(data, format_output)

    def _extract_array(self, data: Any, format_output: str) -> List[str]:
        """Extract array items as list."""
        if isinstance(data, list):
            return [self._format_item(item, format_output) for item in data]
        else:
            # Single value, wrap in list
            return [self._format_item(data, format_output)]

    def _extract_values(self, data: Any, format_output: str) -> List[str]:
        """Extract object values as list."""
        if isinstance(data, dict):
            return [self._format_item(value, format_output) for value in data.values()]
        elif isinstance(data, list):
            # Already a list, process each item
            return [self._format_item(item, format_output) for item in data]
        else:
            # Single value, wrap in list
            return [self._format_item(data, format_output)]

    def _extract_keys(self, data: Any) -> List[str]:
        """Extract object keys as list."""
        if isinstance(data, dict):
            return [str(key) for key in data.keys()]
        elif isinstance(data, list):
            # Return indices as strings
            return [str(i) for i in range(len(data))]
        else:
            # Single value has no keys
            return ["0"]

    def _extract_flatten(
        self, data: Any, format_output: str, max_depth: int, current_depth: int = 0, prefix: str = ""
    ) -> List[str]:
        """Flatten nested structure to single-level list with paths."""
        if max_depth > 0 and current_depth >= max_depth:
            return [f"{prefix}: {self._stringify(data)}"]

        results = []

        if isinstance(data, dict):
            for key, value in data.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    results.extend(
                        self._extract_flatten(
                            value, format_output, max_depth, current_depth + 1, new_prefix
                        )
                    )
                else:
                    results.append(f"{new_prefix}: {self._stringify(value)}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_prefix = f"{prefix}[{i}]"
                if isinstance(item, (dict, list)):
                    results.extend(
                        self._extract_flatten(
                            item, format_output, max_depth, current_depth + 1, new_prefix
                        )
                    )
                else:
                    results.append(f"{new_prefix}: {self._stringify(item)}")
        else:
            # Leaf value
            if prefix:
                results.append(f"{prefix}: {self._stringify(data)}")
            else:
                results.append(self._stringify(data))

        return results

    def _format_item(self, item: Any, format_output: str) -> str:
        """Format a single item based on format_output parameter."""
        if format_output == "json":
            return json.dumps(item, ensure_ascii=False)
        elif format_output == "labeled":
            # For labeled format, if item is dict, create key:value pairs
            if isinstance(item, dict):
                pairs = [f"{key}: {self._stringify(value)}" for key, value in item.items()]
                return ", ".join(pairs)
            else:
                return self._stringify(item)
        else:  # raw
            return self._stringify(item)

    def _stringify(self, value: Any) -> str:
        """Convert any value to string representation."""
        if isinstance(value, str):
            return value
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif value is None:
            return ""
        else:
            # Complex types, use JSON representation
            return json.dumps(value, ensure_ascii=False)

    def input_names(self) -> Dict[str, str]:
        return {"input": "Input"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Output"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}