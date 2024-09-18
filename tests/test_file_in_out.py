import pytest
from backend.base_classes import Node, NodeType
from backend.nodes.file_in_node import FileInNode
from backend.nodes.file_out_node import FileOutNode
from backend.nodes.null_node import NullNode
from backend.nodes.input_null_node import InputNullNode

@pytest.fixture
def setup_nodes():
    file_in = Node.create_node(NodeType.FILE_IN, node_name="file_in")
    null_node = Node.create_node(NodeType.NULL, node_name="null")
    file_out = Node.create_node(NodeType.FILE_OUT, node_name="file_out")
    return file_in, null_node, file_out


def test_file_in_out(setup_nodes, tmp_path):
    file_in, null_node, file_out = setup_nodes
    
    # Connect nodes
    null_node.set_input("input", file_in, "output")
    file_out.set_input("input", null_node, "output")
    
    # Create input file and set names
    input_file = tmp_path / "input.txt"
    print("INPUT FILE = ",input_file)
    input_file.write_text("This is a test input file.\nWith multiple lines.")
    file_in._parms["file_name"].set(str(input_file))

    # Set output file names and create file
    output_file = tmp_path / "output.txt"
    print("OUTPUT FILE = ",output_file)
    file_out._parms["file_name"].set(str(output_file))
    
    print("-- COOKING --")
    # Cook nodes
    #file_in.cook()
    #null_node.cook()
    file_out.cook()
    
    # Check output
    assert output_file.exists()
    assert output_file.read_text() == "This is a test input file.\nWith multiple lines."


def test_node_info(setup_nodes):
    file_in, null_node, file_out = setup_nodes

    assert file_in.type().name == NodeType.FILE_IN.name
    assert null_node.type().name == NodeType.NULL.name
    assert file_out.type().name == NodeType.FILE_OUT.name

    assert "file_name" in file_in._parms
    assert "file_name" in file_out._parms