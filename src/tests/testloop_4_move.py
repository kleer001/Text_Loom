import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info

outer_looper = Node.create_node(NodeType.LOOPER, node_name="outer_looper")

print("NODE ENV HAS", NodeEnvironment.list_nodes())

inner_looper = Node.create_node(NodeType.LOOPER, node_name="inner_looper", parent_path="/outer_looper")
text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/outer_looper/inner_looper")

print("Initial node structure:")
print_node_info(text1)
print("\nMoving inner_looper to root...")

inner_looper.set_parent("/")
print("\nAfter moving inner_looper:")
print_node_info(text1)