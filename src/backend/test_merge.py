import os
from base_classes import Node, NodeType

def print_node_info(node, node_name):
    print(f"\n--- {node_name} Node Information ---")
    print(f"Node: {node}")
    print(f"Node Type: {node.type()}")
    print(f"Node Path: {node.path()}")
    print(f"Node State: {node.state()}")
    print("Parameters:")
    if hasattr(node, '_parms'):
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

# 3. Create a MERGE node
merge_node = Node.create_node(NodeType.MERGE)
print_node_info(merge_node, "Merge (Initial)")

# 4. Connect the MERGE node's input to the outputs of the three FILE_IN nodes
for i, file_in in enumerate(file_in_nodes):
    merge_node.set_input(f"input{i}", file_in, "output")

print_node_info(merge_node, "Merge (After Connections)")

# 5. Cook the MERGE node and check its output
merge_node.cook()
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


# 7. Cook the MERGE node again and check its output
merge_node.cook()
print_node_info(merge_node, "Merge (After Second Cook)")
# print("\nMerge Node Output (After Reordering):")
# print(merge_node.outputs("output").raw_value())

# Clean up
for filename, _ in temp_files:
    os.remove(filename)

print("\nTemporary files cleaned up.")
