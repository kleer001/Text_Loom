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

print("\n=== Test 1: Character Chunking ===")

text_node = Node.create_node(NodeType.TEXT, node_name="text1")
chunk_node = Node.create_node(NodeType.CHUNK, node_name="chunk1")

text_node._parms["text_string"].set('["abcdefghij"]')
text_node._parms["pass_through"].set(False)

chunk_node.set_input(0, text_node)
chunk_node._parms["chunk_mode"].set("character")
chunk_node._parms["chunk_size"].set(5)
chunk_node._parms["overlap_size"].set(0)
chunk_node._parms["respect_boundaries"].set(False)
chunk_node._parms["min_chunk_size"].set(1)

output = chunk_node.eval()
verify(len(output), 2, "Character chunking creates 2 chunks")
verify(output[0], "abcde", "First chunk is correct")
verify(output[1], "fghij", "Second chunk is correct")

print("\n=== Test 2: Character Chunking with Overlap ===")

text_node._parms["text_string"].set('["abcdefghij"]')
text_node.set_state(NodeState.UNCOOKED)

chunk_node._parms["chunk_size"].set(6)
chunk_node._parms["overlap_size"].set(2)
chunk_node.set_state(NodeState.UNCOOKED)

output = chunk_node.eval()
verify(output[0], "abcdef", "First chunk with overlap")
verify(len(output[1]) <= 6, True, "Second chunk respects size limit")

print("\n=== Test 3: Sentence Chunking ===")

text_node._parms["text_string"].set('["First sentence. Second sentence. Third sentence. Fourth sentence."]')
text_node.set_state(NodeState.UNCOOKED)

chunk_node._parms["chunk_mode"].set("sentence")
chunk_node._parms["chunk_size"].set(40)
chunk_node._parms["overlap_size"].set(0)
chunk_node.set_state(NodeState.UNCOOKED)

output = chunk_node.eval()
verify(len(output) >= 1, True, "Sentence chunking creates chunks")

print("\n=== Test 4: Paragraph Chunking ===")

text_node._parms["text_string"].set('["Para 1 text.\\n\\nPara 2 text.\\n\\nPara 3 text."]')
text_node.set_state(NodeState.UNCOOKED)

chunk_node._parms["chunk_mode"].set("paragraph")
chunk_node._parms["chunk_size"].set(100)
chunk_node.set_state(NodeState.UNCOOKED)

output = chunk_node.eval()
verify(len(output) >= 1, True, "Paragraph chunking creates chunks")

print("\n=== Test 5: Metadata Addition ===")

text_node._parms["text_string"].set('["abcdefghij"]')
text_node.set_state(NodeState.UNCOOKED)

chunk_node._parms["chunk_mode"].set("character")
chunk_node._parms["chunk_size"].set(5)
chunk_node._parms["overlap_size"].set(0)
chunk_node._parms["min_chunk_size"].set(1)
chunk_node._parms["add_metadata"].set(True)
chunk_node.set_state(NodeState.UNCOOKED)

output = chunk_node.eval()
verify("Chunk 1/" in output[0], True, "Metadata added to first chunk")
verify("Chunk 2/" in output[1], True, "Metadata added to second chunk")

print("\n=== Test 6: Disabled Node ===")

text_node._parms["text_string"].set('["test"]')
text_node.set_state(NodeState.UNCOOKED)

chunk_node._parms["enabled"].set(False)
chunk_node.set_state(NodeState.UNCOOKED)

output = chunk_node.eval()
verify(output, ["test"], "Disabled node passes through")

print("\n=== Test Complete ===")
