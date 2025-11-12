import sys, os
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(parent_dir, 'src'))

from core.base_classes import Node, NodeType

text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2")
text3 = Node.create_node(NodeType.TEXT, node_name="text3")
merge = Node.create_node(NodeType.MERGE, node_name="merge")

text1._parms["text_string"].set("input1")
text2._parms["text_string"].set("input2")
text3._parms["text_string"].set("input3")

print("Initial state (0 connections):")
print(f"  Input connectors: {list(merge.input_names().keys())}")
print(f"  Expected: [0] (one open connector)")
assert list(merge.input_names().keys()) == [0], "Should have 1 connector when no connections"

merge.set_input(0, text1)
print("\nAfter connecting text1 to index 0:")
print(f"  Active connections: {len(merge.inputs())}")
print(f"  Input connectors: {list(merge.input_names().keys())}")
print(f"  Expected: [0, 1] (connector 0 connected, connector 1 open)")
assert list(merge.input_names().keys()) == [0, 1], "Should have 2 connectors with 1 connection"

merge.set_input(1, text2)
print("\nAfter connecting text2 to index 1:")
print(f"  Active connections: {len(merge.inputs())}")
print(f"  Input connectors: {list(merge.input_names().keys())}")
print(f"  Expected: [0, 1, 2] (connectors 0,1 connected, connector 2 open)")
assert list(merge.input_names().keys()) == [0, 1, 2], "Should have 3 connectors with 2 connections"

merge.set_input(2, text3)
print("\nAfter connecting text3 to index 2:")
print(f"  Active connections: {len(merge.inputs())}")
print(f"  Input connectors: {list(merge.input_names().keys())}")
print(f"  Expected: [0, 1, 2, 3] (connectors 0,1,2 connected, connector 3 open)")
assert list(merge.input_names().keys()) == [0, 1, 2, 3], "Should have 4 connectors with 3 connections"

connections = merge.inputs()
merge.remove_connection(connections[1])
print("\nAfter removing connection at index 1:")
print(f"  Active connections: {len(merge.inputs())}")
print(f"  Input connectors: {list(merge.input_names().keys())}")
print(f"  Expected: [0, 1, 2] (2 connections remain, one open connector)")
assert list(merge.input_names().keys()) == [0, 1, 2], "Should have 3 connectors with 2 connections"

print("\n✓ All dynamic connector tests passed!")
