import argparse
from pathlib import Path
from typing import List, Set
from core.base_classes import NodeEnvironment, Node
from core.flowstate_manager import load_flowstate

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

def process_nodes(nodes: List[Node]) -> None:
    for node in nodes:
        try:
            print(f"Processing node: {node.path()}")
            node.eval()
            output = node.get_output()
            print(f"Output from {node.path()}:")
            print(output)
            print("-" * 80)
        except Exception as e:
            print(f"Error processing node {node.path()}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process TextLoom flowstate files")
    parser.add_argument("flowstate", type=str, help="Path to flowstate JSON file")
    args = parser.parse_args()
    
    flowstate_path = Path(args.flowstate)
    if not flowstate_path.exists():
        print(f"Error: File {flowstate_path} does not exist")
        return
    
    env = NodeEnvironment.get_instance()
    if not load_flowstate(str(flowstate_path)):
        print("Failed to load flowstate")
        return
    
    bottom_nodes = find_bottom_nodes(env)
    if not bottom_nodes:
        print("No bottom nodes found in flowstate")
        return
    
    print(f"Found {len(bottom_nodes)} bottom nodes")
    process_nodes(bottom_nodes)

if __name__ == "__main__":
    main()