import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info


def print_node_info(node):
    print(f"\n--- {node.name()} Node Information ---")
    print(f"Node: {node}")
    print(f"Node Type: {node.type()}")
    print(f"Node Path: {node.path()}")
    print(f"Node State: {node.state()}")
    print("Parameters:")
    if hasattr(node, '_parms'):  # Check if node has a _parms attribute
        for parm_name, parm in node._parms.items():
            print(f"  {parm_name}: {parm.raw_value()}")
    else:
        print("No parameters found.")
    print(f"Inputs: {node.inputs_with_indices()}")
    print(f"Outputs: {node.outputs_with_indices()}")
    print(f"Errors: {node.errors()}")
    print(f"Warnings: {node.warnings()}")
    print(f"Last Cook Time: {node.last_cook_time()}")
    print(f"Cook Count: {node.cook_count()}")


# Create nodes
loopman = Node.create_node(NodeType.LOOPER)
print("path after run = " , NodeEnvironment.node_exists(loopman.path()))
print_node_info(loopman)