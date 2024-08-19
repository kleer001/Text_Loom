import os
import argparse
import sys
import logging
from typing import List, Tuple, Dict

# Constants
TODO_MARKER = "[ ]"
DONE_MARKER = "[X]"
TODO_FILE_HEADER = "# TODO List\n\n"
AUTO_TODO_MARKER = "←"

def find_python_files(directory: str, max_depth: int = None, exclude_file: str = None) -> List[str]:
    """
    Find all Python files in the given directory and its subdirectories.
    
    Args:
    directory (str): The root directory to start the search.
    max_depth (int, optional): The maximum depth to search. None means no limit.
    exclude_file (str, optional): File to exclude from the search.
    
    Returns:
    List[str]: A list of paths to Python files.
    """
    python_files = []
    for root, _, files in os.walk(directory):
        if max_depth is not None:
            depth = root[len(directory):].count(os.sep)
            if depth > max_depth:
                continue
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if file_path != exclude_file:
                    python_files.append(file_path)
    return python_files

def extract_todos(file_path: str, quiet: bool) -> List[Tuple[str, int, str, str]]:
    """Extract TODOs from a Python file."""
    todos = []
    current_function = "Global"
    if not quiet:
        logging.info(f"Scanning file: {file_path}")
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, 1):
            stripped_line = line.strip()
            if stripped_line.startswith('def ') or stripped_line.startswith('class '):
                current_function = stripped_line.split()[1].split('(')[0]
            if '# TODO' in line:
                todo_text = line.split('# TODO', 1)[1].lstrip()
                todos.append((file_path, line_number, current_function, todo_text))
                if not quiet:
                    logging.info(f"  Found TODO at line {line_number}: {todo_text}")
    return todos

# Add this to your constants
AUTO_TODO_MARKER = "←"

def read_existing_todos(todo_file: str) -> Tuple[Dict[str, Tuple[int, str, str]], List[str]]:
    """Read existing TODOs from the TODO file."""
    existing_todos = {}
    content = []
    
    if not os.path.exists(todo_file):
        return existing_todos, [TODO_FILE_HEADER]

    with open(todo_file, 'r') as file:
        content = file.readlines()
        for i, line in enumerate(content):
            if (line.startswith(TODO_MARKER) or line.startswith(DONE_MARKER)) and line.strip().endswith(AUTO_TODO_MARKER):
                parts = line.strip()[:-1].split(' *')  # Remove AUTO_TODO_MARKER before splitting
                if len(parts) >= 2:
                    todo_text = ' '.join(parts[:-1]).strip()[4:]  # Remove checkbox and leading space
                    clean_todo_text = ' '.join(todo_text.split())  # Clean the todo text
                    file_info = parts[-1][:-1]  # Remove trailing asterisk
                    file_info_parts = file_info.rsplit(' ', 2)
                    if len(file_info_parts) == 3:
                        file_path, line_number, function_name = file_info_parts
                        file_path = file_path.lstrip('.')  # Remove leading dots
                        line_number = line_number.split('_')[-1]  # Remove 'Line_' prefix
                        function_name = function_name.rstrip('()')  # Remove trailing parentheses
                        existing_todos[file_path] = (i, line_number, clean_todo_text)
                    else:
                        logging.warning(f"Malformed auto-TODO entry at line {i+1}: {line.strip()}")
                else:
                    logging.warning(f"Malformed auto-TODO entry at line {i+1}: {line.strip()}")
    
    return existing_todos, content


def update_todo_file(todos: List[Tuple[str, int, str, str]], todo_file: str, section: str = None, quiet: bool = False, project_directory: str = ".") -> Tuple[int, int]:
    """Update the TODO.md file with the extracted TODOs."""
    existing_todos, content = read_existing_todos(todo_file)
    new_count = 0
    updated_count = 0
    updated_todos = set()

    # Prepare new content, keeping non-auto TODOs
    new_content = []
    for line in content:
        if not (line.strip().startswith(TODO_MARKER) and line.strip().endswith(AUTO_TODO_MARKER)) and \
           not (line.strip().startswith(DONE_MARKER) and line.strip().endswith(AUTO_TODO_MARKER)):
            new_content.append(line)

    # Process new TODOs
    for file_path, line_number, function_name, todo_text in todos:
        relative_path = os.path.relpath(file_path, project_directory)
        # Strip newlines and extra whitespace from todo_text
        clean_todo_text = ' '.join(todo_text.split())
        
        # Apply syntactic sugar
        pretty_path = f"...{relative_path}"
        pretty_line = f"Line_{line_number}"
        pretty_function = f"{function_name}()"
        
        todo_entry = f"{TODO_MARKER} {clean_todo_text} *{pretty_path} {pretty_line} {pretty_function}* {AUTO_TODO_MARKER}  \n"

        if relative_path in existing_todos:
            _, existing_line_number, existing_text = existing_todos[relative_path]
            if existing_text.strip() != clean_todo_text or str(existing_line_number) != str(line_number):
                updated_count += 1
                if not quiet:
                    logging.info(f"Updating existing TODO: {todo_entry.strip()}")
            else:
                if not quiet:
                    logging.info(f"TODO unchanged: {todo_entry.strip()}")
            del existing_todos[relative_path]  # Remove from existing_todos to mark as processed
        else:
            new_count += 1
            if not quiet:
                logging.info(f"Adding new TODO: {todo_entry.strip()}")

        new_content.append(todo_entry)
        updated_todos.add(relative_path)

    # Add completed TODOs (those that no longer exist in the code)
    for file_path, (_, line_number, todo_text) in existing_todos.items():
        # Strip newlines and extra whitespace from todo_text
        clean_todo_text = ' '.join(todo_text.split())
        
        # Apply syntactic sugar for completed TODOs
        pretty_path = f"...{file_path}"
        pretty_line = f"Line_{line_number}"
        
        done_entry = f"{DONE_MARKER} {clean_todo_text} *{pretty_path} {pretty_line}* {AUTO_TODO_MARKER}  \n"
        new_content.append(done_entry)
        if not quiet:
            logging.info(f"Checking off completed TODO: {done_entry.strip()}")

    # Write updated content back to file
    with open(todo_file, 'w') as file:
        file.writelines(new_content)

    return new_count, updated_count


def main(project_directory: str, todo_file: str, section: str = None, quiet: bool = False, max_depth: int = None) -> None:
    """Main function to extract TODOs and update the TODO.md file."""
    try:
        current_script = os.path.abspath(sys.argv[0])
        python_files = find_python_files(project_directory, max_depth, exclude_file=current_script)
        all_todos = []
        for file in python_files:
            all_todos.extend(extract_todos(file, quiet))
        new_count, updated_count = update_todo_file(all_todos, todo_file, section, quiet, project_directory)
        
        logging.info(f"\nSummary:")
        logging.info(f"Files scanned: {len(python_files)}")
        logging.info(f"TODOs found: {len(all_todos)}")
        logging.info(f"New TODOs added: {new_count}")
        logging.info(f"Existing TODOs updated: {updated_count}")
        logging.info(f"TODO.md has been updated successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.debug("", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract TODOs from Python files and update TODO.md")
    parser.add_argument("-d", "--directory", default=".", help="Project directory to scan (default: current directory)")
    parser.add_argument("-f", "--file", default="TODO.md", help="TODO file to update (default: TODO.md in current directory)")
    parser.add_argument("-s", "--section", help="Section in TODO.md to add new TODOs (optional)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode - only print summary")
    parser.add_argument("--max-depth", type=int, help="Maximum depth to search for Python files (default: no limit)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level")

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level), format='%(message)s')

    project_dir = os.path.abspath(args.directory)
    todo_file = os.path.join(os.getcwd(), args.file)
    
    main(project_dir, todo_file, args.section, args.quiet, args.max_depth)
