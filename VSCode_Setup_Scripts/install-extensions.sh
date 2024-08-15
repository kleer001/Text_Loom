#!/bin/bash

# Check if a filename was provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <extensions_file.txt>"
    exit 1
fi

input_file="$1"
log_file="failed_extensions.log"
> "$log_file" # Clear the log file if it exists

while IFS= read -r extension; do
    output=$(code --install-extension "$extension" 2>&1)
    echo "$output"
    if [[ $output == Failed* ]]; then
        echo "$extension" >> "$log_file"
    fi
done < "$input_file"

echo "Failed extensions have been logged to $log_file"
