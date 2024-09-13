import os
import pytest
from backend.base_classes import Node, NodeType
from backend.nodes.file_out_node import FileOutNode
from backend.nodes.text_node import TextNode

@pytest.fixture
def setup_nodes():
    text_node = Node.create_node(NodeType.TEXT)
    file_out = Node.create_node(NodeType.FILE_OUT)
    return text_node, file_out

def test_text_node_output(setup_nodes, tmp_path):
    text_node, file_out = setup_nodes
    
    # Set the parameters for text node and file output
    text_node._parms["text_string"].set("This is a filler text string for testing.")
    output_file = tmp_path / "output.txt"
    file_out._parms["file_name"].set(str(output_file))
    
    # Set input connection
    file_out.set_input("input", text_node, "output")
    
    # Cook both nodes
    text_node.cook()
    file_out.cook()

    assert output_file.exists()
    assert output_file.read_text() == "This is a filler text string for testing."

    # Change the string and test again
    text_node._parms["text_string"].set("We've changed the string for more testing.")
    output_file2 = tmp_path / "output2.txt"
    file_out._parms["file_name"].set(str(output_file2))

    # Cook both nodes again
    text_node.cook()
    file_out.cook()

    assert output_file2.exists()
    assert output_file2.read_text() == "We've changed the string for more testing."

def test_node_info(setup_nodes):
    text_node, file_out = setup_nodes

    assert text_node.type().name == NodeType.TEXT.name
    assert file_out.type().name == NodeType.FILE_OUT.name
    assert "text_string" in text_node._parms
    assert "file_name" in file_out._parms
