import pytest
from backend.base_classes import Node, NodeType
from backend.nodes.merge_node import MergeNode
from backend.nodes.text_node import TextNode

@pytest.fixture
def setup_nodes():
    text1 = Node.create_node(NodeType.TEXT)
    text2 = Node.create_node(NodeType.TEXT)
    text3 = Node.create_node(NodeType.TEXT)
    merge1 = Node.create_node(NodeType.MERGE)

    # Set the parameters for text nodes
    text1._parms["text_string"].set("This is the first text string.")
    text2._parms["text_string"].set("And this is the second one.")
    text3._parms["text_string"].set("Finally, this is the third and last text string.")

    # Connect nodes
    merge1.set_input(0, text1, "output")
    merge1.set_input(1, text2, "output")
    merge1.set_input(2, text3, "output")

    return text1, text2, text3, merge1

def test_three_text_merge(setup_nodes):
    text1, text2, text3, merge1 = setup_nodes

    # Cook the merge node and check the output for single string mode
    merge1._parms["single_string"].set(True)
    merge1.cook()
    assert merge1.eval() == ["This is the first text string.And this is the second one.Finally, this is the third and last text string."]

    # Change mode to list of strings and check the output
    merge1._parms["single_string"].set(False)
    merge1.cook()
    assert merge1.eval() == ["This is the first text string.", "And this is the second one.", "Finally, this is the third and last text string."]

# Run tests with pytest