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

print("\n=== Test 1: Case Transform Upper ===")

text_node = Node.create_node(NodeType.TEXT, node_name="text1")
transform_node = Node.create_node(NodeType.STRING_TRANSFORM, node_name="transform1")

text_node._parms["text_string"].set('["hello", "world"]')
text_node._parms["pass_through"].set(False)

transform_node.set_input(0, text_node)
transform_node._parms["operation"].set("case_transform")
transform_node._parms["case_mode"].set("upper")

output = transform_node.eval()
verify(output, ["HELLO", "WORLD"], "Case transform to uppercase")

print("\n=== Test 2: Case Transform Lower ===")

text_node._parms["text_string"].set('["HELLO", "WORLD"]')
text_node.set_state(NodeState.UNCOOKED)

transform_node._parms["case_mode"].set("lower")
transform_node.set_state(NodeState.UNCOOKED)

output = transform_node.eval()
verify(output, ["hello", "world"], "Case transform to lowercase")

print("\n=== Test 3: Find Replace ===")

text_node._parms["text_string"].set('["hello world", "hello universe"]')
text_node.set_state(NodeState.UNCOOKED)

transform_node._parms["operation"].set("find_replace")
transform_node._parms["find_text"].set("hello")
transform_node._parms["replace_text"].set("goodbye")
transform_node._parms["case_sensitive"].set(True)
transform_node.set_state(NodeState.UNCOOKED)

output = transform_node.eval()
verify(output, ["goodbye world", "goodbye universe"], "Simple find and replace")

print("\n=== Test 4: Case Insensitive Replace ===")

text_node._parms["text_string"].set('["HELLO world", "HeLLo universe"]')
text_node.set_state(NodeState.UNCOOKED)

transform_node._parms["case_sensitive"].set(False)
transform_node.set_state(NodeState.UNCOOKED)

output = transform_node.eval()
verify(output, ["goodbye world", "goodbye universe"], "Case insensitive replace")

print("\n=== Test 5: Trim Both ===")

text_node._parms["text_string"].set('["  hello  ", "  world  "]')
text_node.set_state(NodeState.UNCOOKED)

transform_node._parms["operation"].set("trim")
transform_node._parms["trim_mode"].set("both")
transform_node.set_state(NodeState.UNCOOKED)

output = transform_node.eval()
verify(output, ["hello", "world"], "Trim whitespace from both sides")

print("\n=== Test 6: Whitespace Normalize ===")

text_node._parms["text_string"].set('["hello    world", "too   many    spaces"]')
text_node.set_state(NodeState.UNCOOKED)

transform_node._parms["operation"].set("whitespace_normalize")
transform_node.set_state(NodeState.UNCOOKED)

output = transform_node.eval()
verify(output, ["hello world", "too many spaces"], "Normalize multiple spaces to single")

print("\n=== Test 7: Disabled Node ===")

text_node._parms["text_string"].set('["test"]')
text_node.set_state(NodeState.UNCOOKED)

transform_node._parms["enabled"].set(False)
transform_node.set_state(NodeState.UNCOOKED)

output = transform_node.eval()
verify(output, ["test"], "Disabled node passes through")

print("\n=== Test Complete ===")
