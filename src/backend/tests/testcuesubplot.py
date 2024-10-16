import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir) 

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from global_store import GlobalStore

# Initialize GlobalStore
globalstore = GlobalStore()

globalstore.set("$ACTORS", 3)
print("Globals are: ", globalstore.list())

# Create nodes
text_chars = Node.create_node(NodeType.TEXT, node_name="text_chars")
text_chars._parms["text_string"].set("please give me a simple numbered list of ${$ACTORS} stereotypical modern japanese characters from every day city life.")

text_stories = Node.create_node(NodeType.TEXT, node_name="text_stories")
text_stories._parms["text_string"].set("please give me a simple numbered list of ${$ACTORS} aesop fables that feature only one animal.")

char_list = Node.create_node(NodeType.MAKE_LIST, node_name="char_list")
story_list = Node.create_node(NodeType.MAKE_LIST, node_name="story_list")

# Connect nodes
char_list.set_input(0, text_chars)
story_list.set_input(0, text_stories)

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
looper1._parms["max"].set(3)

merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")

merge1.set_input(0, char_list)
merge1.set_input(1, story_list)
looper1.set_input(0, merge1)
merge1._parms["single_string"].set(False)

text_prompt = Node.create_node(NodeType.TEXT, node_name="text_prompt", parent_path="/looper1")

looper1.connect_loop_in(text_prompt)
looper1.connect_loop_out(text_prompt)

text_prompt._parms["text_string"].set("Given the character of a $$N put them into the story of $$M+$ACTORS with a full appropriate change of motivations, props, environment, and speech patterns. Keep the essential themes of the story of $$M+$ACTORS but with humans instead of animals.")

loopout = looper1.eval()

print("~LOOP1 returns: \n",loopout)

# out1 = Node.create_node(NodeType.FILE_OUT, node_name="out1")
# out1.set_input(0, looper1)
# out1._parms["file_name"].set("loop_list_book.txt")
# out1.save()
