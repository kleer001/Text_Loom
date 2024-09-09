import os
import hashlib
import time
from typing import List, Dict, Any
from base_classes import Node, NodeType, NodeState
from parm import Parm, ParameterType

class FileInNode(Node):
    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.FILE_IN)
        self._is_time_dependent = True
        self._file_hash = None

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "file_name": Parm("file_name", ParameterType.STRING, self),
            "file_text": Parm("file_text", ParameterType.STRING, self),
            "file_system_path": Parm("file_system_path", ParameterType.STRING, self),
            "refresh": Parm("refresh", ParameterType.BUTTON, self)
        }

        # Set default values
        self._parms["file_name"].set("input.txt")
        self._parms["file_text"].set("")
        self._parms["file_system_path"].set(os.getcwd())  # Default to current working directory

        # Set up refresh button callback
        self._parms["refresh"].set_script_callback("self.node().refresh()")

    def get_full_file_path(self) -> str:
        file_system_path = str(self._parms["file_system_path"].eval())
        file_name = str(self._parms["file_name"].eval())
        fullfilepath = os.path.join(file_system_path, file_name)
        print("Full combined path is ", fullfilepath)
        return fullfilepath

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

        if not self.validate_parameters(): #rabid checks
            self.set_state(NodeState.UNCOOKED)
            return

        print(f"file_system_path: {self._parms['file_system_path'].eval()}")
        print(f"file_name: {self._parms['file_name'].eval()}")

        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            full_file_path = self.get_full_file_path()
            print(f"Attempting to read file: {full_file_path}")  # Debug print

            if not os.path.isfile(full_file_path):
                raise FileNotFoundError(f"Not a file or file not found: {full_file_path}")

            if not os.path.exists(full_file_path):
                raise FileNotFoundError(f"File not found: {full_file_path}")

            with open(full_file_path, 'r') as file:
                content = file.read()

            new_hash = self._calculate_file_hash(content)

            if force or new_hash != self._file_hash:
                self._parms["file_text"].set(content)
                self._file_hash = new_hash
                self.set_state(NodeState.UNCHANGED)
            else:
                self.set_state(NodeState.UNCHANGED)

            print(f"Successfully read file. Content length: {len(content)}")  # Debug print

        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            if isinstance(e, FileNotFoundError):
                error_msg += f"\nCheck if '{self._parms['file_name'].eval()}' exists in '{self._parms['file_system_path'].eval()}'"
            self.add_error(error_msg)
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