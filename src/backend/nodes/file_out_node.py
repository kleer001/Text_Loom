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
            "save": Parm("save", ParameterType.BUTTON, self)
        }

        # Set default values
        self._parms["file_name"].set("output.txt")
        self._parms["file_text"].set("")

        # Set up save button callback
        self._parms["save"].set_script_callback("self.node().save()")

    def input_names(self) -> Dict[str, str]:
        return {"input": "Input Text"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "File Content"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            input_data = self.inputs()[0].eval()
            content = "\n".join(input_data)
            self._parms["file_text"].set(content)

            file_name = self._parms["file_name"].eval()
            file_path = os.path.join(os.path.dirname(self.path()), file_name)

            new_hash = self._calculate_file_hash(content)

            if force or new_hash != self._file_hash:
                with open(file_path, 'w') as file:
                    file.write(content)
                self._file_hash = new_hash
                self.set_state(NodeState.UNCHANGED)
            else:
                self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error writing file: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds

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