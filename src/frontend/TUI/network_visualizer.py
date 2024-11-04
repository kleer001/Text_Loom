from dataclasses import dataclass, field
from typing import List, Set, Optional
from enum import Enum

class ConnectionType(Enum):
    VERTICAL = "↓"
    BRANCH = "+"
    NONE = " "

@dataclass
class Node:
    name: str
    inputs: Set['Node'] = field(default_factory=set)
    outputs: Set['Node'] = field(default_factory=set)
    contains: List['Node'] = field(default_factory=list)

@dataclass
class LayoutEntry:
    node: Optional[Node]
    indent: int
    connection_type: ConnectionType = ConnectionType.NONE
    multi_connection: bool = False
    connected_nodes: Set[Node] = field(default_factory=set)

def layout_network(nodes: List[Node]):
    layout = []
    processed_nodes = set()
    
    def process_node(node: Node, indent: int = 0):
        # First appearance of container node - showing inputs
        if node.contains:
            layout.append(LayoutEntry(
                node=node,
                indent=indent,
                connection_type=ConnectionType.VERTICAL if node.inputs else ConnectionType.NONE,
                connected_nodes=node.inputs
            ))
            
            # Process all contained nodes
            for contained in node.contains:
                contained.inputs.add(node)  # Connect to container
                process_node(contained, indent + 2)
            
            # Second appearance of container node - showing outputs
            if node.outputs:
                layout.append(LayoutEntry(
                    node=node,
                    indent=indent,
                    connection_type=ConnectionType.VERTICAL,
                    connected_nodes=node.outputs
                ))
        else:
            # Regular node processing
            layout.append(LayoutEntry(
                node=node,
                indent=indent,
                connection_type=ConnectionType.VERTICAL if node.inputs or node.outputs else ConnectionType.NONE,
                connected_nodes=node.inputs.union(node.outputs)
            ))
        
        processed_nodes.add(node)

    # Process all root nodes (nodes not contained in any other node)
    root_nodes = [n for n in nodes if not any(n in other.contains for other in nodes)]
    for node in root_nodes:
        process_node(node)
    
    # Add connection lines and branches
    final_layout = []
    i = 0
    while i < len(layout):
        entry = layout[i]
        final_layout.append(entry)
        
        if entry.connected_nodes:
            # Find next connected nodes
            next_connected = []
            search_idx = i + 1
            while search_idx < len(layout):
                if layout[search_idx].node in entry.connected_nodes:
                    next_connected.append(search_idx)
                search_idx += 1
            
            if next_connected:
                # Add vertical line for single connection
                if len(next_connected) == 1:
                    final_layout.append(LayoutEntry(
                        node=None,
                        indent=entry.indent,
                        connection_type=ConnectionType.VERTICAL
                    ))
                # Add branches for multiple connections
                else:
                    for idx in range(len(next_connected)):
                        final_layout.append(LayoutEntry(
                            node=None,
                            indent=entry.indent,
                            connection_type=ConnectionType.BRANCH if idx < len(next_connected)-1 else ConnectionType.VERTICAL,
                            multi_connection=idx < len(next_connected)-1
                        ))
        i += 1
    
    return final_layout

def render_layout(layout: List[LayoutEntry]) -> str:
    result = []
    for entry in layout:
        if entry.node is None:  # Connection line or branch
            if entry.multi_connection:
                line = " " * entry.indent + entry.connection_type.value + "-"
            else:
                line = " " * entry.indent + entry.connection_type.value
        else:  # Node
            line = " " * entry.indent + entry.node.name
            if entry.connection_type != ConnectionType.NONE:
                line = line
        result.append(line)
    return "\n".join(result)

# Example usage
if __name__ == "__main__":
    # Create test nodes
    system = Node("System")
    processor = Node("Processor")
    validator = Node("Validator")
    transformer = Node("Transformer")
    logger = Node("Logger")
    db = Node("Database")
    cache = Node("Cache")
    writer = Node("Writer")

    # Set up nested structure
    system.contains = [processor, logger]
    processor.contains = [validator, transformer]
    transformer.contains = [cache, writer]

    # Set up connections
    processor.inputs.add(system)      # System -> Processor
    validator.inputs.add(processor)   # Processor -> Validator
    transformer.inputs.add(validator) # Validator -> Transformer
    cache.inputs.add(transformer)     # Transformer -> Cache
    writer.inputs.add(transformer)    # Transformer -> Writer
    logger.inputs.add(processor)      # Processor -> Logger
    db.inputs.add(logger)            # Logger -> Database

    # Process and display
    layout = layout_network([system, processor, validator, transformer, logger, db, cache, writer])
    print(render_layout(layout))