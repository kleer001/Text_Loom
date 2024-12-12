import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir) 

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.global_store import GlobalStore

# Initialize GlobalStore
globalstore = GlobalStore()
loops_to_go = 3
globalstore.set("ACTORS", loops_to_go)

# Create nodes
text_chars = Node.create_node(NodeType.TEXT, node_name="text_chars")
text_chars._parms["text_string"].set("please give me a simple numbered list of $ACTORS types of stock characters in comedia del arte. List the character name only please.")

char_prompt = Node.create_node(NodeType.QUERY, node_name="char_prompt")
char_prompt._parms["llm_name"].set("Ollama")

text_stories = Node.create_node(NodeType.TEXT, node_name="text_stories")
text_stories._parms["text_string"].set("please give me a simple numbered list of $ACTORS types of breakfast foods. List the type of food only.")

story_prompt = Node.create_node(NodeType.QUERY, node_name="story_prompt")
story_prompt._parms["llm_name"].set("Ollama")

char_list = Node.create_node(NodeType.MAKE_LIST, node_name="char_list")
story_list = Node.create_node(NodeType.MAKE_LIST, node_name="story_list")

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
looper1._parms["max"].set(loops_to_go)

merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")
merge1._parms["single_string"].set(False)

text_prompt = Node.create_node(NodeType.TEXT, node_name="text_prompt", parent_path="/looper1")
text_prompt._parms["text_string"].set("Given the character of $$N, in Comedia Del Arte, please say in a tweet what they think of $$N+$ACTORS.")
text_prompt._parms["pass_through"].set(False)

full_prompt = Node.create_node(NodeType.QUERY, node_name="full_prompt")
full_prompt._parms["llm_name"].set("Ollama")


text_out = Node.create_node(NodeType.FILE_OUT, node_name="text_out")
output_file_path = os.path.abspath("output.txt")
text_out._parms["file_name"].set(output_file_path)

# Connect nodes

char_prompt.set_input(0, text_chars)
story_prompt.set_input(0, text_stories)

char_list.set_input(0, char_prompt)
story_list.set_input(0, story_prompt)

merge1.set_input(0, char_list)
merge1.set_input(1, story_list)

looper1.set_input(0, merge1)

text_prompt.set_input(0, looper1._input_node)
full_prompt.set_input(0,text_prompt)
looper1._output_node.set_input(0, full_prompt)

text_out.set_input(0,looper1)

output = text_out.eval()

