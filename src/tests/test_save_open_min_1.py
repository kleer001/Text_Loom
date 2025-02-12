import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.flow_simple import save_flowstate, load_flowstate

print("Creating initial nodes...")
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2")

text1._parms["text_string"].set("Filler Text 1")
text2._parms["text_string"].set("Boopah Text 2")
text1.set_next_input(text2)

text1._parms["pass_through"].set(True)
print("\nEval with passthrough True:")
texteval2 = text1.eval()
print_node_info(text1)
print("text1 evals to:", texteval2)

text1._parms["pass_through"].set(False)
text1._parms["text_string"].set("CHANGED Filler Text 1")
text2._parms["text_string"].set("CHANGED Boopah Text 2")

print("\nEval with passthrough False:")
texteval = text1.eval()
print_node_info(text1)
print("text1 evals to:", texteval)

file_path = os.path.abspath("save_flow.txt")
print(f"\nSaving to {file_path}")
if not save_flowstate(file_path):
    print("Failed to save flow!")
    sys.exit(1)

print("\nChecking saved file exists:", os.path.exists(file_path))
with open(file_path, 'r') as f:
    print("File contents:")
    print(f.read())

print("\nClearing environment...")
env = NodeEnvironment.get_instance()
env.nodes.clear()

print("\nLoading saved flow...")
load_flowstate(file_path)

text1 = NodeEnvironment.node_from_name("/text1")
text2 = NodeEnvironment.node_from_name("/text2")

print("\nValidating loaded nodes:")
print_node_info(text1)
print_node_info(text2)

print("\nValidating evaluation:")
texteval = text1.eval()
print("text1 evals to:", texteval)