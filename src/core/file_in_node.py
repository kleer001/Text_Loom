import os
import hashlib
import time
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType

class FileInNode(Node):
    """
    FileInNode: A node that reads and parses text files or input strings into lists.

    This node can either read from a file or take input text, parsing formatted string lists 
    like "[item1, item2, item3]" into proper Python lists. If no input is provided, reads 
    from the specified file.

    Parameters:
        file_name (str): Path to the target file (defaults to "./input.txt")
        file_text (str): Contains the current file content
        refresh (button): Force reloads the file content

    Input Processing:
        - If input is provided, uses that instead of file content
        - Parses text in format "[item1, item2, ...]" into list items
        - Handles quoted strings, escapes, and empty items
        - Falls back to single-item list for invalid formats

    Features:
        - Monitors file changes using MD5 hashing
        - Automatically reloads when file content changes
        - Provides error reporting for file access issues
        - Supports force refresh via button

    Example Usage:
        1. File reading:
        Input: None
        File: "['a', 'b', 'c']"
        Output: ["a", "b", "c"]
        
        2. Input processing:
        Input: ["[1, 2, 3]"]
        Output: ["1", "2", "3"]
        
        3. Raw text:
        Input: ["plain text"]
        Output: ["plain text"]

    Notes:
        - Always time dependent (_is_time_dependent = True)
        - Accepts optional input to override file content
        - Output is List[str] containing parsed items
        - Reports detailed errors for file and parsing issues
    """

    GLYPH = '⤵'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.FILE_IN)
        self._is_time_dependent = False
        self._file_hash = None

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "file_name": Parm("file_name", ParameterType.STRING, self),
            "file_text": Parm("file_text", ParameterType.STRING, self),
            "refresh": Parm("refresh", ParameterType.BUTTON, self)
        }

        # Set default values
        self._parms["file_name"].set("./input.txt")  # Default to current directory
        self._parms["file_text"].set("")

        # Set up refresh button callback
        self._parms["refresh"].set_script_callback("self.node().refresh()")

    def validate_parameters(self) -> bool:
        file_system_path = self._parms["file_system_path"].eval()
        file_name = self._parms["file_name"].eval()
        
        if not isinstance(file_system_path, str) or not os.path.isdir(file_system_path):
            self.add_error(f"Invalid file system path: {file_system_path}")
            return False
        
        if not isinstance(file_name, str) or not file_name:
            self.add_error(f"Invalid file name: {file_name}")
            return False
        
        return True

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        # First process any input text
        input_text = ""
        if self.inputs():
            input_data = self.inputs()[0].output_node().eval(requesting_node=self)
            if isinstance(input_data, list) and len(input_data) > 0:
                input_text = input_data[0]  # Take first item if it's a list

        try:
            # Read file content
            full_file_path = self._parms["file_name"].eval()
            print(f"Attempting to read file: {full_file_path}")

            if not full_file_path:
                raise ValueError("File path is empty or None")

            if not os.path.exists(full_file_path):
                raise FileNotFoundError(f"File not found: {full_file_path}")

            with open(full_file_path, 'r') as file:
                content = file.read()

            # Use input text if available, otherwise use file content
            text_to_parse = input_text if input_text else content

            # Parse the content into a list
            parsed_content = self._parse_string_list(text_to_parse)

            new_hash = self._calculate_file_hash(content)
            if force or new_hash != self._file_hash:
                self._parms["file_text"].set(content)
                self._output = parsed_content
                self._file_hash = new_hash

            self.set_state(NodeState.UNCHANGED)
            print(f"Successfully processed content. Items: {len(parsed_content)}")

        except Exception as e:
            self.add_error(f"Error processing content: {str(e)}")
            self.set_state(NodeState.UNCOOKED)
            print(f"Exception details: {type(e).__name__}: {str(e)}")

        self._last_cook_time = (time.time() - start_time) * 1000


    def input_names(self) -> Dict[str, str]:
        return {}  # No inputs for this node

    def output_names(self) -> Dict[str, str]:
        return {"output": "File Content"}

    def input_data_types(self) -> Dict[str, str]:
        return {}  # No inputs for this node

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def validate_file_system_path(self):
        path = self._parms["file_system_path"].eval()
        if not os.path.isdir(path):
            self.add_error(f"Invalid file system path: {path}")
            return False
        return True

    def refresh(self) -> None:
        if self.validate_file_system_path():
            self.cook(force=True)

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            file_name = self._parms["file_name"].eval()
            file_path = os.path.join(os.path.dirname(self.path()), file_name)

            with open(file_path, 'r') as file:
                content = file.read()

            new_hash = self._calculate_file_hash(content)
            return new_hash != self._file_hash

        except Exception:
            return True

    def _calculate_file_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()
