import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info

from global_store import GlobalStore

# Initialize GlobalStore
globalstore = GlobalStore()
globalstore.set("COUNTRY", " France")

# Create nodes
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
prompt = Node.create_node(NodeType.QUERY, node_name="prompt")

# Set the parameters for text nodes
text1._parms["text_string"].set("What is the capital of ${$COUNTRY} ?")
# Connect nodes
prompt.set_input(0, text1)

#print_node_info(text1)
#print_node_info(text2)

#text1._parms["pass_through"].set(True)
prompt._parms["llm_name"].set("Ollama")
print(":: COOK Query::")
prompt.cook()
print_node_info(text1)
print_node_info(prompt)

# text1._parms["pass_through"].set(False)
# text1._parms["text_string"].set("CHANGED Filler Text 1")
# text2._parms["text_string"].set("CHAGNED Boopah Text 2")

# print(":: EVAL False passthrough::")
# texteval = text1.eval()

# print("text1 evals to: \n",texteval)

