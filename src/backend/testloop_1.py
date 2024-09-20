import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *


# Create nodes

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text 1")
# Set merge node parameter

# Connect nodes
looper1._output_node.set_input(0, text1, "output")
text1.set_input(0, merge1)
merge1.set_input(0, looper1._input_node, "output")

# print_node_info(text1)
# print_node_info(looper1)
# print_node_info(looper1._input_node)
# print_node_info(looper1._output_node)

print(":: LOOPER EVAL::")
# text1.cook()
loopeval = looper1.eval()
print("::LOOP EVALS TO::", loopeval)

print_node_info(looper1._input_node)
print_node_info(merge1)
print_node_info(text1)
print_node_info(looper1._output_node)
print_node_info(looper1)

print("looper evals to : ", looper1._output_node.eval())
