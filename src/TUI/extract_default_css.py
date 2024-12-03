from pathlib import Path
from typing import List, Dict, Set
import re
from enum import Enum, auto
from dataclasses import dataclass


@dataclass
class Theme:
    """Template for theme colors"""

    pass


def quote_css_keywords(css: str) -> str:
    keywords = {
        r'\balign:\s*([\w\s]+);': lambda m: f'align: "{m.group(1)}";',
        r'\btext-align:\s*([\w\s]+);': lambda m: f'text-align: "{m.group(1)}";',
        r'\bcontent-align:\s*([\w\s]+);': lambda m: f'content-align: "{m.group(1)}";',
        r'\bheight:\s*auto\b': 'height: "auto"',
        r'\bwidth:\s*auto\b': 'width: "auto"',
        r'\bdock:\s*([\w\s]+);': lambda m: f'dock: "{m.group(1)}";',
        r'\blayout:\s*([\w\s]+);': lambda m: f'layout: "{m.group(1)}";',
    }
    
    result = css
    for pattern, replacement in keywords.items():
        if callable(replacement):
            result = re.sub(pattern, replacement, result)
        else:
            result = re.sub(pattern, replacement, result)
    return result

def extract_css_blocks() -> Dict[str, Set[str]]:
    css_blocks = {}
    css_pattern = re.compile(r'DEFAULT_CSS\s*=\s*f?"""(.*?)"""', re.DOTALL)

    for py_file in Path(".").rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            matches = css_pattern.findall(content)
            if matches:
                css_blocks[py_file.stem] = set(matches)
        except Exception as e:
            print(f"Error reading {py_file}: {e}")

    return css_blocks


def extract_variables(css: str) -> Set[str]:
    pattern = re.compile(r"\{(?:pal|theme)\.([A-Z_]+)\}")
    return set(pattern.findall(css))

def needs_theme_formatting(css: str) -> bool:
    double_brace_pattern = r'\{\{.*?\}\}'
    single_brace_pattern = r'\{(?!\{).*?(?!\})\}'
    
    has_double_braces = bool(re.search(double_brace_pattern, css))
    has_single_braces = bool(re.search(single_brace_pattern, css))
    
    return has_single_braces and not has_double_braces

def generate_theme_manager(css_blocks: Dict[str, Set[str]], output_file="theme_manager.py"):
    all_variables = set()
    for blocks in css_blocks.values():
        for block in blocks:
            all_variables.update(extract_variables(block))

    with open(output_file, "w", encoding="utf-8") as f:
        # Write imports and setup
        f.write(

            
            """from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List
import importlib.util

@dataclass
class Theme:
"""
        )
        # Write theme variables
        for var in sorted(all_variables):
            f.write(f"    {var}: str\n")

        # Write ThemeManager class
        f.write(
            '''
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
'''
        )


        for component, blocks in css_blocks.items():
            for block in blocks:
                quoted_block = quote_css_keywords(block)
                if needs_theme_formatting(block):
                    formatted_block = quoted_block.replace("pal.", "theme.")
                    f.write(f"    '{component}': f'''{formatted_block}''',\n")
                else:
                    f.write(f"    '{component}': '''{quoted_block}''',\n")

        f.write("       }\n")  # Close the return dictionary
        #f.write("}\n")         # Close the class



if __name__ == "__main__":
    css_blocks = extract_css_blocks()
    generate_theme_manager(css_blocks)
