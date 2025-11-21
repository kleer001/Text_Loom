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

print("\n=== Test 1: Count Items ===")

text_node = Node.create_node(NodeType.TEXT, node_name="text1")
count_node = Node.create_node(NodeType.COUNT, node_name="count1")

text_node._parms["text_string"].set('["apple", "banana", "cherry"]')
text_node._parms["pass_through"].set(False)

count_node.set_input(0, text_node)
count_node._parms["stat_mode"].set("count")
count_node._parms["count_what"].set("items")
count_node._parms["format_output"].set("plain")

output = count_node.eval()
verify(output, ["3"], "Count items in list")

print("\n=== Test 2: Count Words ===")

text_node._parms["text_string"].set('["hello world", "foo bar baz"]')
text_node.set_state(NodeState.UNCOOKED)

count_node._parms["count_what"].set("words")
count_node.set_state(NodeState.UNCOOKED)

output = count_node.eval()
verify(output, ["5"], "Count total words")

print("\n=== Test 3: Count Characters ===")

text_node._parms["text_string"].set('["abc", "de"]')
text_node.set_state(NodeState.UNCOOKED)

count_node._parms["count_what"].set("characters")
count_node.set_state(NodeState.UNCOOKED)

output = count_node.eval()
verify(output, ["5"], "Count total characters")

print("\n=== Test 4: Deduplicate Preserve Order ===")

text_node._parms["text_string"].set('["apple", "banana", "apple", "cherry", "banana"]')
text_node.set_state(NodeState.UNCOOKED)

count_node._parms["stat_mode"].set("deduplicate")
count_node._parms["preserve_order"].set(True)
count_node.set_state(NodeState.UNCOOKED)

output = count_node.eval()
verify(output, ["apple", "banana", "cherry"], "Deduplicate preserving order")

print("\n=== Test 5: Deduplicate Case Insensitive ===")

text_node._parms["text_string"].set('["Apple", "APPLE", "apple"]')
text_node.set_state(NodeState.UNCOOKED)

count_node._parms["case_sensitive"].set(False)
count_node.set_state(NodeState.UNCOOKED)

output = count_node.eval()
verify(len(output), 1, "Deduplicate case insensitive")

print("\n=== Test 6: Word Frequency ===")

text_node._parms["text_string"].set('["hello world hello", "world test"]')
text_node.set_state(NodeState.UNCOOKED)

count_node._parms["stat_mode"].set("word_freq")
count_node._parms["case_sensitive"].set(False)
count_node._parms["format_output"].set("plain")
count_node.set_state(NodeState.UNCOOKED)

output = count_node.eval()
verify("hello: 2" in output, True, "Word frequency contains hello: 2")
verify("world: 2" in output, True, "Word frequency contains world: 2")

print("\n=== Test 7: Disabled Node ===")

text_node._parms["text_string"].set('["test"]')
text_node.set_state(NodeState.UNCOOKED)

count_node._parms["enabled"].set(False)
count_node.set_state(NodeState.UNCOOKED)

output = count_node.eval()
verify(output, ["test"], "Disabled node passes through")

print("\n=== Test Complete ===")
