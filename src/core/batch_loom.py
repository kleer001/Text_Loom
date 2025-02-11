import argparse
import logging
import sys
from pathlib import Path
from typing import List, Set, Optional, Union, TextIO, Any
from core.base_classes import NodeEnvironment, Node
from core.flowstate_manager import load_flowstate


"""Batch processor for Text Loom flowstate files that evaluates and outputs node results.

This script loads a Text Loom flowstate file and processes its nodes, focusing on bottom-most
nodes (those with inputs but no outputs) by default. It supports both plain text and 
formatted output, with optional logging capabilities.

Args:
    flowstate: Path to flowstate JSON file (positional or -f/--flowstate-file)
    output: Path for output file (positional or -o/--output-file)
    -p/--plain-text: Format output as plain text, adding spacing between list items
    -l/--log-file: Path to log file for detailed processing information

Example usage:
    python batch_loom.py flowstate.json output.txt
    python batch_loom.py -f flowstate.json -o output.txt -p -l process.log

Raises:
    FileNotFoundError: If the specified flowstate file doesn't exist
    Exception: Various exceptions from node processing are caught and logged

Notes:
    - Bottom nodes are identified as those with inputs but no outgoing connections
    - Plain text formatting (-p) adds double newlines between list items and quad newlines between lists of lists
    - Log files duplicate all console output when specified
"""

def setup_logging(log_file: Optional[str] = None) -> None:
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)

def get_nodes_with_outputs(env: NodeEnvironment) -> Set[str]:
    output_nodes: Set[str] = set()
    
    for node in env.nodes.values():
        if hasattr(node, '_inputs'):
            for conn in node._inputs.values():
                if conn and conn.output_node():
                    output_nodes.add(str(conn.output_node().path()))
    
    return output_nodes

def find_bottom_nodes(env: NodeEnvironment) -> List[Node]:
    output_nodes = get_nodes_with_outputs(env)
    bottom_nodes = []
    
    for node in env.nodes.values():
        node_path = str(node.path())
        if node_path not in output_nodes and hasattr(node, '_inputs'):
            if any(node._inputs.values()):
                bottom_nodes.append(node)
    
    return bottom_nodes

def format_output(output: Any, plain_text: bool = False) -> str:
    if not plain_text:
        return str(output)
    
    if isinstance(output, list):
        formatted_items = []
        for item in output:
            if isinstance(item, list):
                formatted_items.append(format_output(item, plain_text=True))
            else:
                formatted_items.append(str(item).strip('[]'))
        return '\n\n'.join(formatted_items)
    
    return str(output).strip('[]')

def process_nodes(nodes: List[Node], output_file: Optional[Union[str, TextIO]] = None, plain_text: bool = False) -> None:
    outputs = []
    
    for node in nodes:
        try:
            logging.info(f"Processing node: {node.path()}")
            node.eval()
            output = node.get_output()
            formatted_output = format_output(output, plain_text)
            outputs.append(formatted_output)
            
            logging.info(f"Output from {node.path()}:")
            logging.info(formatted_output)
            logging.info("-" * 80)
            
        except Exception as e:
            logging.error(f"Error processing node {node.path()}: {e}")
    
    if output_file:
        final_output = '\n\n\n\n'.join(outputs) if plain_text else '\n'.join(outputs) + '\n'
        if isinstance(output_file, str):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_output)
        else:
            output_file.write(final_output)

def main():
    parser = argparse.ArgumentParser(description="Process TextLoom flowstate files")
    parser.add_argument("flowstate", nargs="?", help="Path to flowstate JSON file")
    parser.add_argument("output", nargs="?", help="Path to output file")
    parser.add_argument("-f", "--flowstate-file", help="Path to flowstate JSON file")
    parser.add_argument("-o", "--output-file", help="Path to output file")
    parser.add_argument("-p", "--plain-text", action="store_true", help="Format output as plain text")
    parser.add_argument("-l", "--log-file", help="Path to log file")
    
    args = parser.parse_args()
    
    flowstate_path = args.flowstate_file or args.flowstate
    output_path = args.output_file or args.output
    
    if not flowstate_path:
        parser.error("Flowstate file path is required")
    
    setup_logging(args.log_file)
    
    flowstate_path = Path(flowstate_path)
    if not flowstate_path.exists():
        logging.error(f"Error: File {flowstate_path} does not exist")
        return
    
    env = NodeEnvironment.get_instance()
    if not load_flowstate(str(flowstate_path)):
        logging.error("Failed to load flowstate")
        return
    
    bottom_nodes = find_bottom_nodes(env)
    if not bottom_nodes:
        logging.error("No bottom nodes found in flowstate")
        return
    
    logging.info(f"Found {len(bottom_nodes)} bottom nodes")
    process_nodes(bottom_nodes, output_path, args.plain_text)

if __name__ == "__main__":
    main()