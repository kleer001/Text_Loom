import argparse
import ast
import re
from pathlib import Path
from typing import Set, List, Dict, Tuple, TYPE_CHECKING

def find_class_node(tree: ast.AST, class_name: str) -> Tuple[ast.ClassDef, List[ast.Import | ast.ImportFrom]]:
    imports = []
    target_class = None
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)
        elif isinstance(node, ast.ClassDef) and node.name == class_name:
            target_class = node
            
    return target_class, imports

def extract_method_imports(node: ast.ClassDef) -> Set[str]:
    method_imports = set()
    
    for child in ast.walk(node):
        if isinstance(child, ast.Import):
            for alias in child.names:
                method_imports.add(f"import {alias.name}")
        elif isinstance(child, ast.ImportFrom):
            names = [alias.name for alias in child.names]
            method_imports.add(f"from {child.module} import {', '.join(names)}")
            
    return method_imports

def get_required_imports(class_node: ast.ClassDef, imports: List[ast.Import | ast.ImportFrom], source_file: str) -> Tuple[Set[str], bool]:
    required = set()
    has_circular = False
    base_name = Path(source_file).stem
    
    class_visitor = ast.NodeVisitor()
    names_used = set()
    
    def visit_Name(self, node):
        names_used.add(node.id)
    
    class_visitor.visit(class_node)
    
    for imp in imports:
        if isinstance(imp, ast.Import):
            for alias in imp.names:
                if alias.name in names_used:
                    required.add(f"import {alias.name}")
        elif isinstance(imp, ast.ImportFrom):
            if imp.module == base_name:
                has_circular = True
            names = [alias.name for alias in imp.names if alias.name in names_used]
            if names:
                required.add(f"from {imp.module} import {', '.join(names)}")
                
    method_imports = extract_method_imports(class_node)
    required.update(method_imports)
    
    return required, has_circular

def process_file(source_file: str, class_name: str, execute: bool = False):
    with open(source_file) as f:
        content = f.read()
        
    tree = ast.parse(content)
    class_node, imports = find_class_node(tree, class_name)
    
    if not class_node:
        raise ValueError(f"Class {class_name} not found")
        
    required_imports, has_circular = get_required_imports(class_node, imports, source_file)
    
    if has_circular:
        print("Warning: Potential circular import detected")
        
    new_file = f"{class_name.lower()}_class.py"
    new_content = "\n".join([
        *required_imports,
        "",
        ast.unparse(class_node)
    ])
    
    modified_content = content.replace(ast.unparse(class_node), "")
    modified_content = f"from {Path(new_file).stem} import {class_name}\n" + modified_content
    
    print(f"\nNew file ({new_file}) first/last 20 lines:")
    lines = new_content.splitlines()
    if len(lines) > 40:
        print("\n".join(lines[:20]))
        print("...")
        print("\n".join(lines[-20:]))
    else:
        print(new_content)
        
    print(f"\nModified file ({source_file}) first/last 20 lines:")
    lines = modified_content.splitlines()
    if len(lines) > 40:
        print("\n".join(lines[:20]))
        print("...")
        print("\n".join(lines[-20:]))
    else:
        print(modified_content)
        
    if execute:
        with open(new_file, "w") as f:
            f.write(new_content)
        with open(source_file, "w") as f:
            f.write(modified_content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_file", help="Source file containing the class")
    parser.add_argument("class_name", help="Name of class to extract")
    parser.add_argument("-x", "--execute", action="store_true", help="Execute the extraction")
    args = parser.parse_args()
    
    process_file(args.source_file, args.class_name, args.execute)

if __name__ == "__main__":
    main()