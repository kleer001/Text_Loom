import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *
from loop_manager import *

# Create nodes

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2", parent_path="/looper1")
text3 = Node.create_node(NodeType.TEXT, node_name="text3", parent_path="/looper1")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text -> $$N")
text1._parms["pass_through"].set(False)


text2._parms["text_string"].set("Poop Text 2")
text3._parms["text_string"].set("Lalala Text 3")
# Set merge node parameter
merge1._parms["single_string"].set(True)

# Connect nodes
looper1._output_node.set_input(0, text1, "output")
text1.set_input(0, merge1)
merge1.set_input(0, text2, "output")
merge1.set_input(1, text3, "output")

# print_node_info(text1)
# print_node_info(looper1)
# print_node_info(looper1._input_node)
# print_node_info(looper1._output_node)

print(":: LOOPER EVAL::")
loopeval = looper1.eval()
print("::LOOP EVALS TO::", loopeval)

# newtext = text1._parms["text_string"].eval()
# print("eval text1 text to : ", newtext)

# print_node_info(looper1._input_node)
# print_node_info(merge1)
# print_node_info(text1)
# print_node_info(looper1._output_node)
# print_node_info(looper1)

# print("looper evals to : ", looper1._output_node.eval())
