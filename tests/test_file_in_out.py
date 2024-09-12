import pytest
from src.backend.base_classes import Node, NodeType
from src.backend.nodes.file_in_node import FileInNode
from src.backend.nodes.file_out_node import FileOutNode
from src.backend.nodes.null_node import NullNode

@pytest.fixture
def setup_nodes():
    file_in = Node.create_node(NodeType.FILE_IN)
    file_out = Node.create_node(NodeType.FILE_OUT)
    null_node = Node.create_node(NodeType.NULL)

    null_node.set_input("input", file_in, "output")
    file_out.set_input("input", null_node, "output")

    return file_in, null_node, file_out

def test_file_in_out(setup_nodes, tmp_path):
    file_in, null_node, file_out = setup_nodes

    # Create input file
    input_file = tmp_path / "input.txt"
    input_file.write_text("This is a test input file.\nWith multiple lines.")

    # Set up nodes
    file_in._parms["file_name"].set(str(input_file))
    output_file = tmp_path / "output.txt"
    file_out._parms["file_name"].set(str(output_file))

    # Cook nodes
    file_in.cook()
    null_node.cook()
    file_out.cook()

    # Check output
    assert output_file.exists()
    assert output_file.read_text() == "This is a test input file.\nWith multiple lines."

def test_node_info(setup_nodes):
    file_in, null_node, file_out = setup_nodes

    assert isinstance(file_in, FileInNode)
    assert isinstance(null_node, NullNode)
    assert isinstance(file_out, FileOutNode)

    assert file_in.type() == NodeType.FILE_IN
    assert null_node.type() == NodeType.NULL
    assert file_out.type() == NodeType.FILE_OUT

    assert "file_name" in file_in._parms
    assert "file_name" in file_out._parms