import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *

from global_store import GlobalStore

globals = GlobalStore()

# set global variables 
globals.set("FOO", 9)
globals.set("BAR", 42)

print("Globals are: " , globals.list())


# Create nodes

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")

text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2", parent_path="/looper1")
#text3 = Node.create_node(NodeType.TEXT, node_name="text3", parent_path="/looper1")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")
text4 = Node.create_node(NodeType.TEXT, node_name="text4", parent_path="/looper1")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text 1")
text2._parms["text_string"].set("Filler Text 2")
#text3._parms["text_string"].set("Filler Text 3")
text4._parms["text_string"].set("Text4. Input text: $$M*$FOO+$BAR")

# Set merge node parameter
merge1._parms["single_string"].set(False)

# Connect nodes
merge1.set_input(0, text1, "output")
merge1.set_input(1, text2, "output")
#merge1.set_input(2, text3, "output")
text4.set_input(0, merge1, "output")

#text1.set_input(0,looper1._input_node,"output")
#text2.set_input(0,looper1._input_node, "output")
#text3.set_input(0,looper1._input_node)

looper1._output_node.set_input(0,text4,"output")

# print_node_info(text1)
# print_node_info(text2)
# print_node_info(merge1)
# print("merged output = ",merge1._merged_output)
# print_node_info(text4)
# print_node_info(looper1._input_node)
# print_node_info(looper1._output_node)

# print_node_info(looper1)
print(":: LOOPER EVAL::")
loopeval = looper1.eval()


print_node_info(merge1)
print("merged output = ",merge1._merged_output)
# print_node_info(text4)
# print_node_info(looper1._input_node)
# print_node_info(looper1._output_node)

# print_node_info(looper1)


#print(NodeEnvironment.list_nodes())

# print(loopeval)

# print_node_info(text4)