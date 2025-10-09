import sys, os
import shutil
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

# Test: Recursive directory scanning, filtering

test_dir = os.path.abspath("test_folder_2")
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

print("\n=== Test 1: Recursive Directory Scanning ===")

# Create nested directory structure
subdir1 = os.path.join(test_dir, "subdir1")
subdir2 = os.path.join(test_dir, "subdir2")
nested = os.path.join(subdir1, "nested")
os.makedirs(subdir1, exist_ok=True)
os.makedirs(subdir2, exist_ok=True)
os.makedirs(nested, exist_ok=True)

# Create files at different levels
with open(os.path.join(test_dir, "root.txt"), "w") as f:
    f.write("Root level")
with open(os.path.join(subdir1, "sub1.txt"), "w") as f:
    f.write("Subdir 1")
with open(os.path.join(subdir2, "sub2.txt"), "w") as f:
    f.write("Subdir 2")
with open(os.path.join(nested, "deep.txt"), "w") as f:
    f.write("Deep nested")

folder_node = Node.create_node(NodeType.FOLDER, node_name="folder_test")
folder_node._parms["folder_path"].set(test_dir)
folder_node._parms["pattern"].set("*.txt")
folder_node._parms["recursive"].set(False)

# Non-recursive: should only find root.txt
output = folder_node.eval()
verify(len(output[0]), 1, "Non-recursive scan file count")
verify("Root level" in output[0], True, "Non-recursive content check")

# Recursive: should find all 4 files
folder_node._parms["recursive"].set(True)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
verify(len(output[0]), 4, "Recursive scan file count")
verify("Deep nested" in output[0], True, "Recursive deep file found")

print("\n=== Test 2: Size Filtering ===")

# Create files of different sizes
small_file = os.path.join(test_dir, "small.txt")
medium_file = os.path.join(test_dir, "medium.txt")
large_file = os.path.join(test_dir, "large.txt")

with open(small_file, "w") as f:
    f.write("X" * 10)  # 10 bytes

with open(medium_file, "w") as f:
    f.write("X" * 100)  # 100 bytes

with open(large_file, "w") as f:
    f.write("X" * 1000)  # 1000 bytes

folder_node._parms["recursive"].set(False)
folder_node._parms["min_size"].set(50)
folder_node._parms["max_size"].set(500)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()

# Should only find medium.txt (100 bytes)
verify(len(output[0]), 1, "Size filtering file count")
verify("medium.txt" in output[1][0], True, "Size filtering correct file")

# Test min_size only
folder_node._parms["min_size"].set(100)
folder_node._parms["max_size"].set(0)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
verify(len(output[0]) >= 2, True, "Min size filtering (100+)")

# Test max_size only
folder_node._parms["min_size"].set(0)
folder_node._parms["max_size"].set(100)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
# Should find small.txt and possibly others <= 100 bytes
verify(len(output[0]) >= 1, True, "Max size filtering (<=100)")

print("\n=== Test 3: Max Files Limit ===")

# Create many files
for i in range(10):
    with open(os.path.join(test_dir, f"file{i:02d}.txt"), "w") as f:
        f.write(f"Content {i}")

folder_node._parms["min_size"].set(0)
folder_node._parms["max_size"].set(0)
folder_node._parms["max_files"].set(5)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
verify(len(output[0]), 5, "Max files limit")

# Test with max_files = 0 (unlimited)
folder_node._parms["max_files"].set(0)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
verify(len(output[0]) > 5, True, "Unlimited files (max_files=0)")

print("\n=== Test 4: Hidden Files ===")

# Create hidden file
hidden_file = os.path.join(test_dir, ".hidden.txt")
with open(hidden_file, "w") as f:
    f.write("Hidden content")

folder_node._parms["max_files"].set(0)
folder_node._parms["include_hidden"].set(False)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
has_hidden = any(".hidden.txt" in name for name in output[1])
verify(has_hidden, False, "Hidden files excluded by default")

# Include hidden files
folder_node._parms["include_hidden"].set(True)
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
has_hidden = any(".hidden.txt" in name for name in output[1])
verify(has_hidden, True, "Hidden files included when enabled")

# Cleanup
shutil.rmtree(test_dir)

print("\n=== Test Complete ===")