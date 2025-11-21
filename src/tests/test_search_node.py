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

print("\n=== Test 1: Contains Search ===")

text_node = Node.create_node(NodeType.TEXT, node_name="text1")
search_node = Node.create_node(NodeType.SEARCH, node_name="search1")

text_node._parms["text_string"].set('["apple pie", "banana split", "cherry tart"]')
text_node._parms["pass_through"].set(False)

search_node.set_input(0, text_node)
search_node._parms["search_text"].set("pie")
search_node._parms["search_mode"].set("contains")

output = search_node.eval()
verify(output[0], ["apple pie"], "Contains search finds matching items")
verify(len(output[1]), 2, "Non-matching items in second output")

print("\n=== Test 2: Case Insensitive Search ===")

text_node._parms["text_string"].set('["APPLE", "banana", "Cherry"]')
text_node.set_state(NodeState.UNCOOKED)

search_node._parms["search_text"].set("apple")
search_node._parms["case_sensitive"].set(False)
search_node.set_state(NodeState.UNCOOKED)

output = search_node.eval()
verify(output[0], ["APPLE"], "Case insensitive search finds APPLE")

print("\n=== Test 3: Exact Match ===")

text_node._parms["text_string"].set('["apple", "apple pie", "pineapple"]')
text_node.set_state(NodeState.UNCOOKED)

search_node._parms["search_text"].set("apple")
search_node._parms["search_mode"].set("exact")
search_node._parms["case_sensitive"].set(True)
search_node.set_state(NodeState.UNCOOKED)

output = search_node.eval()
verify(output[0], ["apple"], "Exact match finds only exact item")

print("\n=== Test 4: Starts With ===")

text_node._parms["text_string"].set('["apple pie", "banana", "cherry"]')
text_node.set_state(NodeState.UNCOOKED)

search_node._parms["search_text"].set("app")
search_node._parms["search_mode"].set("starts_with")
search_node.set_state(NodeState.UNCOOKED)

output = search_node.eval()
verify(output[0], ["apple pie"], "Starts with finds matching item")

print("\n=== Test 5: Ends With ===")

text_node._parms["text_string"].set('["apple pie", "banana split", "cherry"]')
text_node.set_state(NodeState.UNCOOKED)

search_node._parms["search_text"].set("pie")
search_node._parms["search_mode"].set("ends_with")
search_node.set_state(NodeState.UNCOOKED)

output = search_node.eval()
verify(output[0], ["apple pie"], "Ends with finds matching item")

print("\n=== Test 6: OR Boolean Mode ===")

text_node._parms["text_string"].set('["apple", "banana", "cherry"]')
text_node.set_state(NodeState.UNCOOKED)

search_node._parms["search_text"].set("apple banana")
search_node._parms["search_mode"].set("contains")
search_node._parms["boolean_mode"].set("OR")
search_node.set_state(NodeState.UNCOOKED)

output = search_node.eval()
verify(len(output[0]), 2, "OR mode finds both matching items")

print("\n=== Test 7: Invert Match ===")

text_node._parms["text_string"].set('["apple", "banana", "cherry"]')
text_node.set_state(NodeState.UNCOOKED)

search_node._parms["search_text"].set("apple")
search_node._parms["search_mode"].set("contains")
search_node._parms["boolean_mode"].set("OR")
search_node._parms["invert_match"].set(True)
search_node.set_state(NodeState.UNCOOKED)

output = search_node.eval()
verify(output[0], ["banana", "cherry"], "Invert match returns non-matching items")

print("\n=== Test 8: Disabled Node ===")

text_node._parms["text_string"].set('["test"]')
text_node.set_state(NodeState.UNCOOKED)

search_node._parms["enabled"].set(False)
search_node.set_state(NodeState.UNCOOKED)

output = search_node.eval()
verify(output, ["test"], "Disabled node passes through first output")

print("\n=== Test Complete ===")
