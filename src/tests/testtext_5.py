import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType, NodeState
from core.print_node_info import print_node_info

def set_and_print(node, value):
    node._parms["text_string"].set(value)
    node.set_state(NodeState.UNCOOKED)
    node_name = node.name()
    print(f"\nSetting {node_name} text_string to: {value}")

# Create nodes (same as original)
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2")
text3 = Node.create_node(NodeType.TEXT, node_name="text3")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")
processor = Node.create_node(NodeType.TEXT, node_name="processor")

# Set up merge node inputs (same as original)
text1._parms["text_string"].set("apple")
text2._parms["text_string"].set("banana")
text3._parms["text_string"].set("cherry")
merge1.set_input(0, text1)
merge1.set_input(1, text2)
merge1.set_input(2, text3)
merge1._parms["single_string"].set(False)
processor.set_input(0, merge1)

print("#Test 1: Basic list syntax")
set_and_print(processor, '["prefix_", "suffix_"]')
result1 = processor.eval()
print(f"$Output: {result1}\n")

print("#Test 2: Mixed quotes")
set_and_print(processor, '["hello_", \'world_\']')
result2 = processor.eval()
print(f"$Output: {result2}\n")

print("#Test 3: Single item list vs plain string")
set_and_print(processor, '["single_"]')
result3a = processor.eval()
print(f"$Output: {result3a}")
set_and_print(processor, "single_")
result3b = processor.eval()
print(f"$Output: {result3b}\n")

print("#Test 4: Invalid syntax fallback")
set_and_print(processor, '["unclosed')
result4 = processor.eval()
print(f"$Output: {result4}\n")

print("#Test 5: List with per_item=False")
processor._parms["per_item"].set(False)
set_and_print(processor, '["start_", "end_"]')
result5 = processor.eval()
print(f"$Output: {result5}\n")

print("#Test 6: List with prefix=True")
processor._parms["prefix"].set(True)
set_and_print(processor, '["pre1_", "pre2_"]')
result6 = processor.eval()
print(f"$Output: {result6}\n")

print("#Test 7: List with pass_through=False")
processor._parms["pass_through"].set(False)
set_and_print(processor, '["lonely1_", "lonely2_"]')
result7 = processor.eval()
print(f"$Output: {result7}\n")

print("#Test 8: Empty list")
set_and_print(processor, '[]')
result8 = processor.eval()
print(f"$Output: {result8}\n")

print("#Test 9: List with empty strings")
set_and_print(processor, '["", "test_", ""]')
result9 = processor.eval()
print(f"$Output: {result9}\n")

print("#Test 10: Escaped quotes")
set_and_print(processor, '["escaped\\"quote_", "normal_"]')
result10 = processor.eval()
print(f"$Output: {result10}\n")

print_node_info(processor)