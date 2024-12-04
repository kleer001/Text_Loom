from pathlib import Path
from typing import List, Dict, Set
import re
from enum import Enum, auto
from dataclasses import dataclass

def extract_component_name(file_content: str, file_stem: str) -> str:
    """Extract the main component class name from the file"""
    class_pattern = re.compile(r'class\s+(\w+)\s*\([^)]*\):')
    matches = class_pattern.findall(file_content)
    # Look for a class that matches the file name or ends with Window/Screen
    for match in matches:
        if match.lower() == file_stem.lower() or match.endswith(('Window', 'Screen')):
            return match
    return file_stem.title()

def clean_css_block(css: str) -> str:
    """Clean and normalize CSS block"""
    css = css.strip()
    css = css.replace('\r\n', '\n')
    return css

def extract_css_blocks() -> Dict[str, Dict[str, str]]:
    """Extract CSS blocks grouped by component and scoped properly"""
    css_blocks = {}
    css_pattern = re.compile(r'DEFAULT_CSS\s*=\s*f?"""(.*?)"""', re.DOTALL)

    for py_file in Path(".").rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            matches = css_pattern.findall(content)
            if matches:
                component_name = extract_component_name(content, py_file.stem)
                component_css = {}
                
                for block in matches:
                    # Clean the CSS block
                    clean_block = clean_css_block(block)
                    # Scope the CSS to the component
                    if not any(selector in clean_block for selector in [f"{component_name} ", f"{component_name}{{"]):
                        clean_block = f"{component_name} {{\n{clean_block}\n}}"
                    component_css[f"{component_name}-{len(component_css)}"] = clean_block
                
                css_blocks[component_name] = component_css

        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    return css_blocks

def extract_variables(css: str) -> Set[str]:
    """Extract theme variables from CSS"""
    pattern = re.compile(r"\{(?:pal|theme)\.([A-Z_]+)\}")
    return set(pattern.findall(css))

def generate_theme_manager(css_blocks: Dict[str, Dict[str, str]], output_file="theme_manager.py"):
    # Collect all unique variables
    all_variables = set()
    for component_blocks in css_blocks.values():
        for block in component_blocks.values():
            all_variables.update(extract_variables(block))

    with open(output_file, "w", encoding="utf-8") as f:
        # Write imports and Theme class
        f.write("""from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List
import importlib.util

@dataclass
class Theme:
""")
        # Write theme variables
        for var in sorted(all_variables):
            f.write(f"    {var}: str\n")

        # Write theme management code
        f.write('''
def load_theme_module(path: Path):
    """Dynamically import theme module from path"""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ThemeManager:
    @staticmethod
    def get_available_themes() -> List[str]:
        """Get list of available theme names from themes directory"""
        theme_dir = Path(__file__).parent / "themes"
        return [p.stem.replace("_colors", "") for p in theme_dir.glob("*_colors.py")]
        
    @staticmethod
    def load_theme(theme_name: str) -> Theme:
        """Load theme by name from themes directory"""
        theme_path = Path(__file__).parent / "themes" / f"{theme_name}_colors.py"
        if not theme_path.exists():
            raise ValueError(f"Theme {theme_name} not found")
        
        theme_module = load_theme_module(theme_path)
        return Theme(**{var: getattr(theme_module, var) for var in Theme.__annotations__})

    @staticmethod
    def get_css(theme: Theme) -> Dict[str, str]:
        """Generate CSS for all components using theme"""
        return {
''')

        # Write component CSS blocks with proper scoping
        for component, blocks in css_blocks.items():
            for block_id, css in blocks.items():
                # Replace pal. with theme.
                themed_css = css.replace("pal.", "theme.")
                # Proper indentation for readability
                indented_css = "\n".join("            " + line for line in themed_css.split("\n"))
                f.write(f'    "{block_id}": """\n{indented_css}\n""",\n')

        f.write("        }\n")  # Close the return dictionary

if __name__ == "__main__":
    css_blocks = extract_css_blocks()
    generate_theme_manager(css_blocks)