import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType, NodeState
from core.print_node_info import print_node_info

# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2")
text3 = Node.create_node(NodeType.TEXT, node_name="text3")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")
processor = Node.create_node(NodeType.TEXT, node_name="processor")

# Set the parameters for text nodes
text1._parms["text_string"].set("apple")
text2._parms["text_string"].set("banana")
text3._parms["text_string"].set("cherry")

# Connect first three nodes to merge
merge1.set_input(0, text1)
merge1.set_input(1, text2)
merge1.set_input(2, text3)
merge1._parms["single_string"].set(False)

# Connect merge to our processing text node
processor.set_input(0, merge1)
processor._parms["text_string"].set("fruit_")

print("#Test 1: Default behavior (suffix per item)")
result1 = processor.eval()
print(f"$Output: {result1}\n")

print("#Test 2: Single item append mode")
processor._parms["per_item"].set(False)
processor.set_state(NodeState.UNCOOKED)
result2 = processor.eval()
print(f"$Output: {result2}\n")

print("#Test 3: Single item prepend mode")
processor._parms["prefix"].set(True)
processor.set_state(NodeState.UNCOOKED)
result3 = processor.eval()
print(f"$Output: {result3}\n")

print("#Test 4: Prefix per item mode")
processor._parms["per_item"].set(True)
processor.set_state(NodeState.UNCOOKED)
result4 = processor.eval()
print(f"$Output: {result4}\n")

print("#Test 5: No pass through")
processor._parms["pass_through"].set(False)
processor.set_state(NodeState.UNCOOKED)
result5 = processor.eval()
print(f"$Output: {result5}\n")

print("#Test 6: Change text and verify recook with all features")
processor._parms["pass_through"].set(True)
processor._parms["text_string"].set("tasty_")
processor.set_state(NodeState.UNCOOKED)
result6 = processor.eval()
print(f"$Output: {result6}\n")

print_node_info(processor)