import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.global_store import GlobalStore
from core.undo_manager import UndoManager

globals = GlobalStore()
undomanager = UndoManager()
undomanager.flush_all_undos()

print("\nInitial state:")
print("Globals:", globals.list())

print("\nSetting AB = 6")
globals.set("AB", 6)
print("Globals:", globals.list())
print("Undo text:", undomanager.get_undo_text())
print("Redo text:", undomanager.get_redo_text())

print("\nSetting FOO = apples")
globals.set("FOO", "apples")
print("Globals:", globals.list())
print("Undo text:", undomanager.get_undo_text())
print("Redo text:", undomanager.get_redo_text())

print("\nClearing Globals")
globals.flush_all_globals()
print("Globals:", globals.list())
print("Undo text:", undomanager.get_undo_text())
print("Redo text:", undomanager.get_redo_text())

print("\nFirst undo:")
undomanager.undo()
print("Globals:", globals.list())
print("Undo text:", undomanager.get_undo_text())
print("Redo text:", undomanager.get_redo_text())
print("Redo stack length:", len(undomanager.redo_stack))

print("\nSecond undo:")
undomanager.undo()
print("Globals:", globals.list())
print("Undo text:", undomanager.get_undo_text())
print("Redo text:", undomanager.get_redo_text())
print("Redo stack length:", len(undomanager.redo_stack))

print("\nFirst redo:")
undomanager.redo()
print("Globals:", globals.list())
print("Undo text:", undomanager.get_undo_text())
print("Redo text:", undomanager.get_redo_text())
print("Redo stack length:", len(undomanager.redo_stack))

print("\nSecond redo:")
undomanager.redo()
print("Globals:", globals.list())
print("Undo text:", undomanager.get_undo_text())
print("Redo text:", undomanager.get_redo_text())
print("Redo stack length:", len(undomanager.redo_stack))
