import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info



# Create nodes
text1 = Node.create_node(NodeType.TEXT)

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text ")

print(NodeEnvironment.list_nodes())
node = NodeEnvironment.node_from_name("text_1")

print(node)

# print_node_info(text1)
# evaltext = text1._parms["text_string"].eval()
# print("text1 evals to: \n",evaltext)


# text1._parms["pass_through"].set(False)
# text1._parms["text_string"].set("CHANGED Filler Text 1")
# text2._parms["text_string"].set("CHAGNED Boopah Text 2")

# print(":: EVAL False passthrough::")
# texteval = text1.eval()
# print_node_info(text1)
# print("text1 evals to: \n",texteval)

