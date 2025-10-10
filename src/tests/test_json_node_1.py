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

print("\n=== Test 1: Basic Array Extraction ===")

text_node = Node.create_node(NodeType.TEXT, node_name="text1")
json_node = Node.create_node(NodeType.JSON, node_name="json1")

# Test extracting simple array
json_input = '{"items": ["apple", "banana", "cherry"]}'
text_node._parms["text_string"].set(json_input)
text_node._parms["pass_through"].set(False)

json_node.set_input(0, text_node)
json_node._parms["json_path"].set("items")

output = json_node.eval()
verify(output, ["apple", "banana", "cherry"], "Simple array extraction")

print("\n=== Test 2: Wildcard Path ===")

json_input2 = '{"users": [{"name": "Alice"}, {"name": "Bob"}]}'
text_node._parms["text_string"].set(json_input2)
text_node.set_state(NodeState.UNCOOKED)

json_node._parms["json_path"].set("users[*].name")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(output, ["Alice", "Bob"], "Wildcard path extraction")

print("\n=== Test 3: Extract Object Values ===")

json_input3 = '{"count": 42, "status": "ok", "active": true}'
text_node._parms["text_string"].set(json_input3)
text_node.set_state(NodeState.UNCOOKED)

json_node._parms["json_path"].set("")
json_node._parms["extraction_mode"].set("values")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(len(output), 3, "Values extraction count")
verify("42" in output, True, "Contains number value")
verify("ok" in output, True, "Contains string value")

print("\n=== Test 4: Extract Object Keys ===")

json_node._parms["extraction_mode"].set("keys")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(set(output), {"count", "status", "active"}, "Keys extraction")

print("\n=== Test 5: Flatten Mode ===")

json_input4 = '{"user": {"name": "Alice", "age": 30}}'
text_node._parms["text_string"].set(json_input4)
text_node.set_state(NodeState.UNCOOKED)

json_node._parms["json_path"].set("")
json_node._parms["extraction_mode"].set("flatten")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify("user.name: Alice" in output, True, "Flatten includes path")
verify("user.age: 30" in output, True, "Flatten includes nested value")

print("\n=== Test 6: JSON Format Output ===")

json_input5 = '{"items": [{"id": 1, "name": "Item1"}]}'
text_node._parms["text_string"].set(json_input5)
text_node.set_state(NodeState.UNCOOKED)

json_node._parms["json_path"].set("items")
json_node._parms["extraction_mode"].set("array")
json_node._parms["format_output"].set("json")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(len(output), 1, "JSON format output count")
verify('{"id": 1, "name": "Item1"}' in output[0] or '{"id":1,"name":"Item1"}' in output[0], True, "JSON format contains object")

print("\n=== Test 7: Error Handling - Invalid JSON ===")

text_node._parms["text_string"].set("not valid json")
text_node.set_state(NodeState.UNCOOKED)

json_node._parms["json_path"].set("")
json_node._parms["extraction_mode"].set("array")
json_node._parms["format_output"].set("raw")
json_node._parms["on_parse_error"].set("warn")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(output, [""], "Invalid JSON returns empty string")
verify(len(json_node.warnings()) > 0, True, "Invalid JSON generates warning")

print("\n=== Test 8: Error Handling - Passthrough ===")

json_node._parms["on_parse_error"].set("passthrough")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(output, ["not valid json"], "Passthrough returns original input")

print("\n=== Test 9: Nested Wildcard ===")

json_input6 = '{"users": [{"name": "Alice", "tags": ["admin", "user"]}, {"name": "Bob", "tags": ["user", "guest"]}]}'
text_node._parms["text_string"].set(json_input6)
text_node.set_state(NodeState.UNCOOKED)

json_node._parms["json_path"].set("users[*].tags[*]")
json_node._parms["on_parse_error"].set("warn")
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(output, ["admin", "user", "user", "guest"], "Nested wildcard flattens all tags")

print("\n=== Test 10: Enabled Toggle ===")

json_input7 = '{"data": "test"}'
text_node._parms["text_string"].set(json_input7)
text_node.set_state(NodeState.UNCOOKED)

json_node._parms["enabled"].set(False)
json_node.set_state(NodeState.UNCOOKED)

output = json_node.eval()
verify(output, [json_input7], "Disabled node passes through input")

print("\n=== Test Complete ===")