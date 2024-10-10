import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *
from global_store import GlobalStore

globals = GlobalStore()

#set global variables 
globals.set("AB", 6)
globals.set("FOO", "apples")
globals.set("BAR", 69)
# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text ${$FOO and $BAR}")
# Connect nodes
#text1.set_input(0, text2)

#print_node_info(text1)
#print_node_info(text2)

print(":: EVAL ::")
texteval = text1.cook()
print_node_info(text1)
evaltext = text1._parms["text_string"].eval()
print("text1 evals to: \n",evaltext)


# text1._parms["pass_through"].set(False)
# text1._parms["text_string"].set("CHANGED Filler Text 1")
# text2._parms["text_string"].set("CHAGNED Boopah Text 2")

# print(":: EVAL False passthrough::")
# texteval = text1.eval()
# print_node_info(text1)
# print("text1 evals to: \n",texteval)

