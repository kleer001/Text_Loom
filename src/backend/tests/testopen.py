import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from nodes.looper_node import *
from loop_manager import *
from flowstate_manager import *
from global_store import GlobalStore
# from undo_manager import UndoManager

# Set up save file
file_path = os.path.abspath("save_file.json")

load_flowstate(filepath=file_path)

global_store = GlobalStore()
# # set global variables 
# globals.set("AB", 6)
# globals.set("FOO", "apples")
# globals.set("BAR", 42)

print("Globals are: " , global_store.list())

print(NodeEnvironment.list_nodes())

merge1 = NodeEnvironment.node_from_name("merge1")

print_node_info(merge1)

# Create nodes

# looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
# text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")
# text2 = Node.create_node(NodeType.TEXT, node_name="text2", parent_path="/looper1")
# text3 = Node.create_node(NodeType.TEXT, node_name="text3", parent_path="/looper1")
# text4 = Node.create_node(NodeType.TEXT, node_name="text3", parent_path="/looper1")
# merge1 = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")

# # Set the parameters for text nodes
# text1._parms["text_string"].set("I have $$N")
# text1._parms["pass_through"].set(False)


# text2._parms["text_string"].set(" 2 Apples ")
# text3._parms["text_string"].set(" 3 Cherries")
# text4._parms["text_string"].set(" 4 Eggplants")
# # Set merge node parameter
# merge1._parms["single_string"].set(False)

# Connect nodes
# looper1._output_node.set_input(0, text1)
# text1.set_input(0, merge1)
# merge1.set_input(0, text2)
# merge1.set_input(1, text3)
# merge1.set_input(2, text4)

looper1 = NodeEnvironment.node_from_name("looper1")
print("\n:: LOOPER EVAL::")
loopeval = looper1.eval()
print("::LOOP EVALS TO::\n", loopeval)



