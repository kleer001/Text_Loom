import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *


# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2", parent_path="/looper1")
text3 = Node.create_node(NodeType.TEXT, node_name="text3")

# Set the parameters for text nodes
text1._parms["text_string"].set("front-1 ")
text2._parms["text_string"].set("In@2 $$M+1")
text3._parms["text_string"].set(" END_TEXT_3")

# Connect nodes
looper1.set_input(0,text1)
text2.set_input(0, looper1._input_node)
looper1._output_node.set_input(0, text2)
text3.set_input(0, looper1)

print(":: LOOPER EVAL::")
endeval = text3.eval()
print("::TEXT3 EVALS TO::", endeval)

print_node_info(looper1._input_node)
#print_node_info(text2)
#print_node_info(text3)
#print_node_info(looper1._output_node)
#print_node_info(looper1)

#print("looper evals to : ", looper1._output_node.eval())
