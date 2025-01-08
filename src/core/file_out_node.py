import os
import codecs
import re
import hashlib
import time
import ast
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType


class FileOutNode(Node):

    """
    Write the given content to a text file. The function provides a refresh button to force the write.

    The hash check helps to determine whether the file needs to be written again. If the hash of the input content matches the previously recorded hash and `force_write` is False, the function will skip writing the file.

    Parameters:
        filename (str): The name of the file to write to.
        content (list of str): A list of strings to be written to the file.
        refresh (button): Force the file to be written regardless of content changes or hash matching. Default is False.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """

    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.FILE_OUT)
        self._is_time_dependent = True
        self._file_hash = None

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "file_name": Parm("file_name", ParameterType.STRING, self),
            "file_text": Parm("file_text", ParameterType.STRING, self),
            "refresh": Parm("refresh", ParameterType.BUTTON, self),
            "format_output": Parm("format_output", ParameterType.TOGGLE, self),
        }

        # Set default values
        self._parms["file_name"].set("./output.txt")
        self._parms["file_text"].set("")
        self._parms["format_output"].set(True)
        # Set up refresh button callback
        self._parms["refresh"].set_script_callback("self.node().refresh()")



    ESCAPE_SEQUENCE_RE = re.compile(r'''
        ( \\U........      # 8-digit hex escapes
        | \\u....          # 4-digit hex escapes
        | \\x..            # 2-digit hex escapes
        | \\[0-7]{1,3}     # Octal escapes
        | \\N\{[^}]+\}     # Unicode characters by name
        | \\[\\'"abfnrtv]  # Single-character escapes
        )''', re.UNICODE | re.VERBOSE)

    def decode_escapes(self, s: str):
        def decode_match(match):
            try:
                return codecs.decode(match.group(0), 'unicode-escape')
            except UnicodeDecodeError:
                # In case we matched the wrong thing after a double-backslash
                return match.group(0)

        return ESCAPE_SEQUENCE_RE.sub(decode_match, s)

    def _internal_cook(self, force: bool = False) -> None:
        
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            # Check if we have any inputs
            if not self.inputs():
                raise ValueError("No input connected to FileOutNode")

            input_data = self.inputs()[0].output_node().eval(requesting_node=self)
            #print(f"Debug: Input data received: {input_data}")

            if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
                raise TypeError("Input data must be a list of strings")

            content = "\n\n\n".join(input_data)
            if (self._parms["format_output"].eval()):
                content = content.replace("[", "").replace("]", "")
                content = content.encode('utf-8').decode('unicode_escape')

            self._parms["file_text"].set(content)
            self._output = content
            full_file_path = self._parms["file_name"].eval()

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

    # def eval(self) -> List[str]:
    #     if self.state() != NodeState.UNCHANGED:
    #         self.cook()
    #     return [self._parms["file_text"].eval()]