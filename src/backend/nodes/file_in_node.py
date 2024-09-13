import os
import hashlib
import time
from typing import List, Dict, Any
from base_classes import Node, NodeType, NodeState
from parm import Parm, ParameterType

class FileInNode(Node):

    """Reads content from a specified file and stores it as a parameter.
    Provides functionality to refresh file content and track file changes."""

    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.FILE_IN)
        self._is_time_dependent = True
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

    def cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        full_file_path = self._parms["file_name"].eval()

        try:
            full_file_path = self._parms["file_name"].eval()
            print(f"Attempting to read file: {full_file_path}")  # Debug print

            if not full_file_path:
                raise ValueError("File path is empty or None")

            if not os.path.exists(full_file_path):
                raise FileNotFoundError(f"File not found: {full_file_path}")

            with open(full_file_path, 'r') as file:
                content = file.read()

            new_hash = self._calculate_file_hash(content)
            if force or new_hash != self._file_hash:
                self._parms["file_text"].set(content)
                self._file_hash = new_hash

            self.set_state(NodeState.UNCHANGED)
            print(f"Successfully read file. Content length: {len(content)}")  # Debug print

        except Exception as e:
            self.add_error(f"Error reading file: {str(e)}")
            self.set_state(NodeState.UNCOOKED)
            print(f"Exception details: {type(e).__name__}: {str(e)}")  # Debug print

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds


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

    def eval(self) -> List[str]:
        if self.state() != NodeState.UNCHANGED:
            self.cook()
        return [self._parms["file_text"].eval()]