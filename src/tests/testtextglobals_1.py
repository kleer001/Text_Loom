import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.looper_node import *
from core.global_store import GlobalStore

globals = GlobalStore()

# set global variables 
globals.set("AB", 6)
globals.set("FOO", "apples")
globals.set("BAR", 42)

print("Globals are: " , globals.list())

# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text $FOO and $BAR AND printing -> `ascii(\"$FOO\")` ")
# Connect nodes
#text1.set_input(0, text2)

#print_node_info(text1)
#print_node_info(text2)

print_node_info(text1)
evaltext = text1._parms["text_string"].eval()
print("text1 evals to: \n",evaltext)




