import os
import hashlib
import time
from typing import List, Dict, Any
from base_classes import Node, NodeType, NodeState
from parm import Parm, ParameterType


class FileOutNode(Node):
    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.FILE_OUT)
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
        self._parms["file_name"].set("output.txt")
        self._parms["file_text"].set("")
        self._parms["file_system_path"].set(os.getcwd())  # Default to current working directory

        # Set up refresh button callback
        self._parms["refresh"].set_script_callback("self.node().refresh()")

    def get_full_file_path(self) -> str:
        file_system_path = self._parms["file_system_path"].eval()
        file_name = self._parms["file_name"].eval()
        return os.path.join(file_system_path, file_name)

    def cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            # Check if we have any inputs
            if not self.inputs():
                raise ValueError("No input connected to FileOutNode")

            input_data = self.inputs()[0].output_node().eval()
            if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
                raise TypeError("Input data must be a list of strings")

            content = "\n".join(input_data)
            self._parms["file_text"].set(content)

            full_file_path = self.get_full_file_path()

            new_hash = self._calculate_file_hash(content)

            if force or new_hash != self._file_hash:
                os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                with open(full_file_path, 'w') as file:
                    file.write(content)
                self._file_hash = new_hash
                print(f"File written successfully: {full_file_path}")
                self.set_state(NodeState.UNCHANGED)
            else:
                print(f"File content unchanged: {full_file_path}")
                self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error writing file: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds


    def input_names(self) -> Dict[str, str]:
        return {"input": "Input Text"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "File Content"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def save(self) -> None:
        self.cook(force=True)

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            input_data = self.inputs()[0].eval()
            content = "\n".join(input_data)
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