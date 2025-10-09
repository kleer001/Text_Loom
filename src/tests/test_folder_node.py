import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

# Create test directory with sample files
test_dir = os.path.abspath("test_folder")
os.makedirs(test_dir, exist_ok=True)

# Create test files
with open(os.path.join(test_dir, "file1.txt"), "w") as f:
    f.write("Content of file 1")

with open(os.path.join(test_dir, "file2.txt"), "w") as f:
    f.write("Content of file 2")

with open(os.path.join(test_dir, "file3.md"), "w") as f:
    f.write("Markdown content")

# Create FolderNode
folder_node = Node.create_node(NodeType.FOLDER, node_name="folder_test")
folder_node._parms["folder_path"].set(test_dir)
folder_node._parms["pattern"].set("*.txt")

# Evaluate
output = folder_node.eval()

print("\n=== FolderNode Test ===")
print(f"Folder path: {test_dir}")
print(f"Pattern: *.txt")
print(f"\nContents output: {output[0]}")
print(f"\nNames output: {output[1]}")
print(f"\nErrors output: {output[2]}")

# Cleanup
import shutil
shutil.rmtree(test_dir)

print("\n=== Test Complete ===")