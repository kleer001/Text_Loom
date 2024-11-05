import os
import sys
import argparse
import ast
from pathlib import Path
from termcolor import colored

def get_project_root(start_path):
    print(f"Searching for project root starting from: {start_path}")
    current = Path(start_path).resolve()
    while current != current.parent:
        if (current / '.git').exists() or (current / 'setup.py').exists():
            print(f"Project root found: {current}")
            return current
        current = current.parent
    print("Project root not found")
    return None

def should_ignore(path):
    ignore_patterns = ['__pycache__', '.venv', '.git']
    return any(pattern in path for pattern in ignore_patterns)

def create_file_map(project_root):
    file_map = {}
    src_dir = project_root / 'src'
    for root, dirs, files in os.walk(src_dir):
        if root == str(src_dir):
            continue
        for file in files:
            if file.endswith('.py'):
                module_path = os.path.relpath(os.path.join(root, file), src_dir)
                module_name = os.path.splitext(module_path)[0].replace(os.path.sep, '.')
                file_map[file] = module_name
    return file_map

def get_full_import_path(import_name, file_map):
    for file, path in file_map.items():
        if file == f"{import_name}.py" or path.endswith(f".{import_name}"):
            return path
    return import_name  # Return original if not found

def fix_imports(file_path, project_root, file_map, auto_fix=False):
    print(f"Processing file: {file_path}")
    with open(file_path, 'r') as file:
        content = file.read()

    tree = ast.parse(content)
    imports_to_change = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                full_path = get_full_import_path(alias.name, file_map)
                if full_path != alias.name:
                    imports_to_change.append((f"import {alias.name}", f"import {full_path}"))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                full_path = get_full_import_path(node.module, file_map)
                if full_path != node.module:
                    old_import = f"from {node.module} import {', '.join(n.name for n in node.names)}"
                    new_import = f"from {full_path} import {', '.join(n.name for n in node.names)}"
                    imports_to_change.append((old_import, new_import))

    if not imports_to_change:
        print("No imports to change in this file")
        return

    print(f"\nFile: {file_path}")
    for old_import, new_import in imports_to_change:
        print(f"Change:\n  {old_import}\nTo:\n  {colored(new_import, 'red')}")

    if auto_fix:
        apply_changes = True
    else:
        response = input("Apply these changes? (yes/no/quit): ").lower()
        if response == 'quit':
            sys.exit(0)
        apply_changes = response == 'yes'

    if apply_changes:
        for old_import, new_import in imports_to_change:
            content = content.replace(old_import, new_import)
        
        with open(file_path, 'w') as file:
            file.write(content)
        print("Changes applied.")

def main(directory, auto_fix):
    print(f"Starting to process directory: {directory}")
    project_root = get_project_root(directory)
    if not project_root:
        print("Could not determine project root. Exiting.")
        return

    file_map = create_file_map(project_root)
    print("File map created:")
    for file, path in file_map.items():
        print(f"  {file}: {path}")

    for root, dirs, files in os.walk(directory):
        print(f"Scanning directory: {root}")
        dirs[:] = [d for d in dirs if not should_ignore(d)]
        for file in files:
            if file.endswith('.py'):
                fix_imports(os.path.join(root, file), project_root, file_map, auto_fix)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix relative imports in Python files.")
    parser.add_argument("-path", required=True, help="Path to the directory to process")
    parser.add_argument("-auto", action="store_true", help="Automatically fix all files without prompting")
    args = parser.parse_args()
    print(f"Received path argument: {args.path}")
    print(f"Auto-fix mode: {'Enabled' if args.auto else 'Disabled'}")
    main(args.path, args.auto)
