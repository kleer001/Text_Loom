import sys, os
import shutil
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

# Test: FolderNode with Looper - Processing File Contents

test_dir = os.path.abspath("test_folder_3")
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

print("\n=== Test: FolderNode Contents → Looper → Split -> TextNode ===")

# Create test files with numbers
for i in range(5):
    with open(os.path.join(test_dir, f"file{i}.txt"), "w") as f:
        f.write(f"Number: {i}")

# Set up node network:
# FolderNode (contents output) -> Looper -> Split -> TextNode (adds prefix) -> Output
folder_node = Node.create_node(NodeType.FOLDER, node_name="folder")
looper = Node.create_node(NodeType.LOOPER, node_name="looper")
text_node = Node.create_node(NodeType.TEXT, node_name="text_prefix", parent_path="/looper")
split_node = Node.create_node(NodeType.SPLIT, node_name="split_current", parent_path="/looper")

# Configure FolderNode
folder_node._parms["folder_path"].set(test_dir)
folder_node._parms["pattern"].set("*.txt")
folder_node._parms["sort_by"].set("name")

# Connect FolderNode contents (output[0]) to Looper
looper.set_input(0, folder_node, output_index=0)

# Configure looper to iterate over all files
looper._parms["max_from_input"].set(True)

# Inside looper: split to get just current iteration's item
split_node.set_input(0, looper._input_node)
split_node._parms["split_expr"].set("[$$L]")  # Get item at current loop index

# Inside looper: add prefix to each file content
text_node.set_input(0, split_node, output_index=0)  # Connect to split's main output
text_node._parms["text_string"].set("PROCESSED: Loop - $$L, File = ")
text_node._parms["prefix"].set(True)
text_node._parms["per_item"].set(True)

# Connect text_node to looper output
looper._output_node.set_input(0, text_node)

# Evaluate
output = looper.eval()

print(f"\nLooper output: {output}")

# Verify all files were processed
verify(len(output), 5, "Looper processed all files")

# Verify prefix was added to each
all_have_prefix = all("PROCESSED:" in item for item in output)
verify(all_have_prefix, True, "All files have prefix")

# Verify original content is preserved
has_numbers = all(any(f"Number: {i}" in item for item in output) for i in range(5))
verify(has_numbers, True, "Original content preserved")

print("\n=== Test: FolderNode Filenames → Looper → Split -> TextNode ===")

# Connect FolderNode file names (output[1]) to Looper
looper.remove_input(0)
looper.set_input(0, folder_node, output_index=1)
#Change up text output
text_node._parms["text_string"].set("PROCESSED: Loop - $$L, FileName = ")

# Evaluate
output = looper.eval()

print(f"\nLooper output: {output}")

# Verify all files were processed
verify(len(output), 5, "Looper processed all files")

# Verify prefix was added to each
all_have_prefix = all("PROCESSED:" in item for item in output)
verify(all_have_prefix, True, "All files have prefix")

# Verify original content is preserved
has_numbers = all(any(f"file{i}.txt" in item for item in output) for i in range(5))
verify(has_numbers, True, "Original content preserved")


# Cleanup
shutil.rmtree(test_dir)

print("\n=== Test Complete ===")