import os
import pytest
from ..src.backend.base_classes import Node, NodeType
from ..src.backend.nodes.text_node import TextNode
from ..src.backend.nodes.file_out_node import FileOutNode

@pytest.fixture
def setup_nodes():
    text_node = Node.create_node(NodeType.TEXT)
    file_out = Node.create_node(NodeType.FILE_OUT)
    file_out.set_input("input", text_node, "output")
    return text_node, file_out

def test_text_node_output(setup_nodes, tmp_path):
    text_node, file_out = setup_nodes
    
    # First test
    text_node._parms["text_string"].set("This is a filler text string for testing.")
    output_file = tmp_path / "output.txt"
    file_out._parms["file_name"].set(str(output_file))

    file_out.cook()

    assert output_file.exists()
    assert output_file.read_text() == "This is a filler text string for testing."

    # Second test
    text_node._parms["text_string"].set("We've changed the string for more testing.")
    output_file2 = tmp_path / "output2.txt"
    file_out._parms["file_name"].set(str(output_file2))

    file_out.cook()

    assert output_file2.exists()
    assert output_file2.read_text() == "We've changed the string for more testing."

def test_node_info(setup_nodes):
    text_node, file_out = setup_nodes

    assert isinstance(text_node, TextNode)
    assert isinstance(file_out, FileOutNode)
    assert text_node.type() == NodeType.TEXT
    assert file_out.type() == NodeType.FILE_OUT
    assert "text_string" in text_node._parms
    assert "file_name" in file_out._parms
