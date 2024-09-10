import os
from base_classes import NodeEnvironment, Node, NodeType

def print_node_info(node, node_name):
    print(f"\n--- {node_name} Node Information ---")
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
file_in = Node.create_node(NodeType.FILE_IN)
null_node = Node.create_node(NodeType.NULL)

# Connect nodes
null_node.set_input("input", file_in, "output")

# Set up input file
input_file_path = os.path.abspath("input.txt")
with open(input_file_path, "w") as f:
    f.write("This is a test input file.\nWith multiple lines.")

# Set file names
file_in._parms["file_name"].set(input_file_path)

print("\n--- Initial State ---")
print_node_info(file_in, "File In")
print_node_info(null_node, "Null")

print("\n--- Cooking Nodes ---")
file_in.cook()
print_node_info(file_in, "File In (After Cook)")

null_node.cook()
print_node_info(null_node, "Null (After Cook)")

