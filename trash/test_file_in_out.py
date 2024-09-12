import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info

# Create nodes
file_in = Node.create_node(NodeType.FILE_IN)
file_out = Node.create_node(NodeType.FILE_OUT)
null_node = Node.create_node(NodeType.NULL)

# Connect nodes
null_node.set_input("input", file_in, "output")
file_out.set_input("input", null_node, "output")

# Set up input file
input_file_path = os.path.abspath("input.txt")
with open(input_file_path, "w") as f:
    f.write("This is a test input file.\nWith multiple lines.")

# Set file names
file_in._parms["file_name"].set(input_file_path)
output_file_path = os.path.abspath("output.txt")
file_out._parms["file_name"].set(output_file_path)

print("\n--- Initial State ---")
print_node_info(file_in, "File In")
print_node_info(null_node, "Null")
print_node_info(file_out, "File Out")

print("\n--- Cooking Nodes ---")
file_in.cook()
print_node_info(file_in, "File In (After Cook)")

null_node.cook()
print_node_info(null_node, "Null (After Cook)")

file_out.cook()
print_node_info(file_out, "File Out (After Cook)")

print("\n--- Checking Output File ---")
print(f"Checking for output file at: {output_file_path}")
if os.path.exists(output_file_path):
    with open(output_file_path, "r") as f:
        content = f.read()
    print("Output file content:")
    print(content)
else:
    print("Output file was not created.")

# Clean up
# os.remove(input_file_path)
# if os.path.exists(output_file_path):
#     os.remove(output_file_path)

print("\n--- Final State ---")
print_node_info(file_in, "File In")
print_node_info(null_node, "Null")
print_node_info(file_out, "File Out")