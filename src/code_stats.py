"""
Calculate statistics about Python files in a directory.

This function calculates several statistics about Python files in a given directory, including total size of all files, total lines in all files, and more specific information for code objects (objects, methods, loose functions) such as unique imports.

Args:
    directory (str): The path to the root directory to analyze.

Returns:
    dict: A dictionary containing various statistics about Python files. It includes:
        'earliest_timestamp': datetime object representing the earliest timestamp among all Python files.
        'latest_timestamp': datetime object representing the latest timestamp among all Python files.
        'time_diff_days': float, representing the difference in days between the earliest and latest timestamps.
        'total_size_kb': float, representing the total size of all Python files in kilobytes.
        'total_lines': int, representing the total number of lines in all Python files.
        'total_comment_lines': int, representing the total number of comment lines in all Python files.
        'total_objects': int, representing the total number of code objects (classes and methods).
        'total_methods': int, representing the total number of methods.
        'total_loose_functions': int, representing the total number of loose functions.
        'unique_imports': int, representing the number of unique built-in packages imported in all Python files.
        'python_file_count': int, representing the total number of Python files in the directory and its subdirectories.

Raises:
    FileNotFoundError: If the given path does not exist or is not a directory.
"""
import os
import ast
from datetime import datetime
import sys

def is_loose_function(node):
    return isinstance(node, ast.FunctionDef) and not isinstance(node.parent, ast.ClassDef)

class CodeAnalyzer(ast.NodeVisitor):
    """
    A visitor class for Python code that calculates statistics about code objects (objects, methods, loose functions).

    Args:
        None.

    Returns:
        None.
    """
    def __init__(self):
        """Initialize the CodeAnalyzer."""
        self.objects = 0
        self.methods = 0
        self.loose_functions = 0
        self.unique_imports = set()

    def visit_ClassDef(self, node):
        """Visit a ClassDef node in the AST and update statistics."""
        self.objects += 1
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.methods += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit a FunctionDef node in the AST and update statistics."""
        if is_loose_function(node):
            self.loose_functions += 1

    def visit_Import(self, node):
        """Visit an Import node in the AST to track unique built-in packages."""
        for alias in node.names:
            module = alias.name.split('.')[0]
            if module in sys.builtin_module_names:
                self.unique_imports.add(module)

    def visit_ImportFrom(self, node):
        """Visit an ImportFrom node in the AST to track unique built-in packages."""
        if node.level == 0:  # not a relative import
            module = node.module.split('.')[0]
            if module in sys.builtin_module_names:
                self.unique_imports.add(module)

def read_file_with_fallback_encoding(file_path):
    """
    Read a Python file with a fallback encoding.

    Args:
        file_path (str): The path to the Python file to read.

    Returns:
        str or None: The content of the file if successful, otherwise None.
    """
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    print(f"Warning: Unable to decode {file_path} with any of the attempted encodings. Skipping this file.")
    return None

def analyze_python_files(directory):
    """
    Analyze Python files in a directory, calculating statistics about each.

    Args:
        directory (str): The path to the root directory to analyze.

    Returns:
        dict: A dictionary containing various statistics about Python files. See the docstring for details.
    """
    total_size = 0
    total_lines = 0
    total_comment_lines = 0
    earliest_timestamp = float('inf')
    latest_timestamp = 0
    analyzer = CodeAnalyzer()
    python_file_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_file_count += 1
                file_path = os.path.join(root, file)

                file_stats = os.stat(file_path)
                total_size += file_stats.st_size
                earliest_timestamp = min(earliest_timestamp, file_stats.st_ctime)
                latest_timestamp = max(latest_timestamp, file_stats.st_mtime)

                content = read_file_with_fallback_encoding(file_path)
                if content is None:
                    continue

                lines = content.split('\n')
                total_lines += len(lines)
                total_comment_lines += sum(1 for line in lines if line.strip().startswith('#'))

                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        node.parent = None
                    for node in ast.walk(tree):
                        for child in ast.iter_child_nodes(node):
                            child.parent = node
                    analyzer.visit(tree)
                except SyntaxError:
                    pass

    time_diff = (latest_timestamp - earliest_timestamp) / (24 * 3600)

    return {
        'earliest_timestamp': datetime.fromtimestamp(earliest_timestamp),
        'latest_timestamp': datetime.fromtimestamp(latest_timestamp),
        'time_diff_days': time_diff,
        'total_size_kb': total_size / 1024,
        'total_lines': total_lines,
        'total_comment_lines': total_comment_lines,
        'total_objects': analyzer.objects,
        'total_methods': analyzer.methods,
        'total_loose_functions': analyzer.loose_functions,
        'unique_imports': len(analyzer.unique_imports),
        'python_file_count': python_file_count
    }

if __name__ == "__main__":
    current_dir = os.getcwd()
    results = analyze_python_files(current_dir)
    print(f"Total number of Python files: {results['python_file_count']}")
    print(f"Earliest timestamp: {results['earliest_timestamp']}")
    print(f"Latest timestamp: {results['latest_timestamp']}")
    print(f"Time difference: {results['time_diff_days']:.2f} days")
    print(f"Total size of all files: {results['total_size_kb']:.2f} KB")
    print(f"Total lines in all files: {results['total_lines']}")
    print(f"Total comment lines: {results['total_comment_lines']}")
    print(f"Total number of objects: {results['total_objects']}")
    print(f"Total number of methods: {results['total_methods']}")
    print(f"Total number of loose functions: {results['total_loose_functions']}")
    print(f"Total number of unique built-in packages used: {results['unique_imports']}")