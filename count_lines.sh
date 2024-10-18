#!/bin/bash

# Count lines in all .py files in the current directory
line_count=$(find . -maxdepth 1 -name "*.py" -type f -exec wc -l {} + | awk '{total += $1} END {print total}')

echo "Total lines in .py files: $line_count"
