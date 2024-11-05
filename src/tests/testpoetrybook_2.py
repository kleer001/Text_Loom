import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir) 

from core.base_classes import NodeEnvironment, Node, NodeType, generate_node_types
from core.print_node_info import print_node_info
from core.global_store import GlobalStore
from typing import Optional

def create_node_type_mapping():
    node_types = generate_node_types()
    return {nt.lower(): getattr(NodeType, nt) for nt in node_types}

node_type_mapping = create_node_type_mapping()

def create_node(node_type_str: str, node_name: Optional[str] = None, parent_path: str = "/") -> Node:
    node_type_enum = node_type_mapping.get(node_type_str.lower())
    if not node_type_enum:
        raise ValueError(f"Invalid node type: {node_type_str}")
    return Node.create_node(node_type_enum, node_name=node_name, parent_path=parent_path)


# Initialize GlobalStore
globalstore = GlobalStore()
globalstore.set("LENGTH", " about 250 words ")

globalstore.set("SYS", "Respond without introductions, summaries, or explanations. Provide only the requested information, without extra context or conversational fillers. Focus on clarity, conciseness, and delivering the direct result of the task. Only provide core information. No introductions, summaries, or extra explanations. Remove all fluff and focus on delivering the direct result." )

globalstore.set("LIST", "When asked for a list please provide it in a simple numbered list like 1,2,3, etc.")

globalstore.set("ROLE", "You are Alan Ginsbeg. You write free verse with vivid, surreal imagery, a rebellious tone, and raw emotional intensity. Use repetition for emphasis and rhythm, with long, flowing lines that capture chaotic thoughts and unfiltered feelings. Focus on themes of existential angst, societal critique, and personal liberation. Remember your background, Judiasm, Buddism. Remember the other beats and draw on the themes in their work too: Jack Kerouac, William S. Burroughs, Lawrence Ferlinghetti, Michael McClure, Frank O'Hara, Diane di Prima, Gary Snyder. Compose heartfelt, inspiring prose that is authentic, emotionally deep, and filled with vivid imagery. Use precise language and create a natural, compelling flow. When refering to objects name a specific one, don't rely on generalities. Ensure the narrative offers a unique perspective and leaves a lasting emotional impact. Avoid clichés, shallow emotions, vague language, and overused themes that would make the writing feel trite or forgettable.")

#print("Globals are: " , globalstore.list())

# Create nodes

prompt_months = create_node("text")
prompt_months._parms["text_string"].set(
    "${$SYS} ${$LIST} Please give a list of twelve unique feelings it engenders and brings that go along with the 12 months of the year. Mention only the feeling, not the month its self."
)

months_query = create_node("query")
months_query._parms["llm_name"].set("Ollama")

list_months = create_node("make_list")


looper1 = create_node("looper")
looper1._parms["step_from_input"].set(True)

print(NodeEnvironment.list_nodes())

prompt_roles = create_node("text", node_name="p_scenes", parent_path="/looper_1")
prompt_roles._parms["text_string"].set(
    "${$SYS} ${$ROLE}. Given the following season of life please compose ${$LENGTH} free verse meditation about $$N . Break through the constant rhythm of normal poetry. Break the bones of rhyme. Make short lines and long lines. Be ORGANIC! YOU ARE ALIVE!"
)
prompt_roles._parms["pass_through"].set(False)

role_prompt = create_node("query")
role_prompt._parms["llm_name"].set("Ollama")

compile = create_node("merge")
compile._parms["use_insert"].set(True)

text_out = create_node("file_out")
output_file_path = os.path.abspath("poetry_02.txt")
text_out._parms["file_name"].set(output_file_path)

# Connect nodes

months_query.set_input(0, prompt_months)
list_months.set_input(0, months_query)

looper1.set_input(0, list_months)
prompt_roles.set_input(0, looper1._input_node)
role_prompt.set_input(0, prompt_roles)
looper1._output_node.set_input(0, role_prompt)

compile.set_input(0,looper1)
text_out.set_input(0, compile)

text_out.cook()

