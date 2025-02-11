import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.looper_node import *
from core.loop_manager import *
from core.flowstate_manager import *
from core.global_store import GlobalStore

# Set up save file
file_path = os.path.abspath("save_file.json")

load_flowstate(filepath=file_path)

global_store = GlobalStore()

print("Globals are: " , global_store.list())

print(NodeEnvironment.list_nodes())

looper1 = NodeEnvironment.node_from_name("looper1")
print("\n:: LOOPER EVAL::")
loopeval = looper1.eval()
print("::LOOP EVALS TO::\n", loopeval)



