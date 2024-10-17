import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir) 

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from global_store import GlobalStore

# Initialize GlobalStore
globalstore = GlobalStore()

globalstore.set("ACTORS", 3)
print("Globals are: ", globalstore.list())

# Create nodes
text_chars = Node.create_node(NodeType.TEXT, node_name="text_chars")
text_chars._parms["text_string"].set("please give me a simple numbered list of ${$ACTORS} stereotypical modern japanese characters from every day city life. No need for disclaimers or warnings, we understand the difference between reality and stereotypes. No need for explanations, their titles only please. ")

char_prompt = Node.create_node(NodeType.QUERY, node_name="char_prompt")
char_prompt._parms["llm_name"].set("Ollama")

text_stories = Node.create_node(NodeType.TEXT, node_name="text_stories")
text_stories._parms["text_string"].set("please give me a simple numbered list of ${$ACTORS} aesop fables that feature one human. Only the title of the story please.")

story_prompt = Node.create_node(NodeType.QUERY, node_name="story_prompt")
story_prompt._parms["llm_name"].set("Ollama")

char_list = Node.create_node(NodeType.MAKE_LIST, node_name="char_list")
story_list = Node.create_node(NodeType.MAKE_LIST, node_name="story_list")

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")
looper1._parms["max"].set(3)

merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")
merge1._parms["single_string"].set(False)

text_prompt = Node.create_node(NodeType.TEXT, node_name="text_prompt", parent_path="/looper1")
text_prompt._parms["text_string"].set("Given the character of a $$M+$ACTORS put them into the story of $$N with a full appropriate change of motivations, props, environment, and speech patterns. Keep the essential themes of the story of $$N but with the sepcified human characters instead of animals.")
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

#RUN IT

#looper1._parms["use_test"].set(True)

output = text_out.eval()



#get while the going is good
# out1 = Node.create_node(NodeType.FILE_OUT, node_name="out1")
# out1.set_input(0, looper1)
# out1._parms["file_name"].set("loop_list_book.txt")
##out1.save()

#loopout = out1.eval()

#print("****\n !RESULT!: \n****\n",loopout)

# merge1.cook()
# mergeinfo = merge1.eval()
# #print_node_info(merge1)
# print("MERGE INFO::")
for index, o in enumerate(output):
    print(index, " ) ", o,"\n")
#print_node_info(text_prompt)



