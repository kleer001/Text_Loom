import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
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

