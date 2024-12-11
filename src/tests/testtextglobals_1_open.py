import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.looper_node import *
from core.global_store import GlobalStore
from core.flowstate_manager import *



# Set up save file
file_path = os.path.abspath("save_file_globaltest.json")
load_flowstate(filepath=file_path)

globals = GlobalStore()
print("Globals are: " , globals.list())


text1 = NodeEnvironment.node_from_name("text1")
print_node_info(text1)

evaltext = text1._parms["text_string"].eval()
print("text1 evals to: \n",evaltext)
