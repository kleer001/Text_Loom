import os
from base_classes import Node, NodeType
from print_node_info import print_node_info

# 1. Create three temp txt files with simple filler text
temp_files = [
    ("temp1.txt", "This is the first file about cats."),
    ("temp2.txt", "This is the second file about dogs."),
    ("temp3.txt", "This is the third file about birds.")
]

for filename, content in temp_files:
    with open(filename, "w") as f:
        f.write(content)

# 2. Create three FILE_IN nodes and point each to the txt files
file_in_nodes = []
for i, (filename, _) in enumerate(temp_files):
    file_in = Node.create_node(NodeType.FILE_IN)
    file_in._parms["file_name"].set(os.path.abspath(filename))
    file_in_nodes.append(file_in)
    print_node_info(file_in, f"File In {i+1}")

# 3. Create a MERGE node and FILEOUT node
merge_node = Node.create_node(NodeType.MERGE)
print_node_info(merge_node, "Merge (Initial)")

# 4. Connect the MERGE node's input to the outputs of the three FILE_IN nodes
for i, file_in in enumerate(file_in_nodes):
    merge_node.set_input(f"input{i}", file_in, "output")

# create and setup the FILEOUT node
file_out = Node.create_node(NodeType.FILE_OUT)
output_file_path = os.path.abspath("output_1.txt")
temp_files.append((output_file_path,""))
file_out._parms["file_name"].set(output_file_path)
file_out.set_input("input", merge_node, "output")
print_node_info(file_out, "File Out")
print_node_info(merge_node, "Merge (After Connections)")

# 5. Cook the FILEOUT node and check its output
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


print_node_info(merge_node, "Merge (After First Cook)")
# print("\nMerge Node Output:")
# print(merge_node.outputs("output").raw_value())

# 6. Reorder the inputs going to the MERGE node
current_inputs = merge_node.inputs()
print("\nCurrent input order:", [i for i in range(len(current_inputs))])

# Reorder: move the last input to the first position
reordered_indices = [2, 0, 1]  # Assuming we have 3 inputs
reordered_inputs = [current_inputs[i] for i in reordered_indices]

print("Reordered input indices:", reordered_indices)

for i in range(len(current_inputs)):
    merge_node.remove_input(f"input{i}")

for i, input_node in enumerate(reordered_inputs):
    merge_node.set_input(f"input{i}", input_node, "output")

print("New input order:", [reordered_indices.index(i) for i in range(len(reordered_inputs))])

output_file_path = os.path.abspath("output_2.txt")
temp_files.append((output_file_path,""))
file_out._parms["file_name"].set(output_file_path)
print("New file out created ", output_file_path)

# 7. Cook the MERGE node again and check its output
merge_node.cook()
print_node_info(merge_node, "Merge (After Second Cook)")
# print("\nMerge Node Output (After Reordering):")
# print(merge_node.outputs("output").raw_value())

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
for filename, _ in temp_files:
    if(os.path.exists(filename)):
        os.remove(filename)

print("\nTemporary files cleaned up.")
