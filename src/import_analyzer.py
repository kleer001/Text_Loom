import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import importlib.util
import sys
from collections import defaultdict
import shutil
from datetime import datetime
import re

class ImportAnalyzerFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.python_files = {}  # Dict[Path, Set[str]]
        self.import_statements = {}  # Dict[Path, List[Tuple[str, str, str]]]
        self.module_map = {}  # Dict[str, Path]
        self.issues = defaultdict(list)  # Dict[Path, List[Dict]]
        self.backup_dir = None
        
    def create_backup(self):
        """Create a backup of all Python files before modifications."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = self.project_root / f'import_backup_{timestamp}'
        self.backup_dir.mkdir(exist_ok=True)
        
        for py_file in self.python_files:
            relative_path = py_file.relative_to(self.project_root)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, backup_path)
            
    def scan_project(self):
        """Scan and categorize project files."""
        # Reset stored data
        self.python_files.clear()
        self.module_map.clear()
        
        component_types = {
            'core': [],
            'gui': [],
            'tui': [],
            'tests': []
        }
        
        for path in self.project_root.rglob("*.py"):
            if any(x in str(path) for x in ["__pycache__", ".venv", "venv", ".env", "env", "trash"]):
                continue
                
            relative_path = path.relative_to(self.project_root)
            module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")
            self.module_map[module_name] = path
            self.python_files[path] = set()
            
            # Categorize file
            path_str = str(relative_path)
            for component in component_types:
                if component in path_str.lower():
                    component_types[component].append(path)
                    break
                    
        return component_types
        
    def check_structure_issues(self, component_types: Dict[str, List[Path]]):
        """Analyze structural issues based on new directory layout."""
        structure_issues = []
        
        # Check core isolation
        for core_file in component_types['core']:
            with open(core_file, 'r') as f:
                content = f.read()
                if any(term in content for term in ['from src.gui', 'from src.tui', 'import src.gui', 'import src.tui']):
                    structure_issues.append({
                        'file': core_file,
                        'type': 'core_dependency',
                        'message': 'Core module should not depend on GUI or TUI modules',
                        'fixable': True
                    })
                    
        # Check for old-style imports
        old_patterns = [
            r'from .*\.frontend\..*',
            r'from .*\.backend\..*',
            r'import .*\.frontend\..*',
            r'import .*\.backend\..*'
        ]
        
        for file_path in self.python_files:
            with open(file_path, 'r') as f:
                content = f.read()
                for pattern in old_patterns:
                    if re.search(pattern, content):
                        structure_issues.append({
                            'file': file_path,
                            'type': 'old_structure',
                            'message': f'Found old structure import pattern: {pattern}',
                            'fixable': True
                        })
                        
        return structure_issues
        
    def fix_import_statement(self, import_str: str) -> str:
        """Convert import statements to match new structure."""
        # Convert backend → core
        import_str = re.sub(r'from .*\.backend\.', 'from src.core.', import_str)
        import_str = re.sub(r'import .*\.backend\.', 'import src.core.', import_str)
        
        # Convert frontend/GUI → gui
        import_str = re.sub(r'from .*\.frontend\.GUI\.', 'from src.gui.', import_str)
        import_str = re.sub(r'import .*\.frontend\.GUI\.', 'import src.gui.', import_str)
        
        # Convert frontend/TUI → tui
        import_str = re.sub(r'from .*\.frontend\.TUI\.', 'from src.tui.', import_str)
        import_str = re.sub(r'import .*\.frontend\.TUI\.', 'import src.tui.', import_str)
        
        return import_str
        
    def fix_file(self, file_path: Path, issues: List[dict]) -> bool:
        """Apply fixes to a single file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            modified = False
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                new_line = line
                
                # Fix import statements
                if 'import' in line and not line.strip().startswith('#'):
                    fixed_import = self.fix_import_statement(line)
                    if fixed_import != line:
                        new_line = fixed_import
                        modified = True
                        
                new_lines.append(new_line)
                
            if modified:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(new_lines))
                    
            return modified
            
        except Exception as e:
            print(f"Error fixing {file_path}: {str(e)}")
            return False
            
    def suggest_fixes(self, issues: List[dict]):
        """Generate fixing suggestions for detected issues."""
        suggestions = defaultdict(list)
        
        for issue in issues:
            file_path = issue['file']
            if issue['type'] == 'old_structure':
                suggestions[file_path].append(
                    "Update import statements to match new structure:\n"
                    "  - 'from backend' → 'from src.core'\n"
                    "  - 'from frontend.GUI' → 'from src.gui'\n"
                    "  - 'from frontend.TUI' → 'from src.tui'"
                )
            elif issue['type'] == 'core_dependency':
                suggestions[file_path].append(
                    "Remove GUI/TUI imports from core module.\n"
                    "Consider using dependency injection or events instead."
                )
                
        return suggestions
        
    def analyze_and_fix(self, auto_fix: bool = False):
        """Run complete analysis and optionally fix issues."""
        print(f"Analyzing project at: {self.project_root}")
        
        # Scan and categorize files
        component_types = self.scan_project()
        print(f"\nFound files:")
        for component, files in component_types.items():
            print(f"  {component}: {len(files)} files")
            
        # Check for structure issues
        structure_issues = self.check_structure_issues(component_types)
        
        if structure_issues:
            print("\nStructure issues found:")
            for issue in structure_issues:
                print(f"\n{issue['file'].relative_to(self.project_root)}:")
                print(f"  - {issue['message']}")
                
            suggestions = self.suggest_fixes(structure_issues)
            print("\nSuggested fixes:")
            for file_path, file_suggestions in suggestions.items():
                print(f"\n{file_path.relative_to(self.project_root)}:")
                for suggestion in file_suggestions:
                    print(f"  {suggestion}")
                    
            if auto_fix:
                proceed = input("\nApply automatic fixes? (y/n): ").lower().strip()
                if proceed == 'y':
                    print("\nCreating backup...")
                    self.create_backup()
                    print(f"Backup created at: {self.backup_dir}")
                    
                    print("\nApplying fixes...")
                    fixed_count = 0
                    for issue in structure_issues:
                        if issue['fixable'] and self.fix_file(issue['file'], [issue]):
                            fixed_count += 1
                            print(f"Fixed: {issue['file'].relative_to(self.project_root)}")
                            
                    print(f"\nFixed {fixed_count} files")
                    print(f"Original files backed up to: {self.backup_dir}")
        else:
            print("\nNo structure issues found!")
            
        print("\nBest practices for new structure:")
        print("1. Keep core modules independent of GUI/TUI")
        print("2. Use relative imports within each component (core/gui/tui)")
        print("3. Use absolute imports when crossing component boundaries")
        print("4. Consider creating interface modules in core for UI integration")
        print("5. Use __init__.py files to expose clean public APIs")

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_analyzer.py <project_root> [--fix]")
        return
        
    project_root = sys.argv[1]
    auto_fix = "--fix" in sys.argv
    
    analyzer = ImportAnalyzerFixer(project_root)
    analyzer.analyze_and_fix(auto_fix)

if __name__ == "__main__":
    main()