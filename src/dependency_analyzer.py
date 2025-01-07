import os
import ast
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ImportInfo:
    from_imports: Dict[str, Set[str]]
    file_defines: Set[str]
    imported_by: Set[str]
    has_star_import: bool
    has_wholesale_import: bool

class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.from_imports = defaultdict(set)
        self.file_defines = set()
        self.imported_by = set()
        self.has_star_import = False
        self.has_wholesale_import = False
        
    def visit_ClassDef(self, node):
        self.file_defines.add(node.name)
        self.generic_visit(node)
            
    def visit_FunctionDef(self, node):
        self.file_defines.add(node.name)
        self.generic_visit(node)
            
    def visit_Import(self, node):
        for name in node.names:
            self.has_wholesale_import = True
            self.imported_by.add(name.asname or name.name)
            
    def visit_ImportFrom(self, node):
        module = node.module if node.module else ''
        for name in node.names:
            if name.name == '*':
                self.has_star_import = True
            else:
                self.from_imports[module].add(name.asname or name.name)
                if module:
                    self.imported_by.add(module.split('.')[-1])

def analyze_file(file_path: Path) -> Optional[ImportInfo]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            analyzer = ImportAnalyzer()
            analyzer.visit(tree)
            return ImportInfo(
                from_imports=analyzer.from_imports,
                file_defines=analyzer.file_defines,
                imported_by=analyzer.imported_by,
                has_star_import=analyzer.has_star_import,
                has_wholesale_import=analyzer.has_wholesale_import
            )
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def find_circular_imports(base_file_info: ImportInfo, 
                         dependency_map: Dict[str, ImportInfo],
                         base_module: str) -> List[Tuple[str, str, str]]:
    circular_imports = []
    
    for file_path, info in dependency_map.items():
        imported_items = set()
        for module, imports in info.from_imports.items():
            if base_module in module:
                imported_items.update(imports)
                
        if imported_items:
            file_stem = Path(file_path).stem
            if file_stem in base_file_info.imported_by:
                for item in imported_items:
                    circular_imports.append((item, file_path, file_stem))
                    
    return circular_imports

def analyze_directory(start_dir: Path, base_file: Path) -> Dict[str, ImportInfo]:
    dependency_map = {}
    
    for file_path in start_dir.rglob("*.py"):
        if file_path == base_file:
            continue
            
        import_info = analyze_file(file_path)
        if import_info:
            relative_path = file_path.relative_to(start_dir)
            dependency_map[str(relative_path)] = import_info
            
    return dependency_map

def analyze_and_report(directory: str, base_file: str) -> None:
    dir_path = Path(directory)
    base_path = Path(base_file)
    
    if not dir_path.exists() or not base_path.exists():
        print(f"Directory or base file does not exist!")
        return
        
    base_module = base_path.stem
    print(f"\nAnalyzing dependencies for {base_path.name}...\n")
    
    base_file_info = analyze_file(base_path)
    if not base_file_info:
        return
        
    dependency_map = analyze_directory(dir_path, base_path)
    circular_imports = find_circular_imports(base_file_info, dependency_map, base_module)
    
    import_counts = defaultdict(int)
    for info in dependency_map.values():
        for module, imports in info.from_imports.items():
            if base_module in module:
                for item in imports:
                    import_counts[item] += 1
                    
    #We don't really need to know all the bits we're looking at 
    # print("=== Base File Analysis ===")
    # print(f"\nDefined in {base_path.name}:")
    # for item in sorted(base_file_info.file_defines):
    #     print(f"- {item}")
        
    print("\n=== Circular Import Analysis ===")
    if circular_imports:
        print("\nWarning: Found circular dependencies:")
        for item, file_path, imported_by in sorted(circular_imports):
            print(f"- {item} is imported by {file_path}")
            print(f"  BUT {base_path.name} imports from {imported_by}")
    else:
        print("\nNo circular dependencies found.")
    
    print("\n=== Import Usage Statistics ===")
    if import_counts:
        for item, count in sorted(import_counts.items(), key=lambda x: (-x[1], x[0])):
            print(f"- {item}: {count} file{'s' if count != 1 else ''}")
    else:
        print("\nNo imports found from the specified base file.")

def main():
    parser = argparse.ArgumentParser(description='Analyze Python project dependencies')
    parser.add_argument('directory', help='Root directory to start analysis from')
    parser.add_argument('base_file', help='Path to base file to analyze')
    args = parser.parse_args()
    
    analyze_and_report(args.directory, args.base_file)

if __name__ == "__main__":
    main()