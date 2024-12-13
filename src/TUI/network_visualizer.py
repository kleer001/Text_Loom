import sys
import os

from core.base_classes import NodeEnvironment, NodeType, generate_node_types, Node
from core.flowstate_manager import load_flowstate

from dataclasses import dataclass
from typing import List, Set, Optional, Callable, Dict
from pathlib import Path
from enum import Enum

class NodeType(Enum):
    pass
NodeType = Enum("NodeType", generate_node_types(), type=NodeType)


@dataclass
class LayoutEntry:
    node: Node  
    indent: int

def get_container_path(node_path: str) -> str:
    return str(Path(node_path).parent)

def calculate_dependency_depth(node: 'Node', visited: Set['Node'] = None) -> int:
    if visited is None:
        visited = set()
    
    if node in visited:
        return 0
    visited.add(node)
    
    if not node._inputs:
        return 0
        
    max_depth = 0
    for conn in node._inputs.values():
        input_depth = calculate_dependency_depth(conn.output_node(), visited)
        max_depth = max(max_depth, input_depth)
    
    return max_depth + 1

def sort_nodes_by_dependency(nodes: List['Node']) -> List['Node']:
    node_depths: Dict['Node', int] = {}
    for node in nodes:
        node_depths[node] = calculate_dependency_depth(node)
    
    def get_sort_key(node: 'Node') -> tuple:
        depth = node_depths[node]
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

        layout.append(LayoutEntry(node=node, indent=indent))
        processed_nodes.add(node)

        container_path = node.path()
        contained_paths = [p for p in env.list_nodes() 
                         if get_container_path(p) == container_path]
        contained_nodes = [env.node_from_name(p) for p in contained_paths]
        contained_nodes = [n for n in contained_nodes if n is not None]
        contained_nodes = sort_nodes_by_dependency(contained_nodes)
        
        for contained in contained_nodes:
            process_node(contained, indent + 2)

    root_paths = [p for p in env.list_nodes() 
                 if get_container_path(p) == '/']
    root_nodes = [env.node_from_name(p) for p in root_paths]
    root_nodes = [n for n in root_nodes if n is not None]
    root_nodes = sort_nodes_by_dependency(root_nodes)
    
    for node in root_nodes:
        process_node(node)

    return layout

# In network_visualizer.py - just handle the structure:
def render_layout(
    layout: List[LayoutEntry],
    format_node: Optional[Callable[[Node, int], tuple[str, str]]] = None
) -> list[dict]:
    result = []
    output_connections: Dict[Node, List[Node]] = {}
    
    for entry in layout:
        if entry.node._inputs:
            for conn in entry.node._inputs.values():
                out_node = conn.output_node()
                if out_node not in output_connections:
                    output_connections[out_node] = []
                output_connections[out_node].append(entry.node)
    
    for entry in layout:
        line_info = {
            'indent': " " * entry.indent,
            'node': entry.node,
            'input_nodes': [],
            'output_nodes': []
        }
        
        if entry.node._inputs:
            for conn in entry.node._inputs.values():
                line_info['input_nodes'].append(conn.output_node())
                
        if entry.node in output_connections:
            line_info['output_nodes'] = output_connections[entry.node]
            
        result.append(line_info)
            
    return result

def main():
    file_path = os.path.abspath("save_file.json")
    load_flowstate(file_path)
    env = NodeEnvironment.get_instance()
    layout = layout_network(env)
    print(render_layout(layout))

if __name__ == "__main__":
    main()