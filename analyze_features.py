import os
import ast
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict, List, Any, Tuple

def get_local_modules(root_dir):
    local_modules = set()
    for root, _, files in os.walk(root_dir):
        if '__pycache__' in root or '.git' in root:
            continue
        rel_path = os.path.relpath(root, root_dir)
        if rel_path == '.':
            module_prefix = ''
        else:
            module_prefix = rel_path.replace(os.sep, '.')
        if module_prefix:
            local_modules.add(module_prefix)
        for file in files:
            if file.endswith('.py'):
                module_name = os.path.splitext(file)[0]
                if module_prefix:
                    local_modules.add(f"{module_prefix}.{module_name}")
                else:
                    local_modules.add(module_name)
    return local_modules

class AdvancedFeatureVisitor(ast.NodeVisitor):
    def __init__(self, local_modules):
        self.local_modules = local_modules
        self.features = defaultdict(set)
        self.imports = defaultdict(set)
        self.current_file = ""
        
    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in {'ABC', 'Protocol'}:
                self.features['abstract_classes'].add(f"{self.current_file}:{node.name}")
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == 'dataclass':
                self.features['dataclasses'].add(f"{self.current_file}:{node.name}")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.features['async_await'].add(f"{self.current_file}:{node.name}")
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if not any(alias.name.startswith(prefix) for prefix in self.local_modules):
                self.imports['direct_imports'].add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and not any(node.module.startswith(prefix) for prefix in self.local_modules):
            for alias in node.names:
                self.imports['from_imports'].add(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_With(self, node):
        if isinstance(node.items[0].context_expr, ast.Call):
            self.features['context_managers'].add(f"{self.current_file}")
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.annotation, ast.Subscript):
            self.features['type_hints'].add(f"{self.current_file}")
        self.generic_visit(node)

def analyze_directory(directory: str) -> Tuple[Dict, Dict]:
    local_modules = get_local_modules(directory)
    visitor = AdvancedFeatureVisitor(local_modules)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Analyzing {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    visitor.current_file = file_path
                    visitor.visit(tree)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return dict(visitor.features), dict(visitor.imports)

def generate_report(features: Dict, imports: Dict, output_file: str):
    with open(output_file, 'w') as f:
        f.write("# Code Analysis Report\n\n")
        
        f.write("## Advanced Python Features\n\n")
        for feature, instances in features.items():
            f.write(f"### {feature.replace('_', ' ').title()}\n")
            for instance in sorted(instances):
                f.write(f"- {instance}\n")
            f.write("\n")
        
        f.write("## External Dependencies\n\n")
        all_imports = set()
        all_imports.update(imports.get('direct_imports', set()))
        all_imports.update(imp.split('.')[0] for imp in imports.get('from_imports', set()))
        
        for imp in sorted(all_imports):
            f.write(f"### {imp}\n")
            from_imports = [i for i in imports.get('from_imports', set()) if i.startswith(imp)]
            if from_imports:
                f.write("Imported components:\n")
                for comp in sorted(from_imports):
                    f.write(f"- {comp}\n")
            f.write("\n")

if __name__ == "__main__":
    directory = "."
    features, imports = analyze_directory(directory)
    generate_report(features, imports, "code_analysis.md")  