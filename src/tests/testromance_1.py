import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir) 

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.global_store import GlobalStore

# Initialize GlobalStore
globalstore = GlobalStore()
chapters = 12
globalstore.set("CHAPTERS", chapters)
globalstore.set("SCENES", " about 3 to 6 scenes, depending on tension. Fewer scenes in high tension and more scenes with less. ")
globalstore.set("SCENELENGTH", "about 1000 words ")
globalstore.set("LOVERA", "a cybernetic dolphin named Takuma ")
globalstore.set("LOVERB", "an alien octopus named Ophilia ")
globalstore.set("ROLE", "Respond without introductions, summaries, or explanations. Provide only the requested information, without extra context or conversational fillers. Focus on clarity, conciseness, and delivering the direct result of the task. Only provide core information. No introductions, summaries, or extra explanations. Remove all fluff and focus on delivering the direct result. You are a master romance novelist, crafting irresistible love stories filled with passion, tension, and unforgettable characters. Every plot twist and emotional beat pulls readers deeper into the heart of the romance. ")

print("Globals are: " , globalstore.list())

# Create nodes

prompt_outline = Node.create_node(NodeType.TEXT)
prompt_outline._parms["text_string"].set("${$ROLE} Please outline a romance novel titled DEEP BLUE LOVE, where two characters from different backgrounds meet unexpectedly and fall in love. The main characters are ${$LOVERA} and ${$LOVERB}. Include key plot points, conflicts, and a satisfying conclusion. Add moments of emotional tension, vulnerability, slow-burn tension, steamy scenes, and intense chemistry. This outline should be about ${$CHAPTERS} chapters long. Please provide the chaper outlines in a simple numbered list like 1,2,3, etc.  ")
outline_query = Node.create_node(NodeType.QUERY)
outline_query._parms["llm_name"].set("Ollama")
list_outline = Node.create_node(NodeType.MAKE_LIST)

looper1 = Node.create_node(NodeType.LOOPER)
looper1._parms["max_from_input"].set(True)
print(NodeEnvironment.list_nodes())
prompt_scenes = Node.create_node(NodeType.TEXT, node_name="p_scenes", parent_path="/looper_1")
prompt_scenes._parms["text_string"].set("${$ROLE} Expand the following chapter with ${$SCENES} for ${$LOVERA} and ${$LOVERB}. Please provide the scenes in a simple numbered list like 1,2,3, etc :  $$N")
prompt_scenes._parms["pass_through"].set(False)
scene_prompt = Node.create_node(NodeType.QUERY)
scene_prompt._parms["llm_name"].set("Ollama")
list_scenes = Node.create_node(NodeType.MAKE_LIST)

looper2 = Node.create_node(NodeType.LOOPER)
looper2._parms["max_from_input"].set(True)
prompt_prose = Node.create_node(NodeType.TEXT, node_name="p_prose", parent_path="/looper_2")
prompt_prose._parms["text_string"].set("${$ROLE} Expand the following scene with ${$SCENELENGTH} for the characters  ${$LOVERA} and ${$LOVERB}. Please provide only the story prose:  $$N")
prompt_prose._parms["pass_through"].set(False)
prose_query = Node.create_node(NodeType.QUERY)
prose_query._parms["llm_name"].set("Ollama")

compile = Node.create_node(NodeType.MERGE)
compile._parms["use_insert"].set(True)

text_out = Node.create_node(NodeType.FILE_OUT)
output_file_path = os.path.abspath("romance_01.txt")
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
