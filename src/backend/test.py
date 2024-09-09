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
os.remove(input_file_path)
if os.path.exists(output_file_path):
    os.remove(output_file_path)

print("\n--- Final State ---")
print_node_info(file_in, "File In")
print_node_info(null_node, "Null")
print_node_info(file_out, "File Out")