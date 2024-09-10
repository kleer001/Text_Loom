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

# Set up input file
input_file_path = os.path.abspath("./input.txt")
with open(input_file_path, "w") as f:
    f.write("This is a test input file.\nWith multiple lines.")

# Set file names
file_in._parms["file_name"].set(str(input_file_path))

print("\n--- Initial State ---")
print_node_info(file_in, "File In")

print(f"Debug: input_file_path = {input_file_path}")

print("\n--- Cooking Nodes ---")
file_in.cook()
print_node_info(file_in, "File In (After Cook)")

# Clean up
# os.remove(input_file_path)

