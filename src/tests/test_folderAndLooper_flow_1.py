import sys, os
import shutil
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

# Create test directory and files
test_dir = os.path.abspath("test_debug")
os.makedirs(test_dir, exist_ok=True)

for i in range(3):
    with open(os.path.join(test_dir, f"file{i}.txt"), "w") as f:
        f.write(f"Content_{i}")

print("=== DEBUG: Testing FolderNode Output Indexing ===\n")

# Create nodes
folder_node = Node.create_node(NodeType.FOLDER, node_name="folder")
test_node = Node.create_node(NodeType.TEXT, node_name="test_receiver")

# Configure folder node
folder_node._parms["folder_path"].set(test_dir)
folder_node._parms["pattern"].set("*.txt")
folder_node._parms["sort_by"].set("name")

# First evaluation - check what folder_node produces
print("STEP 1: Initial folder_node evaluation")
folder_output = folder_node.eval()
print(f"folder_node._output type: {type(folder_output)}")
print(f"folder_node._output length: {len(folder_output)}")
print(f"Output[0] (contents) sample: {folder_output[0][0] if folder_output[0] else 'EMPTY'}")
print(f"Output[1] (names) sample: {folder_output[1][0] if folder_output[1] else 'EMPTY'}")
print()

# Connect to output[0] (contents)
print("STEP 2: Connect test_node to folder_node output[0]")
test_node.set_input(0, folder_node, output_index=0)
print(f"test_node input 0 connection: {test_node._inputs.get(0)}")
if test_node._inputs.get(0):
    conn = test_node._inputs[0]
    print(f"  - source_node: {conn.output_node().name()}")
    print(f"  - output_index: {conn.output_index()}")
print()

# What does test_node receive?
print("STEP 3: Evaluate test_node (connected to output[0])")
test_node._parms["text_string"].set("RECEIVED: ")
test_node._parms["prefix"].set(True)
test_node._parms["per_item"].set(True)
test_output = test_node.eval()
print(f"test_node output: {test_output}")
print()

# Now reconnect to output[1] (names)
print("STEP 4: Disconnect and reconnect to output[1]")
test_node.remove_input(0)
test_node.set_input(0, folder_node, output_index=1)
print(f"test_node input 0 connection: {test_node._inputs.get(0)}")
if test_node._inputs.get(0):
    conn = test_node._inputs[0]
    print(f"  - source_node: {conn.output_node().name()}")
    print(f"  - output_index: {conn.output_index()}")
print()

# After STEP 4
print("\nDEBUG: Check folder_node._outputs dictionary")
for output_idx, conns in folder_node._outputs.items():
    print(f"  Output index {output_idx}: {len(conns)} connections")
    for conn in conns:
        print(f"    -> connects to: {conn.input_node().name()}, output_index: {conn.output_index()}")

# Reset states
print("STEP 5: Reset states and re-evaluate")
folder_node.set_state(NodeState.UNCOOKED)
test_node.set_state(NodeState.UNCOOKED)

# Check folder_node output again
folder_output2 = folder_node.eval()
print(f"folder_node._output after reset:")
print(f"  Output[0] (contents) sample: {folder_output2[0][0] if folder_output2[0] else 'EMPTY'}")
print(f"  Output[1] (names) sample: {folder_output2[1][0] if folder_output2[1] else 'EMPTY'}")
print()

# What does test_node receive now?
print("STEP 6: Evaluate test_node (should now have output[1] data)")
test_output2 = test_node.eval()
print(f"test_node output: {test_output2}")
print()

# Let's check what the input gathering mechanism sees
print("STEP 7: Debug - What does test_node._gather_input_data see?")
print(f"test_node has {len(test_node._inputs)} inputs")
for input_idx, conn in test_node._inputs.items():
    print(f"  Input {input_idx}:")
    print(f"    source: {conn.output_node().name()}")
    print(f"    output_index: {conn.output_index()}")
    # Try to see what data it would get
    source = conn.output_node()
    out_idx = conn.output_index()
    print(f"    source._output type: {type(source._output)}")
    print(f"    source._output length: {len(source._output) if isinstance(source._output, (list, tuple)) else 'N/A'}")
    if isinstance(source._output, (list, tuple)) and len(source._output) > out_idx:
        print(f"    source._output[{out_idx}] sample: {source._output[out_idx][0] if source._output[out_idx] else 'EMPTY'}")

    # Most importantly - what does get_output return when called by this node?
    print(f"    get_output(test_node) returns: {source.get_output(test_node)}")
    if isinstance(source.get_output(test_node), list) and source.get_output(test_node):
        print(f"      First item: {source.get_output(test_node)[0]}")


# Cleanup
shutil.rmtree(test_dir)

print("\n=== DEBUG Complete ===")