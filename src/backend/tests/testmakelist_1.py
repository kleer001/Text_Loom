import os, sys
# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info


# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
prompt = Node.create_node(NodeType.QUERY, node_name="prompt")
makelist = Node.create_node(NodeType.MAKE_LIST, node_name="makelist")

# Set the parameters for text nodes
text1._parms["text_string"].set("Please give me a simple numbered list of five fairy tales from around the world. The list and only the list, please, no summary!")
# Connect nodes
prompt.set_input(0, text1)
makelist.set_input(0,prompt)

#text1._parms["pass_through"].set(True)
prompt._parms["llm_name"].set("Ollama")
print(":: COOK Query::")
makelist.cook()
print_node_info(text1)
#print_node_info(prompt)
print_node_info(makelist)
outputs = makelist.eval()
for index, o in enumerate(outputs):
    print(index, " ) ", o,"\n")
