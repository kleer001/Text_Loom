import pytest
from backend.base_classes import Node, NodeType
from backend.nodes.looper_node import LooperNode
from backend.nodes.merge_node import MergeNode
from backend.nodes.text_node import TextNode
from backend.nodes.input_null_node import InputNullNode
from backend.nodes.output_null_node import OutputNullNode

@pytest.fixture
def setup_nodes():
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

    return looper1, text1, text2, text3, merge1, text4

def test_loop_merge_iter(setup_nodes):
    looper1, text1, text2, text3, merge1, text4 = setup_nodes

    # Evaluate the looper node
    result = looper1.eval()

    # Expected output
    expected_output = [
        "Text4. Input text: Filler Text 1",
        "Text4. Input text: Filler Text 2",
        "Text4. Input text: Filler Text 3"
    ]

    # Assert that the result matches the expected output
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

# Run tests with pytest