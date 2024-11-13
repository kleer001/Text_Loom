import sys
import os

# current_dir = os.path.dirname(os.path.abspath(__file__))
# src_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
# backend_dir = os.path.join(src_dir, 'backend')
# nodes_dir = os.path.join(backend_dir, 'nodes')

# sys.path.insert(0, src_dir)
# sys.path.insert(0, backend_dir)
# sys.path.insert(0, nodes_dir)

from core.base_classes import NodeEnvironment, NodeType, generate_node_types, Node
from core.flowstate_manager import load_flowstate

from dataclasses import dataclass
from typing import List, Set
from pathlib import Path
from enum import Enum

class NodeType(Enum):
    pass
NodeType = Enum("NodeType", generate_node_types(), type=NodeType)


@dataclass
class LayoutEntry:
    node: Node  # Your Node class
    indent: int

def get_container_path(node_path: str) -> str:
    """Returns the container path for a node"""
    return str(Path(node_path).parent)

def calculate_dependency_depth(node: 'Node', visited: Set['Node'] = None) -> int:
    """
    Calculate how deep in the dependency chain a node is.
    Returns:
        0 for nodes with no inputs (sources)
        max(input_depths) + 1 for nodes with inputs
    """
    if visited is None:
        visited = set()
    
    # Avoid circular dependencies
    if node in visited:
        return 0
    visited.add(node)
    
    # If no inputs, it's a source node
    if not node._inputs:
        return 0
        
    # Calculate max depth of input nodes
    max_depth = 0
    for conn in node._inputs.values():
        input_depth = calculate_dependency_depth(conn.output_node(), visited)
        max_depth = max(max_depth, input_depth)
    
    return max_depth + 1

def sort_nodes_by_dependency(nodes: List['Node']) -> List['Node']:
    """Sort nodes by their dependency depth and connection indices"""
    
    # Calculate depths for all nodes
    node_depths: Dict['Node', int] = {}
    for node in nodes:
        node_depths[node] = calculate_dependency_depth(node)
    
    def get_sort_key(node: 'Node') -> tuple:
        depth = node_depths[node]
        # For nodes at same depth, use input/output indices as secondary sort
        if node._inputs:
            input_idx = min(conn.output_index() for conn in node._inputs.values())
        else:
            input_idx = float('inf')
        return (depth, input_idx)
    
    return sorted(nodes, key=get_sort_key)

def layout_network(env: NodeEnvironment) -> List[LayoutEntry]:
    layout = []
    processed_nodes = set()
    
    def process_node(node, indent: int = 0):
        if node in processed_nodes and get_container_path(node.path()) == '/':
            return

        # Add node at current indent level
        layout.append(LayoutEntry(node=node, indent=indent))
        processed_nodes.add(node)

        # Process nodes inside this container
        container_path = node.path()
        # Get paths of contained nodes then convert to actual node objects
        contained_paths = [p for p in env.list_nodes() 
                         if get_container_path(p) == container_path]
        contained_nodes = [env.node_from_name(p) for p in contained_paths]
        
        # Filter out None values in case node_from_name failed
        contained_nodes = [n for n in contained_nodes if n is not None]
        
        # Sort contained nodes by dependency depth
        contained_nodes = sort_nodes_by_dependency(contained_nodes)
        
        for contained in contained_nodes:
            process_node(contained, indent + 2)

    # Get root nodes (nodes at root level)
    root_paths = [p for p in env.list_nodes() 
                 if get_container_path(p) == '/']
    root_nodes = [env.node_from_name(p) for p in root_paths]
    root_nodes = [n for n in root_nodes if n is not None]
    
    # Sort root nodes by dependency depth
    root_nodes = sort_nodes_by_dependency(root_nodes)
    
    for node in root_nodes:
        process_node(node)

    return layout

def render_layout(layout: List[LayoutEntry]) -> str:
    result = []
    for entry in layout:
        # Start with indented node name and path
        #line = " " * entry.indent + f"{entry.node.name()} ({entry.node.path()})"
        # Start with indented node name
        line = " " * entry.indent + f"{entry.node.name()}"

        # Add output connections if any
        if entry.node._inputs:
            connections = []
            # Sort connections by input index
            for idx, conn in sorted(entry.node._inputs.items()):
                out_node = conn.output_node()
                connections.append(f"{out_node.name()}[{conn.output_index()}]")
            if connections:
                line += f" <- " + ", ".join(connections)
        
        result.append(line)
            
    return "\n".join(result)

def main():
    
    file_path = os.path.abspath("save_file.json")
    load_flowstate(file_path)
    
    # Get the environment instance
    env = NodeEnvironment.get_instance()
    
    # Generate and print the layout
    layout = layout_network(env)
    print(render_layout(layout))

if __name__ == "__main__":
    main()