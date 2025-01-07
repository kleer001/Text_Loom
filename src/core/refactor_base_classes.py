import ast
import astor
import os
from typing import Dict, Set, List, Optional
from collections import defaultdict

class ClassDependencyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.current_class = None
        self.dependencies = defaultdict(set)
        self.imports = defaultdict(set)
        self.class_defs = {}
        self.enums = set()
        self.class_source = {}
        
    def visit_ClassDef(self, node):
        self.current_class = node.name
        # Store the full class definition
        self.class_defs[node.name] = node
        # Check if it's an Enum
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'Enum':
                self.enums.add(node.name)
        # Get the source code for this class
        self.class_source[node.name] = astor.to_source(node)
        # Visit all child nodes
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if self.current_class and isinstance(node.ctx, ast.Load):
            if node.id in self.class_defs and node.id != self.current_class:
                self.dependencies[self.current_class].add(node.id)

def organize_classes(source_file: str, output_dir: str):
    # Read the source file
    with open(source_file, 'r') as f:
        source = f.read()
    
    # Parse the AST
    tree = ast.parse(source)
    
    # Analyze dependencies
    analyzer = ClassDependencyAnalyzer()
    analyzer.visit(tree)
    
    # Create mapping of classes to their new files
    class_to_file = {}
    for class_name in analyzer.class_defs:
        if class_name in analyzer.enums:
            module_name = 'enums'
        else:
            # Convert CamelCase to snake_case
            module_name = ''.join(['_' + c.lower() if c.isupper() else c 
                                 for c in class_name]).lstrip('_')
        class_to_file[class_name] = f"{module_name}.py"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate new files
    for class_name, file_name in class_to_file.items():
        # Get the class dependencies
        deps = analyzer.dependencies[class_name]
        
        # Build import statements
        imports = set()
        for dep in deps:
            if dep in class_to_file:
                module_name = os.path.splitext(class_to_file[dep])[0]
                imports.add(f"from .{module_name} import {dep}")
        
        # Add TYPE_CHECKING imports for circular dependencies
        circular_imports = set()
        for dep in deps:
            if dep in analyzer.dependencies and class_name in analyzer.dependencies[dep]:
                imports.remove(f"from .{os.path.splitext(class_to_file[dep])[0]} import {dep}")
                circular_imports.add(f"    from .{os.path.splitext(class_to_file[dep])[0]} import {dep}")
        
        # Build the file content
        content = []
        
        # Add original imports from source
        content.extend([
            "from abc import ABC, abstractmethod",
            "from enum import Enum, auto",
            "from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING"
        ])
        
        # Add regular imports
        content.extend(sorted(imports))
        
        # Add circular imports if any
        if circular_imports:
            content.extend([
                "",
                "if TYPE_CHECKING:",
                *sorted(circular_imports)
            ])
        
        # Add the class definition
        content.append("\n" + analyzer.class_source[class_name])
        
        # Write the file
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'w') as f:
            f.write('\n'.join(content))
        
        print(f"Created {output_path}")

if __name__ == "__main__":
    organize_classes("base_classes.py", "core")