import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType, generate_node_types
from core.print_node_info import print_node_info
from core.looper_node import *

nodeTypes = generate_node_types()

text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2")

print("Initial state:")
print(f"text1 text_string is_default: {text1._parms['text_string'].is_default}")
print(f"text1 text_string default_value: {text1._parms['text_string'].default_value}")

text1._parms["text_string"].set("Filler Text 1")
print("\nAfter first set:")
print(f"text1 text_string is_default: {text1._parms['text_string'].is_default}")
print(f"text1 text_string default_value: {text1._parms['text_string'].default_value}")

text1._parms["text_string"].set("Filler Text 1")
print("\nAfter setting to same value:")
print(f"text1 text_string is_default: {text1._parms['text_string'].is_default}")

text1._parms["text_string"].set("Changed Text")
print("\nAfter changing value:")
print(f"text1 text_string is_default: {text1._parms['text_string'].is_default}")

text1._parms["text_string"].set("Filler Text 1")
print("\nAfter setting back to default:")
print(f"text1 text_string is_default: {text1._parms['text_string'].is_default}")

text2._parms["text_string"].set("Boopah Text 2")
text1.set_input(0, text2)

text1._parms["pass_through"].set(True)
print("\nPass through parameter check:")
print(f"pass_through is_default: {text1._parms['pass_through'].is_default}")
print(f"pass_through default_value: {text1._parms['pass_through'].default_value}")

texteval2 = text1.eval()
print("\nEval output:", texteval2)