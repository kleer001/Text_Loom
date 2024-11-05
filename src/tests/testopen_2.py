import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.nodes.looper_node import *
from core.loop_manager import *
from core.flowstate_manager import *
from core.global_store import GlobalStore
# from undo_manager import UndoManager

# Set up save file
file_path = os.path.abspath("save_file_2.json")

load_flowstate(filepath=file_path)

text1 = NodeEnvironment.node_from_name("text1")
print_node_info(text1)

text2 = NodeEnvironment.node_from_name("text2")
print_node_info(text2)