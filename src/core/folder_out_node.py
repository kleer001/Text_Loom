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

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.FOLDER_OUT)
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
            if not self.inputs():
                raise ValueError("No input connected to FolderOutNode")

            input_data = self.inputs()[0].output_node().eval(requesting_node=self)

            if not isinstance(input_data, list):
                raise TypeError("Input data must be a list of strings")

            if not all(isinstance(item, str) for item in input_data):
                raise TypeError("All items in input list must be strings")

            folder_path = self._parms["folder_path"].eval()
            format_output = self._parms["format_output"].eval()

            os.makedirs(folder_path, exist_ok=True)

            output_paths = []

            for index, item in enumerate(input_data):
                filename = self._generate_filename(item, index)
                base_path = os.path.join(folder_path, filename)
                final_path = self._find_unique_filename(base_path)

                if format_output:
                    content = item
                else:
                    content = str([item])

                content_hash = self._calculate_file_hash(content)

                if force or not os.path.exists(final_path) or final_path not in self._file_hashes or self._file_hashes[final_path] != content_hash:
                    with open(final_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self._file_hashes[final_path] = content_hash

                output_paths.append(final_path)

            self._output = output_paths
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error writing files: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000

    def _generate_filename(self, content: str, index: int) -> str:
        pattern = self._parms["filename_pattern"].eval()
        extension = self._parms["file_extension"].eval()

        filename = pattern.replace("{index}", str(index))
        filename = filename.replace("{count}", str(index + 1))

        if "{input}" in filename:
            sanitized_input = self._sanitize_filename(content[:20])
            filename = filename.replace("{input}", sanitized_input)

        if not filename.endswith(extension):
            filename = filename + extension

        if len(filename) > 255:
            name_without_ext = filename[:-len(extension)] if extension else filename
            filename = name_without_ext[:255-len(extension)] + extension

        return filename

    def _sanitize_filename(self, text: str) -> str:
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = text

        for char in invalid_chars:
            sanitized = sanitized.replace(char, '')

        sanitized = sanitized.replace(' ', '_')
        sanitized = sanitized.strip().strip('.')

        if not sanitized:
            sanitized = "file"

        if len(sanitized) > 200:
            sanitized = sanitized[:200]

        return sanitized

    def _find_unique_filename(self, base_path: str) -> str:
        if self._parms["overwrite"].eval():
            return base_path

        if not os.path.exists(base_path):
            return base_path

        directory = os.path.dirname(base_path)
        filename = os.path.basename(base_path)
        name, ext = os.path.splitext(filename)

        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1

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
            if not self.inputs():
                return True

            input_data = self.inputs()[0].output_node().get_output()

            if not isinstance(input_data, list):
                return True

            for index, item in enumerate(input_data):
                if not isinstance(item, str):
                    return True

                filename = self._generate_filename(item, index)
                folder_path = self._parms["folder_path"].eval()
                base_path = os.path.join(folder_path, filename)
                final_path = self._find_unique_filename(base_path)

                format_output = self._parms["format_output"].eval()
                if format_output:
                    content = item
                else:
                    content = str([item])

                content_hash = self._calculate_file_hash(content)

                if not os.path.exists(final_path):
                    return True

                if final_path not in self._file_hashes or self._file_hashes[final_path] != content_hash:
                    return True

            return False

        except Exception:
            return True
