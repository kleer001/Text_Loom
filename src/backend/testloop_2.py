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
text4 = Node.create_node(NodeType.TEXT, node_name="text3", parent_path="/looper1")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")

# Set the parameters for text nodes
text1._parms["text_string"].set("I have $$N")
text1._parms["pass_through"].set(False)


text2._parms["text_string"].set(" 2 Apples ")
text3._parms["text_string"].set(" 3 Cherries")
text4._parms["text_string"].set(" 4 Eggplants")
# Set merge node parameter
merge1._parms["single_string"].set(False)

# Connect nodes
looper1._output_node.set_input(0, text1)
text1.set_input(0, merge1)
merge1.set_input(0, text2)
merge1.set_input(1, text3)
merge1.set_input(2, text4)

# print_node_info(text1)
# print_node_info(looper1)
# print_node_info(looper1._input_node)
# print_node_info(looper1._output_node)

print("\n:: LOOPER EVAL::")
loopeval = looper1.eval()
print("::LOOP EVALS TO::\n", loopeval)


# newtext = text1._parms["text_string"].eval()
# print("eval text1 text to : ", newtext)

#print("merge1 evals to : ", merge1.eval())
#print("text1 vars = ",vars(text1))
# print_node_info(looper1._input_node)
#print_node_info(merge1)
# print_node_info(text1)
print_node_info(looper1._output_node)
# print_node_info(looper1)

# print("looper evals to : ", looper1._output_node.eval())
