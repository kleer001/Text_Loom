#!/usr/bin/env python3
import argparse
import os
import shutil
from pathlib import Path
import re
from typing import Dict, Optional

def backup_file(filepath: Path) -> None:
    if filepath.exists():
        backup = Path(f"{filepath}.old")
        if backup.exists():
            i = 1
            while backup.exists():
                backup = Path(f"{filepath}.old.{i}")
                i += 1
        shutil.copy2(filepath, backup)

def extract_color_variables(content: str) -> Dict[str, str]:
    color_vars = {}
    for line in content.splitlines():
        if line.strip() and not line.startswith('#'):
            if '=' in line:
                var_name, value = line.split('=', 1)
                var_name = var_name.strip()
                value = value.strip().strip('"\'')
                if any(c in value for c in ['#', 'rgb', 'rgba']):
                    color_vars[var_name] = value
    return color_vars

def convert_to_textual_theme(theme_name: str, colors: Dict[str, str]) -> str:
    # Map old color variables to new theme structure
    primary = colors.get('NODE_WIN_BORDER', '#486591')
    secondary = colors.get('NODE_WIN_BORDER_FOCUS', '#2C4975')
    
    theme_template = f"""from textual.theme import Theme

{theme_name}_theme = Theme(
    name="{theme_name}",
    dark=False,
    
    # Core colors
    background="{colors.get('MAIN_WIN_BACKGROUND', '#FAFAF8')}",
    foreground="{colors.get('MAIN_WIN_TEXT', '#222222')}",
    primary="{primary}",
    secondary="{secondary}",
    accent="{colors.get('PARAM_INPUT_SELECTED_BG', '#EDF2F7')}",
    error="{colors.get('GLOBAL_WIN_ERROR_COLOR', '#D93025')}",
    success="#4CAF50",
    warning="#FFA726",
    surface="{colors.get('NODE_MODAL_SURFACE', '#F5F5F2')}",
    panel="{colors.get('NODE_INPUT_BACKGROUND', '#FFFFFF')}",
    
    variables={{
        "text-muted": "{colors.get('PARAM_NAME_COLOR', '#444444')}",
        "text-on-primary": "{colors.get('MODELINE_TEXT', '#FFFFFF')}",
        "text-on-secondary": "#FFFFFF",
        
        "border-primary": "solid $primary",
        "border-secondary": "solid $secondary",
        "border-focus": "double $secondary",
        "border-modal": "thick $primary",
        
        "background-input": "$panel",
        "background-input-selected": "$accent",
        "background-input-invalid": "rgba(217, 48, 37, 0.1)",
        "background-editing": "$primary 10%",
        "background-help": "{colors.get('HELP_WIN_BACKGROUND', '$primary 5%')}",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "{colors.get('PARAM_INPUT_BORDER', '#D0D0D0')}",
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }}
)
"""
    return theme_template

def process_file(filepath: Path) -> None:
    if not filepath.name.endswith('_colors.py'):
        print(f"Skipping {filepath} - not a theme file")
        return
        
    print(f"Processing {filepath}")
    theme_name = filepath.stem.replace('_colors', '')
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    colors = extract_color_variables(content)
    new_content = convert_to_textual_theme(theme_name, colors)
    
    backup_file(filepath)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"Converted {filepath} to Textual theme format")

def main():
    parser = argparse.ArgumentParser(description='Convert color theme files to Textual theme format')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=str, help='Single file to convert')
    group.add_argument('-all', action='store_true', help='Convert all theme files in current directory')
    
    args = parser.parse_args()
    
    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File {filepath} not found")
            return
        process_file(filepath)
    
    elif args.all:
        current_dir = Path('.')
        for filepath in current_dir.glob('*_colors.py'):
            process_file(filepath)

if __name__ == '__main__':
    main()