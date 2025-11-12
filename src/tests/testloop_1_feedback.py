import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.looper_node import *


# Create nodes

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text $$L ")
looper1._parms["feedback_mode"].set(True)

# Connect nodes
looper1._output_node.set_input(0, text1, 0)
text1.set_input(0, merge1)
merge1.set_input(0, looper1._input_node, 0)

# print_node_info(text1)
# print_node_info(looper1)
# print_node_info(looper1._input_node)
# print_node_info(looper1._output_node)

print(":: LOOPER EVAL::")
# text1.cook()
loopeval = looper1.eval()
print("::LOOP EVALS TO::", loopeval)

# #print_node_info(looper1._input_node)
# print_node_info(merge1)
# print_node_info(text1)
# print_node_info(looper1._output_node)
# #print_node_info(looper1)

#print("looper evals to : ", looper1._output_node.eval())
