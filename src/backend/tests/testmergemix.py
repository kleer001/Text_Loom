import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *


# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2")
text3 = Node.create_node(NodeType.TEXT, node_name="text3")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")

# Set the parameters for text nodes
text1._parms["text_string"].set("filler1")
text2._parms["text_string"].set("filler2")
text3._parms["text_string"].set("filler3")
# Connect nodes

merge1.set_input(0, text1)
merge1.set_input(1, text2)
merge1.set_input(2, text3)

#print_node_info(text1)
#print_node_info(text2)

pass1 = merge1.eval()
print(pass1)
print_node_info(merge1)

print("\n \n")
merge1._parms["use_insert"].set(True)

merge1.set_state(NodeState.UNCOOKED)

pass2 = merge1.eval()

for a in pass2:
    print(a)

print_node_info(merge1)

# text1._parms["pass_through"].set(True)
# print(":: EVAL True passthrough::")
# texteval2 = text1.eval()
# print_node_info(text1)
# print("text1 evals to: \n",texteval2)


# text1._parms["pass_through"].set(False)
# text1._parms["text_string"].set("CHANGED Filler Text 1")
# text2._parms["text_string"].set("CHAGNED Boopah Text 2")

# print(":: EVAL False passthrough::")
# texteval = text1.eval()
# print_node_info(text1)
# print("text1 evals to: \n",texteval)

