import os
from pathlib import Path
import re

def fix_theme_files(themes_dir):
    # Find all theme files
    theme_files = Path(themes_dir).glob("*_colors.py")
    
    # Regex to find lines with trailing quotes after comments
    pattern = re.compile(r'^(\s*[^#]+#[^"]*)",\s*$')
    
    for file_path in theme_files:
        print(f"Processing {file_path.name}...")
        
        # Read the file
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Flag to track if we made any changes
        changes_made = False
        
        # Process each line
        fixed_lines = []
        for line in lines:
            match = pattern.match(line)
            if match:
                # Remove the trailing quote and keep the line ending
                fixed_line = match.group(1) + '\n'
                fixed_lines.append(fixed_line)
                changes_made = True
            else:
                fixed_lines.append(line)
        
        # Only write if we made changes
        if changes_made:
            print(f"  Fixing trailing quotes in {file_path.name}")
            with open(file_path, 'w') as f:
                f.writelines(fixed_lines)
        else:
            print(f"  No fixes needed in {file_path.name}")

if __name__ == "__main__":
    # Assuming this script is in the same directory as the themes folder
    themes_dir = Path(__file__).parent / "themes"
    print(f"Looking for theme files in: {themes_dir}")
    fix_theme_files(themes_dir)