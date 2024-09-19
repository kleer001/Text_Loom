import os
from base_classes import NodeEnvironment, Node, NodeType
from print_node_info import print_node_info


def print_node_info(node):
    print(f"\n--- {node.name()} Node Information ---")
    print(f"Node: {node}")
    print(f"Node Type: {node.type()}")
    print(f"Node Path: {node.path()}")
    print(f"Node State: {node.state()}")
    print("Parameters:")
    if hasattr(node, '_parms'):  # Check if node has a _parms attribute
        for parm_name, parm in node._parms.items():
            print(f"  {parm_name}: {parm.raw_value()}")
    else:
        print("No parameters found.")
    print(f"Inputs: {node.inputs_with_indices()}")
    print(f"Outputs: {node.outputs_with_indices()}")
    print(f"Errors: {node.errors()}")
    print(f"Warnings: {node.warnings()}")
    print(f"Last Cook Time: {node.last_cook_time()}")
    print(f"Cook Count: {node.cook_count()}")


# Create nodes

looper1 = Node.create_node(NodeType.LOOPER, node_name="looper1")

text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")
text2 = Node.create_node(NodeType.TEXT, node_name="text2", parent_path="/looper1")
text3 = Node.create_node(NodeType.TEXT, node_name="text3", parent_path="/looper1")
merge1 = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")
text4 = Node.create_node(NodeType.TEXT, node_name="text4", parent_path="/looper1")

# Set the parameters for text nodes
text1._parms["text_string"].set("Filler Text 1")
text2._parms["text_string"].set("Filler Text 2")
text3._parms["text_string"].set("Filler Text 3")
text4._parms["text_string"].set("Text4. Input text: $$N")

# Set merge node parameter
merge1._parms["single_string"].set(False)

# Connect nodes
merge1.set_input(0, text1, "output")
merge1.set_input(1, text2, "output")
merge1.set_input(2, text3, "output")
text4.set_input("input", merge1, "output")
looper1._output_node.set_input(0,text4,"output")

print_node_info(looper1)

looper1.cook()

print_node_info(looper1)
print("::VARS::\n",vars(looper1))

print_node_info(looper1._input_node)
print_node_info(looper1._output_node)

print(NodeEnvironment.list_nodes())