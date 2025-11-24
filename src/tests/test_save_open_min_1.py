import sys
import os
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info
from core.flow_simple import save_flowstate, load_flowstate


def test_save_and_load_flow():
    print("Creating initial nodes...")
    text1 = Node.create_node(NodeType.TEXT, node_name="text1")
    text2 = Node.create_node(NodeType.TEXT, node_name="text2")

    text1._parms["text_string"].set("Filler Text 1")
    text2._parms["text_string"].set("Boopah Text 2")
    text1.set_next_input(text2)

    text1._parms["pass_through"].set(True)
    print("\nEval with passthrough True:")
    texteval2 = text1.eval()
    print_node_info(text1)
    print("text1 evals to:", texteval2)

    text1._parms["text_string"].set("CHANGED Filler Text 1")
    text2._parms["text_string"].set("CHANGED Boopah Text 2")

    print("\nEval with passthrough False:")
    texteval = text1.eval()
    print_node_info(text1)
    print("text1 evals to:", texteval)

    file_path = os.path.abspath("save_flow_test.txt")
    print(f"\nSaving to {file_path}")
    assert save_flowstate(file_path), "Failed to save flow!"

    print("\nChecking saved file exists:", os.path.exists(file_path))
    assert os.path.exists(file_path), "Saved file does not exist"

    with open(file_path, 'r') as f:
        content = f.read()
        print("File contents:")
        print(content)
        assert len(content) > 0, "Saved file is empty"

    print("\nClearing environment...")
    env = NodeEnvironment.get_instance()
    env.nodes.clear()

    print("\nLoading saved flow...")
    load_flowstate(file_path)

    text1_loaded = NodeEnvironment.node_from_name("/text1")
    text2_loaded = NodeEnvironment.node_from_name("/text2")

    print("\nValidating loaded nodes:")
    assert text1_loaded is not None, "text1 failed to load"
    assert text2_loaded is not None, "text2 failed to load"

    print_node_info(text1_loaded)
    print_node_info(text2_loaded)

    print("\nValidating evaluation:")
    texteval_loaded = text1_loaded.eval()
    print("text1 evals to:", texteval_loaded)

    if os.path.exists(file_path):
        os.remove(file_path)