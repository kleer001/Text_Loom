import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.global_store import GlobalStore
from core.undo_manager import UndoManager

globals = GlobalStore()
undomanager = UndoManager()

globals.set("AB", 6)
globals.set("FOO", "apples")
globals.set("BAR", 42)

print("Globals are: " , globals.list())
undomanager.undo()
print("Globals are: " , globals.list())
undomanager.undo()
print("Globals are: " , globals.list())
print("REDO STACK:",undomanager.get_redo_text())
undomanager.redo()
print("Globals are: " , globals.list())
undomanager.redo()
print("Globals are: " , globals.list())