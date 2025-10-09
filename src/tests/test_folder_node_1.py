import sys, os
import shutil
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

# Test: Error handling, sorting, pattern matching

test_dir = os.path.abspath("test_folder_1")
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

print("\n=== Test 1: Pattern Matching ===")

# Create test files
with open(os.path.join(test_dir, "alpha.txt"), "w") as f:
    f.write("Alpha content")
with open(os.path.join(test_dir, "beta.txt"), "w") as f:
    f.write("Beta content")
with open(os.path.join(test_dir, "gamma.md"), "w") as f:
    f.write("Gamma content")
with open(os.path.join(test_dir, "delta.py"), "w") as f:
    f.write("Delta content")

folder_node = Node.create_node(NodeType.FOLDER, node_name="folder_test")
folder_node._parms["folder_path"].set(test_dir)
folder_node._parms["pattern"].set("*.txt")

output = folder_node.eval()
verify(len(output[0]), 2, "Pattern *.txt file count")
verify(output[2], ['', ''], "Pattern *.txt no errors")

# Test different pattern
folder_node._parms["pattern"].set("*.md")
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
verify(len(output[0]), 1, "Pattern *.md file count")
verify("Gamma content" in output[0], True, "Pattern *.md content check")

# Test regex pattern
folder_node._parms["pattern"].set("^alpha.*\.txt")
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
verify(len(output[0]), 1, "Regex pattern file count")
verify("Alpha content" in output[0], True, "Regex pattern content check")

print("\n=== Test 2: Sorting ===")

# Create timestamped files
import time
with open(os.path.join(test_dir, "first.txt"), "w") as f:
    f.write("First")
time.sleep(0.01)
with open(os.path.join(test_dir, "second.txt"), "w") as f:
    f.write("Second")
time.sleep(0.01)
with open(os.path.join(test_dir, "third.txt"), "w") as f:
    f.write("Third")

# Sort by name ascending
folder_node._parms["pattern"].set("*.txt")
folder_node._parms["sort_by"].set("name")
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
filenames = [os.path.basename(f) for f in output[1]]
verify(filenames, sorted(filenames), "Sort by name ascending")

# Sort by name descending
folder_node._parms["sort_by"].set("name_desc")
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
filenames = [os.path.basename(f) for f in output[1]]
verify(filenames, sorted(filenames, reverse=True), "Sort by name descending")

# Sort by date descending (most recent first)
folder_node._parms["sort_by"].set("date_desc")
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()
# third.txt should be first (most recent)
verify("third.txt" in output[1][0], True, "Sort by date descending - newest first")

print("\n=== Test 3: Error Handling ===")

# Create unreadable file (on Unix systems)
unreadable_file = os.path.join(test_dir, "unreadable.txt")
with open(unreadable_file, "w") as f:
    f.write("Secret content")
os.chmod(unreadable_file, 0o000)

folder_node._parms["pattern"].set("*.txt")
folder_node._parms["on_error"].set("warn")
folder_node.set_state(NodeState.UNCOOKED)
output = folder_node.eval()

# Should have some errors but continue processing
has_errors = any(err != '' for err in output[2])
verify(has_errors, True, "Error handling - warnings present")
verify(len(output[0]) > 0, True, "Error handling - some files processed")

# Test with non-existent directory
folder_node._parms["folder_path"].set("/nonexistent/path")
folder_node.set_state(NodeState.UNCOOKED)
try:
    output = folder_node.eval()
    verify(len(folder_node.errors()) > 0, True, "Error handling - invalid path generates error")
except:
    print("✅ Error handling - invalid path PASSED (exception raised)")

# Cleanup
os.chmod(unreadable_file, 0o644)
shutil.rmtree(test_dir)

print("\n=== Test Complete ===")