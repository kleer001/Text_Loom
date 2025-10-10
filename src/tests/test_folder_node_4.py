import sys, os
import shutil
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

# Test: FolderNode with Looper - Processing File Names

test_dir = os.path.abspath("test_folder_4")
os.makedirs(test_dir, exist_ok=True)

def verify(actual, expected, name):
    if actual == expected:
        print(f"✅ {name} PASSED")
        print(f"Expected: {expected}")
        print(f"Got: {actual}")
    else:
        print(f"❌ {name} FAILED")
        print(f"Expected: {expected}")
        print(f"Got: {actual}")
        if isinstance(expected, list) and isinstance(actual, list):
            print(f"Length - Expected: {len(expected)}, Got: {len(actual)}")

print("\n=== Test: FolderNode Names → Looper → TextNode ===")

# Create test files
for i in range(5):
    with open(os.path.join(test_dir, f"document_{i}.txt"), "w") as f:
        f.write(f"Content {i}")

# Set up node network:
# FolderNode (names output) -> Looper -> Split -> TextNode (adds prefix) -> Output
folder_node = Node.create_node(NodeType.FOLDER, node_name="folder")
looper = Node.create_node(NodeType.LOOPER, node_name="looper")
text_node = Node.create_node(NodeType.TEXT, node_name="text_names", parent_path="/looper")
split_node = Node.create_node(NodeType.SPLIT, node_name="split_current", parent_path="/looper")

# Configure FolderNode
folder_node._parms["folder_path"].set(test_dir)
folder_node._parms["pattern"].set("*.txt")
folder_node._parms["sort_by"].set("name")

# Connect FolderNode names (output[1]) to Looper
looper.set_input(0, folder_node, output_index=1)

# Configure looper to iterate over all filenames
looper._parms["max_from_input"].set(True)

# Inside looper: connect split and add prefix to show we're processing filenames
split_node.set_input(0,looper._input_node,0)
split_node._parms["split_expr"].set("[$$L]")
text_node.set_input(0, split_node, 0)
text_node._parms["text_string"].set("Processing file: ")
text_node._parms["prefix"].set(True)
text_node._parms["per_item"].set(True)

# Connect text_node to looper output
looper._output_node.set_input(0, text_node)

# Evaluate
output = looper.eval()

print(f"\nLooper output: {output}")

# Verify we processed all filenames
verify(len(output), 5, "Looper processed all filenames")

# Verify all items contain filenames
has_filenames = all("document_" in item and ".txt" in item for item in output)
verify(has_filenames, True, "All items contain filenames")

# Verify prefix was added
has_prefix = all("Processing file:" in item for item in output)
verify(has_prefix, True, "All items have prefix")

# Verify they're in sorted order
filenames = [item.replace("Processing file: ", "").strip() for item in output]
basenames = [os.path.basename(f) for f in filenames]
verify(basenames, sorted(basenames), "Filenames are sorted")

# Cleanup
shutil.rmtree(test_dir)

print("\n=== Test Complete ===")