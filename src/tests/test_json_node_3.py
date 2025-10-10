import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

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

print("\n=== Test 6: JSON Error Recovery in Pipeline ===")

# Create mix of valid and invalid JSON documents
mixed_json = [
    '{"name": "Valid Item 1", "status": "ok"}',
    'this is not valid json at all',
    '{"name": "Valid Item 2", "status": "ok"}',
    '{"incomplete": "missing brace"',
    '{"name": "Valid Item 3", "status": "ok"}',
    'null',
    '{"name": "Valid Item 4", "status": "ok"}'
]

# Set up node network: Text -> Looper -> JSON (with error handling) -> Text -> Merge -> Output
text_input = Node.create_node(NodeType.TEXT, node_name="text_input")
looper = Node.create_node(NodeType.LOOPER, node_name="looper")
split_node = Node.create_node(NodeType.SPLIT, node_name="split_current", parent_path="/looper")
json_node = Node.create_node(NodeType.JSON, node_name="json_extract", parent_path="/looper")
text_format = Node.create_node(NodeType.TEXT, node_name="text_format", parent_path="/looper")

# Set up text node with all JSON documents
text_input._parms["text_string"].set(str(mixed_json))
text_input._parms["pass_through"].set(False)

# Connect to looper
looper.set_input(0, text_input)
looper._parms["max_from_input"].set(True)

# Inside looper: split to get current iteration's JSON
split_node.set_input(0, looper._input_node)
split_node._parms["split_expr"].set("[$$L]")

# Test 6a: Error handling with "warn" mode
print("\n--- Test 6a: Warn mode - skip invalid, continue processing ---")
json_node.set_input(0, split_node, output_index=0)
json_node._parms["json_path"].set("name")
json_node._parms["on_parse_error"].set("warn")
json_node._parms["extraction_mode"].set("array")

# Format with prefix
text_format.set_input(0, json_node)
text_format._parms["text_string"].set("Extracted: ")
text_format._parms["prefix"].set(True)

# Connect to looper output
looper._output_node.set_input(0, text_format)

# Evaluate
output = looper.eval()
print(f"\nLooper output (warn mode): {output}")

# Should have 7 items (one per input), but some will be empty strings for invalid JSON
verify(len(output), 7, "Processed all 7 items (warn mode)")

# Count how many valid extractions we got (non-empty, non-"Extracted: " only)
valid_items = [item for item in output if item != "Extracted: " and "Valid Item" in item]
verify(len(valid_items), 4, "Successfully extracted 4 valid items")

# Check warnings were generated
verify(len(json_node.warnings()) > 0, True, "Warnings generated for invalid JSON")

print("\n--- Test 6b: Passthrough mode - preserve invalid JSON ---")
# Clear previous warnings
json_node.clear_warnings()

json_node._parms["on_parse_error"].set("passthrough")
json_node.set_state(NodeState.UNCOOKED)
looper.set_state(NodeState.UNCOOKED)

output = looper.eval()
print(f"\nLooper output (passthrough mode): {output}")

# Should have 7 items, invalid ones should contain original text
verify(len(output), 7, "Processed all 7 items (passthrough mode)")

# Check that invalid JSON was passed through
has_invalid_text = any("not valid json" in item for item in output)
verify(has_invalid_text, True, "Invalid JSON passed through unchanged")

print("\n--- Test 6c: Empty mode - replace invalid with empty ---")
json_node._parms["on_parse_error"].set("empty")
json_node.set_state(NodeState.UNCOOKED)
looper.set_state(NodeState.UNCOOKED)

output = looper.eval()
print(f"\nLooper output (empty mode): {output}")

verify(len(output), 7, "Processed all 7 items (empty mode)")

# Count completely empty results (just the prefix)
empty_items = [item for item in output if item == "Extracted: "]
verify(len(empty_items), 3, "Invalid JSON replaced with empty strings")

print("\n=== Test 10: Max Depth Protection ===")

# Create deeply nested JSON structure
deep_json = '''{
  "level1": {
    "level2": {
      "level3": {
        "level4": {
          "level5": {
            "level6": {
              "value": "deep_value"
            }
          }
        }
      }
    }
  }
}'''

text_deep = Node.create_node(NodeType.TEXT, node_name="text_deep")
json_deep = Node.create_node(NodeType.JSON, node_name="json_deep")

text_deep._parms["text_string"].set(deep_json)
text_deep._parms["pass_through"].set(False)

json_deep.set_input(0, text_deep)

# Test 10a: Flatten with no depth limit (0 = unlimited)
print("\n--- Test 10a: Flatten with unlimited depth ---")
json_deep._parms["json_path"].set("")
json_deep._parms["extraction_mode"].set("flatten")
json_deep._parms["max_depth"].set(0)

output = json_deep.eval()
print(f"Flattened output (unlimited): {output}")

# Should traverse all the way to the deepest value
verify(len(output), 1, "Single leaf value found")
verify("level1.level2.level3.level4.level5.level6.value: deep_value" in output[0], True, "Full path to deep value")

# Test 10b: Flatten with depth limit of 2
print("\n--- Test 10b: Flatten with max_depth=2 ---")
json_deep._parms["max_depth"].set(2)
json_deep.set_state(NodeState.UNCOOKED)

output = json_deep.eval()
print(f"Flattened output (max_depth=2): {output}")

# Should stop at depth 2 and show the remaining structure
verify(len(output), 1, "Stopped at max depth")
# At depth 2, we should see level1.level2: {nested structure}
verify("level1.level2:" in output[0], True, "Stopped at depth 2")
verify("level6" not in output[0], False, "Did not traverse beyond max depth")

# Test 10c: Flatten with depth limit of 4
print("\n--- Test 10c: Flatten with max_depth=4 ---")
json_deep._parms["max_depth"].set(4)
json_deep.set_state(NodeState.UNCOOKED)

output = json_deep.eval()
print(f"Flattened output (max_depth=4): {output}")

verify(len(output), 1, "Stopped at max depth")
verify("level1.level2.level3.level4:" in output[0], True, "Stopped at depth 4")

# Test 10d: Max depth with array structure
print("\n--- Test 10d: Max depth with nested arrays ---")
nested_arrays = '''{
  "users": [
    {
      "name": "Alice",
      "projects": [
        {"title": "Project A", "tasks": [{"name": "Task 1"}, {"name": "Task 2"}]},
        {"title": "Project B", "tasks": [{"name": "Task 3"}]}
      ]
    }
  ]
}'''

text_deep._parms["text_string"].set(nested_arrays)
text_deep.set_state(NodeState.UNCOOKED)

json_deep._parms["max_depth"].set(3)
json_deep.set_state(NodeState.UNCOOKED)

output = json_deep.eval()
print(f"Flattened output (nested arrays, max_depth=3): {output}")

# Should show structure but not go into tasks array
verify(len(output) > 0, True, "Processed nested arrays")
verify(any("users[0]" in item for item in output), True, "Contains array notation")

print("\n=== Tests Complete ===")