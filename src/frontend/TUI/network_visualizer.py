from dataclasses import dataclass
from typing import List, Set
from pathlib import Path
from ...src.backend.base_classes import NodeEnvironment
from ...src.backend.flowstate_manager import load_flowstate


@dataclass
class LayoutEntry:
    node: 'Node'  # Your Node class
    indent: int

def get_container_path(node_path: str) -> str:
    """Returns the container path for a node"""
    return str(Path(node_path).parent)

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
        contained_nodes = [n for n in env.list_nodes() if get_container_path(n.path()) == container_path]
        
        # Sort contained nodes by their input/output relationships
        def get_node_order(n):
            # Earlier output_index should come first
            if n._inputs:
                return min(conn.output_index() for conn in n._inputs.values())
            return float('inf')
            
        contained_nodes.sort(key=get_node_order)
        
        for contained in contained_nodes:
            process_node(contained, indent + 2)

    # Get root nodes (nodes at root level)
    root_nodes = [n for n in env.list_nodes() if get_container_path(n.path()) == '/']
    
    # Sort root nodes (those without container) by their connections
    def get_root_order(node):
        if node._inputs:
            return min(conn.output_index() for conn in node._inputs.values())
        return float('inf')
        
    root_nodes.sort(key=get_root_order)
    
    for node in root_nodes:
        process_node(node)

    return layout

def render_layout(layout: List[LayoutEntry]) -> str:
    result = []
    for entry in layout:
        # Start with indented node name and path
        line = " " * entry.indent + f"{entry.node.name()} ({entry.node.path()})"
        
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
    # Load the save file
    load_flowstate("../../save_file.json")
    
    # Get the environment instance
    env = NodeEnvironment.get_instance()
    
    # Generate and print the layout
    layout = layout_network(env)
    print(render_layout(layout))

if __name__ == "__main__":
    main()