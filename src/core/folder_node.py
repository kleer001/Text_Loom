import os
import re
import glob
import time
from typing import List, Dict, Any, Tuple
from pathlib import Path
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType


class FolderNode(Node):
    """Scans directories and reads text file contents matching specified criteria.

    Enables batch file processing workflows by scanning directories, filtering
    files based on various criteria, and reading their contents. This node is
    ideal for processing entire directories of text files through LLM pipelines
    without manually specifying each file.

    Attributes:
        folder_path (str): Path to the directory to scan.
        pattern (str): Filename matching pattern (supports wildcards and regex).
        recursive (bool): If True, includes subdirectories in the search.
        sort_by (str): Sorting method ("name", "date", "size", etc.).
        max_files (int): Maximum number of files to return (0 for unlimited).
        min_size (int): Minimum file size in bytes (0 for no minimum).
        max_size (int): Maximum file size in bytes (0 for no maximum).
        include_hidden (bool): If True, includes hidden files (starting with '.').
        follow_symlinks (bool): If True, follows symbolic links during traversal.
        on_error (str): Error handling method ("warn", "skip", "stop").
        enabled (bool): Enable or disable the node's functionality.

    Example:
        Basic scan:
            folder_path = "./fables/"
            pattern = "*.txt"
            Output[0]: ["content1...", "content2..."]
            Output[1]: ["./fables/fable_001.txt", "./fables/fable_002.txt"]
            Output[2]: ["", ""]

        With errors (if fable_002.txt is unreadable):
            Output[2]: ["", "Permission denied: ./fables/fable_002.txt"]

    Note:

        **Outputs:**
        *   Output[0] (List[str]): List of file contents.
        *   Output[1] (List[str]): List of file names (paths).
        *   Output[2] (List[str]): List of errors per file (empty string if successful).
    """

    GLYPH = '📁'
    SINGLE_INPUT = False
    SINGLE_OUTPUT = False

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._last_scan_hash = None

        # Initialize parameters
        self._parms.update({
            "folder_path": Parm("folder_path", ParameterType.STRING, self),
            "pattern": Parm("pattern", ParameterType.STRING, self),
            "recursive": Parm("recursive", ParameterType.TOGGLE, self),
            "sort_by": Parm("sort_by", ParameterType.MENU, self),
            "max_files": Parm("max_files", ParameterType.INT, self),
            "min_size": Parm("min_size", ParameterType.INT, self),
            "max_size": Parm("max_size", ParameterType.INT, self),
            "include_hidden": Parm("include_hidden", ParameterType.TOGGLE, self),
            "follow_symlinks": Parm("follow_symlinks", ParameterType.TOGGLE, self),
            "on_error": Parm("on_error", ParameterType.MENU, self),
        })

        # Set default values
        self._parms["folder_path"].set("./")
        self._parms["pattern"].set("*.*")
        self._parms["recursive"].set(False)

        # Set MENU parameters (pass dictionary to set up menu options)
        self._parms["sort_by"].set({
            "name": "Name (A-Z)",
            "name_desc": "Name (Z-A)",
            "date": "Date (Oldest First)",
            "date_desc": "Date (Newest First)",
            "size": "Size (Smallest First)",
            "size_desc": "Size (Largest First)",
            "none": "No Sorting"
        })

        self._parms["max_files"].set(0)
        self._parms["min_size"].set(0)
        self._parms["max_size"].set(0)
        self._parms["include_hidden"].set(False)
        self._parms["follow_symlinks"].set(False)

        # Set MENU parameters (pass dictionary to set up menu options)
        self._parms["on_error"].set({
            "warn": "Warn and Continue",
            "skip": "Skip Silently",
            "stop": "Stop on Error"
        })

    def _sanitize_path(self, path_str: str) -> str:
        """Sanitize path to prevent directory traversal attacks."""
        # Remove potentially dangerous path components
        path = Path(path_str).resolve()
        return str(path)

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the given pattern (wildcard or regex)."""
        # Check if it's a regex pattern (starts with ^)
        if pattern.startswith("^"):
            regex_pattern = pattern[1:]
            try:
                return bool(re.match(regex_pattern, filename))
            except re.error as e:
                self.add_warning(f"Invalid regex pattern '{pattern}': {str(e)}")
                return False
        else:
            # Use glob-style wildcard matching
            return glob.fnmatch.fnmatch(filename, pattern)

    def _scan_directory(self, folder_path: str, pattern: str, recursive: bool,
                       include_hidden: bool, follow_symlinks: bool) -> List[str]:
        """Scan directory and return list of matching file paths."""
        matching_files = []

        try:
            if recursive:
                # Use os.walk for recursive scanning
                for root, dirs, files in os.walk(folder_path,
                                                followlinks=follow_symlinks):
                    # Filter out hidden directories if needed
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]

                    for filename in files:
                        # Skip hidden files if needed
                        if not include_hidden and filename.startswith('.'):
                            continue

                        if self._matches_pattern(filename, pattern):
                            full_path = os.path.join(root, filename)
                            matching_files.append(full_path)
            else:
                # Non-recursive: only scan immediate directory
                try:
                    for entry in os.scandir(folder_path):
                        if entry.is_file(follow_symlinks=follow_symlinks):
                            filename = entry.name

                            # Skip hidden files if needed
                            if not include_hidden and filename.startswith('.'):
                                continue

                            if self._matches_pattern(filename, pattern):
                                matching_files.append(entry.path)
                except (PermissionError, OSError) as e:
                    self.add_error(f"Cannot access directory '{folder_path}': {str(e)}")

        except Exception as e:
            self.add_error(f"Error scanning directory: {str(e)}")

        return matching_files

    def _filter_by_size(self, file_paths: List[str], min_size: int,
                       max_size: int) -> List[str]:
        """Filter files by size constraints."""
        filtered = []

        for file_path in file_paths:
            try:
                size = os.path.getsize(file_path)

                if min_size > 0 and size < min_size:
                    continue
                if max_size > 0 and size > max_size:
                    continue

                filtered.append(file_path)
            except OSError:
                # If we can't get size, skip the file
                continue

        return filtered

    def _sort_files(self, file_paths: List[str], sort_by: str) -> List[str]:
        """Sort files according to specified method."""
        if sort_by == "none":
            return file_paths

        try:
            if sort_by == "name":
                return sorted(file_paths)
            elif sort_by == "name_desc":
                return sorted(file_paths, reverse=True)
            elif sort_by == "date":
                return sorted(file_paths, key=lambda x: os.path.getmtime(x))
            elif sort_by == "date_desc":
                return sorted(file_paths, key=lambda x: os.path.getmtime(x),
                            reverse=True)
            elif sort_by == "size":
                return sorted(file_paths, key=lambda x: os.path.getsize(x))
            elif sort_by == "size_desc":
                return sorted(file_paths, key=lambda x: os.path.getsize(x),
                            reverse=True)
            else:
                self.add_warning(f"Unknown sort method '{sort_by}', using 'name'")
                return sorted(file_paths)
        except OSError as e:
            self.add_warning(f"Error during sorting: {str(e)}")
            return file_paths

    def _read_file_contents(self, file_paths: List[str],
                           on_error: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Read contents of files and return contents, names, and errors.

        Returns:
            Tuple of (contents, names, errors)
        """
        contents = []
        names = []
        errors = []

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                contents.append(content)
                names.append(file_path)
                errors.append("")  # No error

            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    contents.append(content)
                    names.append(file_path)
                    errors.append("")
                except Exception as e:
                    error_msg = f"Encoding error: {str(e)}"
                    self._handle_file_error(file_path, error_msg, on_error)
                    contents.append("")
                    names.append(file_path)
                    errors.append(error_msg)

            except PermissionError as e:
                error_msg = f"Permission denied: {file_path}"
                self._handle_file_error(file_path, error_msg, on_error)
                contents.append("")
                names.append(file_path)
                errors.append(error_msg)

            except Exception as e:
                error_msg = f"Error reading file: {str(e)}"
                self._handle_file_error(file_path, error_msg, on_error)
                contents.append("")
                names.append(file_path)
                errors.append(error_msg)

        return contents, names, errors

    def _handle_file_error(self, file_path: str, error_msg: str, on_error: str):
        """Handle file reading errors according to on_error setting."""
        if on_error == "warn":
            self.add_warning(error_msg)
        elif on_error == "stop":
            self.add_error(error_msg)
            raise Exception(error_msg)
        # "skip" mode does nothing - just continues

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            # Check if node is enabled
            if not self._parms["enabled"].eval():
                self._output = [[""], [""], [""]]
                self.set_state(NodeState.UNCHANGED)
                return

            # Get parameters
            folder_path = self._parms["folder_path"].eval()
            pattern = self._parms["pattern"].eval()
            recursive = self._parms["recursive"].eval()
            sort_by = self._parms["sort_by"].eval()
            max_files = self._parms["max_files"].eval()
            min_size = self._parms["min_size"].eval()
            max_size = self._parms["max_size"].eval()
            include_hidden = self._parms["include_hidden"].eval()
            follow_symlinks = self._parms["follow_symlinks"].eval()
            on_error = self._parms["on_error"].eval()

            # Validate and sanitize folder path
            try:
                folder_path = self._sanitize_path(folder_path)
            except Exception as e:
                raise ValueError(f"Invalid folder path: {str(e)}")

            # Check if folder exists
            if not os.path.exists(folder_path):
                raise ValueError(f"Folder does not exist: {folder_path}")

            if not os.path.isdir(folder_path):
                raise ValueError(f"Path is not a directory: {folder_path}")

            # Scan directory for matching files
            matching_files = self._scan_directory(folder_path, pattern, recursive,
                                                 include_hidden, follow_symlinks)

            # Filter by size
            matching_files = self._filter_by_size(matching_files, min_size, max_size)

            # Sort files
            matching_files = self._sort_files(matching_files, sort_by)

            # Limit number of files if max_files > 0
            if max_files > 0:
                matching_files = matching_files[:max_files]

            # Check if any files were found
            if not matching_files:
                self.add_warning(f"No files matching pattern '{pattern}' found in '{folder_path}'")
                self._output = [[""], [""], [""]]
                self.set_state(NodeState.UNCHANGED)
                return

            # Read file contents
            contents, names, errors = self._read_file_contents(matching_files, on_error)

            # If all files had errors and on_error is "stop", we would have raised
            # If we're here, set output with whatever we got
            if not contents:
                contents = [""]
                names = [""]
                errors = [""]

            # Set output
            self._output = [contents, names, errors]
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"FolderNode processing error: {str(e)}")
            self._output = [[""], [""], [str(e)]]
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000

    def input_names(self) -> Dict[int, str]:
        """FolderNode has no inputs."""
        return {}

    def output_names(self) -> Dict[int, str]:
        """Define the three output connections."""
        return {
            0: "File Contents",
            1: "File Names",
            2: "Errors"
        }

    def input_data_types(self) -> Dict[int, str]:
        """FolderNode has no inputs."""
        return {}

    def output_data_types(self) -> Dict[int, str]:
        """All outputs are List[str]."""
        return {
            0: "List[str]",
            1: "List[str]",
            2: "List[str]"
        }