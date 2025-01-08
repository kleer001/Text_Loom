import os
import re

def add_single_output_line():
    # Get the current directory
    current_dir = os.getcwd()

    # Iterate through files in the current directory
    for filename in os.listdir(current_dir):
        # Check if the file matches the pattern *_node.py
        if filename.endswith("_node.py"):
            file_path = os.path.join(current_dir, filename)
            
            # Read the contents of the file
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Find the line that starts with SINGLE_INPUT and add SINGLE_OUTPUT = TRUE after it
            modified_lines = []
            single_input_found = False
            for line in lines:
                modified_lines.append(line)
                if line.strip().startswith("SINGLE_INPUT") and not single_input_found:
                    modified_lines.append("SINGLE_OUTPUT = TRUE\n")
                    single_input_found = True

            # Write the modified contents back to the file
            with open(file_path, 'w') as file:
                file.writelines(modified_lines)

            print(f"Modified {filename}")

if __name__ == "__main__":
    add_single_output_line()
    print("Script execution completed.")
