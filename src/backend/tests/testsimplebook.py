import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir) 

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from global_store import GlobalStore

# Initialize GlobalStore
globalstore = GlobalStore()
chapters = 3
globalstore.set("CHAPTERS", chapters)
globalstore.set("SCENES", " 4 scenes ")
globalstore.set("SCENELENGTH", " about 500 words ")
globalstore.set("CHARA", "a dog named Takuma ")
globalstore.set("CHARB", "a cat named Ophilia ")
globalstore.set("SETTING", "an urban park during the afternoon ")
globalstore.set("ROLE", "Respond without introductions, summaries, or explanations. Provide only the requested information, without extra context or conversational fillers. Focus on clarity, conciseness, and delivering the direct result of the task. Only provide core information. No introductions, summaries, or extra explanations. Remove all fluff and focus on delivering the direct result. You are a brilliant children's book author, weaving heartwarming, imaginative stories that delight young readers and spark their curiosity. Your tales are simple and down to earth, based in reality.")

print("Globals are: " , globalstore.list())

# Create nodes

prompt_outline = Node.create_node(NodeType.TEXT)
prompt_outline._parms["text_string"].set("${$ROLE} Outline a children's book where two characters from different worlds meet unexpectedly and become friends. The characters are ${$CHARA} and ${$CHARB}. The setting in ${SETTING} Include key plot points, moments of discovery, and a happy, wholesome resolution. Add elements of wonder, imagination, and playful adventure to capture young readers' attention. This outline should be about ${$CHAPTERS} chapters long. Please provide the chaper outlines in a simple numbered list like 1,2,3, etc.  ")
outline_query = Node.create_node(NodeType.QUERY)
outline_query._parms["llm_name"].set("Ollama")
list_outline = Node.create_node(NodeType.MAKE_LIST)

looper1 = Node.create_node(NodeType.LOOPER)
looper1._parms["step_from_input"].set(True)
print(NodeEnvironment.list_nodes())
prompt_scenes = Node.create_node(NodeType.TEXT, node_name="p_scenes", parent_path="/looper_1")
prompt_scenes._parms["text_string"].set("${$ROLE} Please fill out the following chapter with ${$SCENES} for ${$CHARA} and ${$CHARB} in ${$SETTING}. Please provide the scenes in a simple numbered list like 1,2,3, etc :  $$N")
prompt_scenes._parms["pass_through"].set(False)
scene_prompt = Node.create_node(NodeType.QUERY)
scene_prompt._parms["llm_name"].set("Ollama")
list_scenes = Node.create_node(NodeType.MAKE_LIST)

looper2 = Node.create_node(NodeType.LOOPER)
looper2._parms["step_from_input"].set(True)
prompt_prose = Node.create_node(NodeType.TEXT, node_name="p_prose", parent_path="/looper_2")
prompt_prose._parms["text_string"].set("${$ROLE} Please do your best and bang out finished prose for the following scene with ${$SCENELENGTH} for the characters  ${$CHARA} and ${$CHARB} in ${SETTING}. $$N")
prompt_prose._parms["pass_through"].set(False)
prose_query = Node.create_node(NodeType.QUERY)
prose_query._parms["llm_name"].set("Ollama")

compile = Node.create_node(NodeType.MERGE)
compile._parms["use_insert"].set(True)

text_out = Node.create_node(NodeType.FILE_OUT)
output_file_path = os.path.abspath("kidsbook_01.txt")
text_out._parms["file_name"].set(output_file_path)

# Connect nodes

outline_query.set_input(0, prompt_outline)
list_outline.set_input(0, outline_query)

looper1.set_input(0, list_outline)
prompt_scenes.set_input(0, looper1._input_node)
scene_prompt.set_input(0, prompt_scenes)
list_scenes.set_input(0, scene_prompt)
looper1._output_node.set_input(0, list_scenes)

looper2.set_input(0, looper1)
prompt_prose.set_input(0, looper2._input_node)
prose_query.set_input(0, prompt_prose)
looper2._output_node.set_input(0, prose_query)
compile.set_input(0,looper2)
text_out.set_input(0, compile)

text_out.cook()

