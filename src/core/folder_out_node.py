import os
import hashlib
import time
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.enums import FunctionalGroup


class FolderOutNode(Node):
    """Writes input list items as separate files into a specified folder.

    This node takes a list of strings and writes each item as an individual file
    in the target directory. Perfect for batch processing workflows that need to
    split processed data into multiple output files. File naming supports both
    sequential numbering and custom patterns.

    Attributes:
        folder_path (str): The directory path where files will be written.
                          Creates the directory if it doesn't exist.
        filename_pattern (str): Template for output filenames. Supports:
                               - `{index}` - Sequential number (0-based)
                               - `{count}` - Sequential number (1-based)
                               - `{input}` - First 20 chars of content (sanitized)
                               Default: "output_{count}.txt"
        file_extension (str): File extension for all outputs. Default: ".txt"
        overwrite (bool): When True, overwrites existing files. When False,
                         appends numeric suffix to avoid collisions. Default: False
        refresh (button): Forces all files to be written, regardless of hash checks.
        format_output (bool): When True (default), writes raw string content.
                             When False, preserves Python list format for each item.

    Example:
        Input: `["First document", "Second document", "Third document"]`

        With `filename_pattern="doc_{count}"` and `file_extension=".txt"`:
        Creates:
            - folder_path/doc_1.txt  (contains: "First document")
            - folder_path/doc_2.txt  (contains: "Second document")
            - folder_path/doc_3.txt  (contains: "Third document")

        With `filename_pattern="output_{input}"`:
        Creates:
            - folder_path/output_First_document.txt
            - folder_path/output_Second_document.txt
            - folder_path/output_Third_document.txt

    Note:
        **Input:**
        *   `List[str]`: A list of strings, where each item becomes a separate file.

        **Output:**
        *   `List[str]`: A list of file paths for the created files.

        **Hash-based optimization:** Files are only written if content has changed
        since the last cook, unless `refresh` is triggered or `force=True`.

        **Collision handling:** When `overwrite=False` (default), existing files
        are preserved by appending "_1", "_2", etc. to the filename.
    """

    GLYPH = '📂'
    GROUP = FunctionalGroup.FILE
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = True
        self._file_hashes: Dict[str, str] = {}

        self._parms.update({
            "folder_path": Parm("folder_path", ParameterType.STRING, self),
            "filename_pattern": Parm("filename_pattern", ParameterType.STRING, self),
            "file_extension": Parm("file_extension", ParameterType.STRING, self),
            "overwrite": Parm("overwrite", ParameterType.TOGGLE, self),
            "refresh": Parm("refresh", ParameterType.BUTTON, self),
            "format_output": Parm("format_output", ParameterType.TOGGLE, self),
        })

        self._parms["folder_path"].set("./output")
        self._parms["filename_pattern"].set("output_{count}.txt")
        self._parms["file_extension"].set(".txt")
        self._parms["overwrite"].set(False)
        self._parms["format_output"].set(True)
        self._parms["refresh"].set_script_callback("self.node().refresh()")

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            input_data = []
            if self.inputs():
                input_data = self.inputs()[0].output_node().eval(requesting_node=self)
                if not isinstance(input_data, list):
                    self.add_error("Input must be a list of strings")
                    self.set_state(NodeState.UNCOOKED)
                    return

            folder_path = self._parms["folder_path"].eval()
            overwrite = self._parms["overwrite"].eval()

            os.makedirs(folder_path, exist_ok=True)

            output_paths: List[str] = []

            for index, item in enumerate(input_data):
                if not isinstance(item, str):
                    item = str(item)

                filename = self._generate_filename(item, index)
                base_path = os.path.join(folder_path, filename)
                final_path = self._find_unique_filename(base_path) if not overwrite else base_path

                content_hash = self._calculate_file_hash(item)
                needs_write = force or final_path not in self._file_hashes or self._file_hashes[final_path] != content_hash

                if needs_write:
                    with open(final_path, 'w', encoding='utf-8') as f:
                        f.write(item)
                    self._file_hashes[final_path] = content_hash

                output_paths.append(final_path)

            self._output = output_paths
            self.set_state(NodeState.UNCHANGED)

        except PermissionError as e:
            self.add_error(f"Permission denied when writing files: {e}")
            self.set_state(NodeState.UNCOOKED)
        except OSError as e:
            self.add_error(f"OS error when writing files: {e}")
            self.set_state(NodeState.UNCOOKED)
        except Exception as e:
            self.add_error(f"Unexpected error: {e}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000

    def _generate_filename(self, content: str, index: int) -> str:
        filename_pattern = self._parms["filename_pattern"].eval()
        file_extension = self._parms["file_extension"].eval()

        filename = filename_pattern.replace("{index}", str(index))
        filename = filename.replace("{count}", str(index + 1))
        filename = filename.replace("{input}", self._sanitize_filename(content[:20]))

        if not filename.endswith(file_extension):
            filename += file_extension

        return filename

    def _sanitize_filename(self, text: str) -> str:
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = text
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '')
        sanitized = sanitized.replace(' ', '_')
        sanitized = sanitized.strip()
        sanitized = sanitized.strip('.')
        return sanitized if sanitized else "unnamed"

    def _find_unique_filename(self, base_path: str) -> str:
        overwrite = self._parms["overwrite"].eval()

        if overwrite or not os.path.exists(base_path):
            return base_path

        base, ext = os.path.splitext(base_path)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1

        return f"{base}_{counter}{ext}"

    def _calculate_file_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def input_names(self) -> Dict[int, str]:
        return {0: "Input Text"}

    def output_names(self) -> Dict[int, str]:
        return {0: "File Paths"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True
        if self._is_time_dependent:
            return True
        try:
            folder_path = self._parms["folder_path"].raw_value()
            filename_pattern = self._parms["filename_pattern"].raw_value()
            file_extension = self._parms["file_extension"].raw_value()
            overwrite = self._parms["overwrite"].raw_value()

            param_hash = self._calculate_file_hash(
                f"{folder_path}{filename_pattern}{file_extension}{overwrite}"
            )

            if self.inputs():
                input_data = self.inputs()[0].output_node().get_output()
                input_hash = self._calculate_file_hash(str(input_data))

                if not hasattr(self, '_last_param_hash') or not hasattr(self, '_last_input_hash'):
                    self._last_param_hash = param_hash
                    self._last_input_hash = input_hash
                    return True

                if param_hash != self._last_param_hash or input_hash != self._last_input_hash:
                    self._last_param_hash = param_hash
                    self._last_input_hash = input_hash
                    return True

            return False
        except Exception:
            return True
