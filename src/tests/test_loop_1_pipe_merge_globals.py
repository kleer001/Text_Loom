import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.looper_node import *
from core.global_store import GlobalStore

globalstore = GlobalStore()
globalstore.set("ACTORS", "3")
print("Globals are: ", globalstore.list())

# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text1b = Node.create_node(NodeType.TEXT, node_name="text1b")
text1c = Node.create_node(NodeType.TEXT, node_name="text1c")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")
looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2", parent_path="/looper1")
text3 = Node.create_node(NodeType.TEXT, node_name="text3")

# Set the parameters for text nodes
text1._parms["text_string"].set("front-A ")
text1b._parms["text_string"].set("start-B ")
text1c._parms["text_string"].set("head-C ")
merge1._parms["single_string"].set(False)
text2._parms["text_string"].set("In@2 $$N+$ACTORS")
text2._parms["pass_through"].set(False)
text3._parms["text_string"].set(" END_TEXT_3")

# Connect nodes
merge1.set_input(0,text1)
merge1.set_input(1,text1b)
merge1.set_input(2,text1c)
looper1.set_input(0,merge1)
text2.set_input(0, looper1._input_node)
looper1._output_node.set_input(0, text2)
text3.set_input(0, looper1)

print(":: LOOPER EVAL::")
endeval = text3.eval()
print("::TEXT3 EVALS TO::", endeval)

print_node_info(looper1._input_node)
print_node_info(text2)
#print_node_info(text3)
#print_node_info(looper1._output_node)
#print_node_info(looper1)

#print("looper evals to : ", looper1._output_node.eval())
