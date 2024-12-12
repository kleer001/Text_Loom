import re
import sys
import os
from pathlib import Path

def find_and_replace_globals(execute=False):
    """Find all $GLOBAL patterns and optionally replace with $GLOBAL"""
    pattern = r'\${(\$[A-Z]{2,})}'
    allowed_extensions = {'.py', '.txt', '.json'}
    
    for path in Path('.').rglob('*'):
        if path.is_file() and path.suffix in allowed_extensions:
            try:
                content = path.read_text()
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    old = match.group(0)
                    new = match.group(1)
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.start())
                    if line_end == -1:
                        line_end = len(content)
                    line = content[line_start:line_end]
                    
                    print(f"\nFile: {path}")
                    print(f"Line: {line}")
                    print(f"Change: {old} -> {new}")
                
                if execute:
                    new_content = re.sub(pattern, r'\1', content)
                    if new_content != content:
                        path.write_text(new_content)
                        print(f"\nUpdated: {path}")

            except Exception as e:
                print(f"Error processing {path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    execute = "-x" in sys.argv
    if execute:
        print("Running in execute mode - files will be modified")
    else:
        print("Running in preview mode - no files will be modified")
    
    find_and_replace_globals(execute)
