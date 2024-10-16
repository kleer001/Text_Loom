import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info
from global_store import GlobalStore

def set_global(global_name: str, value: any) -> None:
    globalset = GlobalStore()
    globalset.set(global_name, value)


def create_node(node_type: str, name: str) -> Node:
    node_type_enum = getattr(NodeType, node_type.upper())
    return Node.create_node(node_type_enum, node_name=name)


def set_parm(node_name: str, parm_name: str, value) -> None:
    node = NodeEnvironment.node_from_name(node_name)
    node._parms[parm_name].set(value)


def connect(to_node: str, from_node: str) -> None:
    node1 = NodeEnvironment.node_from_name(to_node)
    node2 = NodeEnvironment.node_from_name(from_node)
    node1.set_input(0, node2)


set_global("$ACTORS", "5")

create_node("text", "text_chars")
set_parm("text_chars", "text", "please give me a simple list of ${$ACTORS} stereotypical modern japanese characters from every day life.")

create_node("text", "text_stories")
set_parm("text_stories", "text", "please give me a simple list of ${$ACTORS} aesop fables that feature only one animal.")

create_node("make_list", "char_list")
create_node("make_list", "story_list")

connect("char_list", "text_chars")
connect("story_list", "text_stories")

create_node("looper", "looper1")
create_node("merge", "merge1")

connect("merge1", "char_list")
connect("merge1", "story_list")
connect("looper1", "merge1")
set_parm("merge1", "single_string", False)

create_node("text", "text_prompt")
connect("text_prompt_A", "looper._input_null")
set_parm("text_prompt_A", "text", "Given the character of $N ")

connect("file_out", "merge")
set_parm("file_out", "export", "loop_list_book.txt")

