import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info

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

