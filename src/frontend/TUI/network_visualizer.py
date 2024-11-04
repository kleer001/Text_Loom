from dataclasses import dataclass, field
from typing import List, Set, Optional

@dataclass
class Node:
    name: str
    inputs: Set['Node'] = field(default_factory=set)
    outputs: Set['Node'] = field(default_factory=set)
    contains: List['Node'] = field(default_factory=list)
    def __hash__(self):
        return hash(self.name)

@dataclass
class LayoutEntry:
    node: Node
    indent: int

def layout_network(nodes: List[Node]):
    layout = []
    processed_nodes = set()
    
    def process_node(node: Node, indent: int = 0):
        if node in processed_nodes and not node.contains:
            return

        # Add node at current indent level
        layout.append(LayoutEntry(node=node, indent=indent))
        processed_nodes.add(node)

        # Process contained nodes
        if node.contains:
            for contained in node.contains:
                process_node(contained, indent + 2)
            # Add container node again after processing its contents
            layout.append(LayoutEntry(node=node, indent=indent))

    # Process all root nodes (nodes not contained in any other node)
    root_nodes = [n for n in nodes if not any(n in other.contains for other in nodes)]
    for node in root_nodes:
        process_node(node)

    return layout

def render_layout(layout: List[LayoutEntry]) -> str:
    result = []
    for entry in layout:
        # Start with indented node name
        line = " " * entry.indent + entry.node.name
        
        # Add output connections if any
        if entry.node.outputs:
            output_list = [f"({n.name})" for n in entry.node.outputs]
            connections = " -> ".join(output_list)
            line += f" -> {connections}"
        
        result.append(line)
            
    return "\n".join(result)

def connect_nodes(source: Node, target: Node):
    """Helper function to properly connect nodes bidirectionally"""
    target.inputs.add(source)
    source.outputs.add(target)

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
    connect_nodes(system, processor)      # System -> Processor
    connect_nodes(processor, validator)   # Processor -> Validator
    connect_nodes(validator, transformer) # Validator -> Transformer
    connect_nodes(transformer, cache)     # Transformer -> Cache
    connect_nodes(transformer, writer)    # Transformer -> Writer
    connect_nodes(processor, logger)      # Processor -> Logger
    connect_nodes(logger, db)            # Logger -> Database

    # Process and display
    layout = layout_network([system, processor, validator, transformer, logger, db, cache, writer])
    print(render_layout(layout))