import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *
from flowstate_manager import *

# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text 1")
text2._parms["text_string"].set("Boopah Text 2")
# Connect nodes

text1.set_input(0, text2)

#print_node_info(text1)
#print_node_info(text2)

text1._parms["pass_through"].set(True)
print(":: EVAL True passthrough::")
texteval2 = text1.eval()
print_node_info(text1)
print("text1 evals to: \n",texteval2)


text1._parms["pass_through"].set(False)
text1._parms["text_string"].set("CHANGED Filler Text 1")
text2._parms["text_string"].set("CHAGNED Boopah Text 2")

print(":: EVAL False passthrough::")
texteval = text1.eval()
print_node_info(text1)
print("text1 evals to: \n",texteval)

# Set up save file
file_path = os.path.abspath("save_file_2.json")
save_flowstate(filepath=file_path)

