import os
import ast
from pathlib import Path
from collections import defaultdict

def find_imports(directory='.'):
    imports = defaultdict(set)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = Path(root) / file
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                imports[path].add(name.name)
                        elif isinstance(node, ast.ImportFrom):
                            module = node.module if node.module else ''
                            for name in node.names:
                                full_name = f"{module}.{name.name}" if module else name.name
                                imports[path].add(full_name)
                except Exception as e:
                    print(f"Error processing {path}: {e}")
    
    return imports

def print_unique_imports():
    imports = find_imports('src')
    all_imports = set()
    
    for file_imports in imports.values():
        all_imports.update(file_imports)
    
    std_lib = set(i for i in all_imports if '.' not in i)
    third_party = set(i.split('.')[0] for i in all_imports if '.' in i)
    
    print("\nStandard Library Imports:")
    for imp in sorted(std_lib):
        print(f"  {imp}")
        
    print("\nThird Party Imports:")
    for imp in sorted(third_party):
        print(f"  {imp}")

if __name__ == '__main__':
    print_unique_imports()