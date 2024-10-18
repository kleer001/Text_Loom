import os
import ast
from datetime import datetime
import sys

def is_loose_function(node):
    return isinstance(node, ast.FunctionDef) and not isinstance(node.parent, ast.ClassDef)

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.objects = 0
        self.methods = 0
        self.loose_functions = 0
        self.unique_imports = set()

    def visit_ClassDef(self, node):
        self.objects += 1
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.methods += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if is_loose_function(node):
            self.loose_functions += 1

    def visit_Import(self, node):
        for alias in node.names:
            module = alias.name.split('.')[0]
            if module in sys.builtin_module_names:
                self.unique_imports.add(module)

    def visit_ImportFrom(self, node):
        if node.level == 0:  # not a relative import
            module = node.module.split('.')[0]
            if module in sys.builtin_module_names:
                self.unique_imports.add(module)

def read_file_with_fallback_encoding(file_path):
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
    total_size = 0
    total_lines = 0
    total_comment_lines = 0
    earliest_timestamp = float('inf')
    latest_timestamp = 0
    analyzer = CodeAnalyzer()

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # File stats
                file_stats = os.stat(file_path)
                total_size += file_stats.st_size
                earliest_timestamp = min(earliest_timestamp, file_stats.st_ctime)
                latest_timestamp = max(latest_timestamp, file_stats.st_mtime)

                content = read_file_with_fallback_encoding(file_path)
                if content is None:
                    continue

                # Line counts
                lines = content.split('\n')
                total_lines += len(lines)
                total_comment_lines += sum(1 for line in lines if line.strip().startswith('#'))

                # AST analysis
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        node.parent = None
                    for node in ast.walk(tree):
                        for child in ast.iter_child_nodes(node):
                            child.parent = node
                    analyzer.visit(tree)
                except SyntaxError:
                    print(f"Warning: Syntax error in {file_path}. Skipping AST analysis for this file.")

    # Calculate time difference
    time_diff = (latest_timestamp - earliest_timestamp) / (24 * 3600)  # Convert to days

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
        'unique_imports': len(analyzer.unique_imports)
    }

if __name__ == "__main__":
    current_dir = os.getcwd()
    results = analyze_python_files(current_dir)

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