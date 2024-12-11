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
prefixer = Node.create_node(NodeType.TEXT, node_name="prefixer")

# Set the parameters for text nodes
text1._parms["text_string"].set("apple")
text2._parms["text_string"].set("banana")
text3._parms["text_string"].set("cherry")

# Connect first three nodes to merge
merge1.set_input(0, text1)
merge1.set_input(1, text2)
merge1.set_input(2, text3)
merge1._parms["single_string"].set(False)

# Connect merge to our prefix-capable text node
prefixer.set_input(0, merge1)
prefixer._parms["text_string"].set("fruit_")

print("#Test 1: Default behavior (no prefix)")
result1 = prefixer.eval()
print(f"$Output: {result1}\n")

print("#Test 2: With prefix enabled")
prefixer._parms["prefix"].set(True)
prefixer.set_state(NodeState.UNCOOKED)
result2 = prefixer.eval()
print(f"$Output: {result2}\n")

print("#Test 3: With pass_through disabled")
prefixer._parms["pass_through"].set(False)
prefixer.set_state(NodeState.UNCOOKED)
result3 = prefixer.eval()
print(f"$Output: {result3}\n")

print("#Test 4: Change prefix text and re-run with pass_through enabled")
prefixer._parms["pass_through"].set(True)
prefixer._parms["text_string"].set("tasty_")
prefixer.set_state(NodeState.UNCOOKED)
result4 = prefixer.eval()
print(f"$Output: {result4}\n")

print_node_info(prefixer)