import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.global_store import GlobalStore

globalstore = GlobalStore()
loops = 3
globalstore.set("TEST", loops)

text_list1 = Node.create_node(NodeType.TEXT, node_name="text_list1")
text_list1._parms["text_string"].set("apple")

text_list2 = Node.create_node(NodeType.TEXT, node_name="text_list2")
text_list2._parms["text_string"].set("banana")

text_list3 = Node.create_node(NodeType.TEXT, node_name="text_list3")
text_list3._parms["text_string"].set("cherry")

merge1 = Node.create_node(NodeType.MERGE, node_name="merge1")
merge1._parms["single_string"].set(False)

looper = Node.create_node(NodeType.LOOPER, node_name="looper")
looper._parms["max"].set(loops)

text_patterns = Node.create_node(NodeType.TEXT, node_name="text_patterns", parent_path="/looper")
text_patterns._parms["text_string"].set(
    "Global var test: ${$TEST}\n"
    "Simple loop number ($$N): $$N\n"
    "Math loop add ($$M+1): $$M+1\n"
    "Math loop subtract ($$M-1): $$M-1\n"
    "Math loop multiply ($$M*2): $$M*2\n"
    "Math loop divide ($$M/2): $$M/2\n"
    "Math loop modulo ($$M%2): $$M%2\n"
    "Explicit number ($$1): $$1\n"
    "Backtick test: `len('test') + 1`\n"
    "Loop number ($$L): $$L"
)


merge1.set_input(0, text_list1)
merge1.set_input(1, text_list2)
merge1.set_input(2, text_list3)

looper.set_input(0, merge1)

text_patterns.set_input(0, looper._input_node)
looper._output_node.set_input(0, text_patterns)

output = looper.eval()
print(f"**Output=\n\n{output}")