import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info

# Create nodes
text_node = Node.create_node(NodeType.TEXT)
file_out = Node.create_node(NodeType.FILE_OUT)

# Connect nodes
file_out.set_input("input", text_node, "output")

# Set up TextNode
text_node._parms["text_string"].set("This is a filler text string for testing.")

# Set up FileOutNode
output_file_path = os.path.abspath("output.txt") #path 1
file_out._parms["file_name"].set(output_file_path)

print("\n--- Initial State ---")
print_node_info(text_node, "Text Node")
print_node_info(file_out, "File Out")

print("\n--- Cooking Nodes ---")
file_out.cook()
print_node_info(text_node, "Text Node (After Cook)")
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
if os.path.exists(output_file_path):
    os.remove(output_file_path)
    print(f"\nTemporary file {output_file_path} has been removed.")

#second round

text_node._parms["text_string"].set("We've changed the string for more testing.")

# Set up FileOutNode
output_file_path = os.path.abspath("output2.txt") #path 1
file_out._parms["file_name"].set(output_file_path)

print("\n--- Cooking Nodes Again ---")
file_out.cook()
print_node_info(text_node, "Text Node (After Cook)")
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
if os.path.exists(output_file_path):
    os.remove(output_file_path)
    print(f"\nTemporary file {output_file_path} has been removed.")












