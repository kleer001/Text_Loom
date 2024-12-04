import argparse
import os
import re
from pathlib import Path
import shutil
from typing import Dict, List, Optional

THEME_COLOR_MAP = {
    # Base app colors from hex to semantic names
    '#FAFAF8': '$background',
    '#222222': '$foreground',
    '#486591': '$primary',
    '#2C4975': '$secondary',
    '#EDF2F7': '$accent',
    '#F5F5F2': '$surface',
    '#FFFFFF': '$panel',
    '#D93025': '$error',
    '#444444': '$text-muted',
    '#D0D0D0': '$input-border',
    
    # Palette variable mappings
    'MAIN_WIN_BACKGROUND': '$background',
    'MAIN_WIN_TEXT': '$foreground',
    'MODELINE_TEXT': '$text-on-secondary',
    'MODELINE_BACKGROUND': '$secondary',
    
    'NODE_WIN_BACKGROUND': '$background',
    'NODE_WIN_BORDER': '$primary',
    'NODE_WIN_BORDER_FOCUS': '$secondary',
    'NODE_MODAL_SURFACE': '$surface',
    'NODE_MODAL_BORDER': '$primary',
    'NODE_MODAL_TEXT': '$foreground',
    'NODE_INPUT_BACKGROUND': '$panel',
    'NODE_INPUT_TEXT': '$foreground',
    
    'NODE_BORDER_NORMAL': 'solid',
    'NODE_BORDER_FOCUS': 'double',
    'NODE_BORDER_MODAL': 'thick',
    
    'STATUS_WIN_BACKGROUND': '$background',
    'STATUS_WIN_BORDER_COLOR': '$primary',
    'STATUS_WIN_TEXT': '$foreground',
    
    'PARAM_SET_BG': '$background',
    'PARAM_SET_BORDER': '$primary',
    'PARAM_WINDOW_BG': '$background',
    'PARAM_WINDOW_BORDER': '$primary',
    'PARAM_TITLE_COLOR': '$secondary',
    'PARAM_WINDOW_FOCUS_BORDER': '$secondary',
    
    'PARAM_LABEL_BG': '$surface',
    'PARAM_LABEL_COLOR': '$text-muted',
    'PARAM_INPUT_BG': '$panel',
    'PARAM_INPUT_COLOR': '$foreground',
    'PARAM_INPUT_BORDER': '$input-border',
    'PARAM_INPUT_SELECTED_BG': '$accent',
    'PARAM_INPUT_SELECTED_COLOR': '$foreground',
    'PARAM_INPUT_SELECTED_BORDER': '$primary',
    'PARAM_VALUE_EDITING_BG': '$primary 10%',
    'PARAM_VALUE_EDITING_COLOR': '$foreground',
    'PARAM_INPUT_INVALID_BG': '$error 10%',
    'PARAM_NAME_COLOR': '$text-muted',
    'PARAM_VALUE_COLOR': '$foreground',
    'PARAM_VALUE_BG': '$panel',
    'PARAM_VALUE_SELECTED_COLOR': '$foreground',
    'PARAM_VALUE_SELECTED_BG': '$accent',
    
    'OUTPUT_WIN_BACKGROUND': '$background',
    'OUTPUT_WIN_BORDER_COLOR': '$primary',
    'OUTPUT_WIN_TEXT': '$foreground',
    
    'KEYMAP_SCR_BACKGROUND': '$background',
    'KEYMAP_SCR_TEXT': '$foreground',
    'KEYMAPCONTENT_SCR_BACKGROUND': '$surface',
    'KEYMAPCONTENT_SCR_TEXT': '$foreground',
    
    'HELP_WIN_BACKGROUND': '$primary 5%',
    'HELP_WIN_TEXT': '$foreground',
    'HELP_WIN_HEADER': '$secondary 30%',
    
    'GLOBAL_WIN_BACKGROUND_COLOR': '$background',
    'GLOBAL_WIN_TABLE_COLOR': '$primary',
    'GLOBAL_WIN_INPUT_COLOR': '$secondary',
    'GLOBAL_WIN_ERROR_COLOR': '$error',
    'GLOBAL_WIN_TEXT_COLOR': '$foreground',
    'GLOBAL_WIN_BORDER_COLOR': '$primary',
    
    'FILE_SCR_BACKGROUND': '$background',
    'FILE_SCR_TEXT': '$foreground',
    'FILECONTENT_SCR_BACKGROUND': '$surface',
    'FILECONTENT_SCR_TEXT': '$foreground',
}

def backup_file(file_path: Path) -> None:
    original = str(file_path)
    backup = original + '.old'
    
    if os.path.exists(backup):
        i = 1
        while os.path.exists(f"{original}.old.{i}"):
            i += 1
        backup = f"{original}.old.{i}"
    
    shutil.copy2(original, backup)

def identify_css_pattern(content: str) -> str:
    """Identifies whether the CSS content is an f-string or regular string."""
    if content.startswith('f"""') or content.startswith("f'''"):
        return 'f-string'
    elif content.startswith('"""') or content.startswith("'''"):
        return 'regular'
    return 'unknown'

def convert_regular_css(css_content: str) -> str:
    """Converts literal CSS content by replacing hex colors with semantic variables."""
    for old_color, new_var in THEME_COLOR_MAP.items():
        css_content = css_content.replace(old_color, new_var)
    return css_content

def convert_f_string_css(css_content: str) -> str:
    """Converts f-string CSS content by replacing placeholders like {pal.NODE_MODAL_SURFACE}."""
    pattern = r'\{pal\.([A-Z_]+)\}'
    for match in re.finditer(pattern, css_content):
        old_var = match.group(1)  # Extract variable name like NODE_MODAL_SURFACE
        new_var = THEME_COLOR_MAP.get(old_var, f"${old_var.lower()}")  # Map to semantic variable
        css_content = css_content.replace(f"{{pal.{old_var}}}", new_var)
    return css_content

def convert_css_string(css_content: str) -> str:
    """
    Converts an f-string CSS to a regular string by:
    1. Removing the 'f' prefix.
    2. Replacing {pal.VARIABLE} with the corresponding semantic variables.
    """
    # Remove the 'f' prefix
    css_content = css_content.lstrip('f')
    
    # Replace {pal.VARIABLE} with semantic variables
    pattern = r'\{pal\.([A-Z_]+)\}'
    css_content = re.sub(
        pattern,
        lambda match: THEME_COLOR_MAP.get(match.group(1), f"${match.group(1).lower()}"),
        css_content,
    )
    
    return css_content


def process_css_block(content: str) -> str:
    pattern_type = identify_css_pattern(content)
    
    if pattern_type == 'f-string':
        return convert_f_string_css(content)
    elif pattern_type == 'regular':
        return convert_regular_css(content)
    else:
        return content


def convert_theme_file(content: str) -> str:
    from TUI.themes.default_colors import default_theme
    theme_vars = default_theme.variables
    
    new_content = []
    theme_name = os.path.basename(file_path).replace('_colors.py', '')
    
    new_content.append("from textual.theme import Theme")
    new_content.append(f"\n{theme_name}_theme = Theme(")
    new_content.append(f"    name='{theme_name}',")
    new_content.append("    dark=False,  # Adjust if needed")
    
    # Extract colors from old format and map to new
    color_matches = re.finditer(r'^(\w+)\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    colors = {}
    for match in color_matches:
        var_name, color_value = match.groups()
        colors[var_name] = color_value
    
    # Map core colors
    core_colors = {
        'background': colors.get('MAIN_WIN_BACKGROUND', '#FAFAF8'),
        'foreground': colors.get('MAIN_WIN_TEXT', '#222222'),
        'primary': colors.get('NODE_WIN_BORDER', '#486591'),
        'secondary': colors.get('NODE_WIN_BORDER_FOCUS', '#2C4975'),
        'accent': colors.get('PARAM_INPUT_SELECTED_BG', '#EDF2F7'),
        'error': colors.get('GLOBAL_WIN_ERROR_COLOR', '#D93025'),
        'surface': colors.get('NODE_MODAL_SURFACE', '#F5F5F2'),
        'panel': colors.get('NODE_INPUT_BACKGROUND', '#FFFFFF'),
    }
    
    for color, value in core_colors.items():
        new_content.append(f"    {color}='{value}',")
    
    new_content.append("    variables={")
    for var, value in theme_vars.items():
        new_content.append(f"        '{var}': '{value}',")
    new_content.append("    }")
    new_content.append(")")
    
    return "\n".join(new_content)


def convert_file(file_path: Path) -> None:
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    # Backup the original file
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if 'DEFAULT_CSS' in content:
        # Match DEFAULT_CSS definitions with or without `f`
        css_pattern = r'(DEFAULT_CSS\s*=\s*f?["\'"]{3}(.*?)[\'"]{3})'
        
        def replace_css(match):
            full_declaration = match.group(1)  # Entire DEFAULT_CSS block
            css_content = match.group(2)  # Extracted CSS content
            
            # Convert the CSS
            converted = convert_css_string(css_content)
            
            # Remove double curly braces and ensure quotes are consistent
            converted = converted.replace("{{", "{").replace("}}", "}")
            
            # Reconstruct the CSS without the `f` prefix
            return full_declaration.replace('f"""', '"""').replace('f\'\'\'', '\'\'\'').replace(css_content, converted)
        
        # Perform the substitution
        new_content = re.sub(css_pattern, replace_css, content, flags=re.DOTALL)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
    else:
        print(f"No DEFAULT_CSS found in {file_path}")


        
def main():
    parser = argparse.ArgumentParser(description='Convert theme variables to Textual theme system')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=str, help='Single file to convert')
    group.add_argument('-all', action='store_true', help='Convert all relevant files in current directory')
    
    args = parser.parse_args()
    
    if args.file:
        convert_file(Path(args.file))
    elif args.all:
        relevant_files = list(Path('.').glob('*_colors.py'))
        relevant_files.extend(Path('.').glob('*.py'))
        
        for file_path in relevant_files:
            if not file_path.name.endswith('.old'):
                convert_file(file_path)
    
if __name__ == "__main__":
    main()