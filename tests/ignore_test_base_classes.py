import pytest
from pathlib import Path
import uuid
from backend.base_classes import (
    Node, NodeType, NodeEnvironment, MobileItem, NodeConnection,
    NetworkItemType, InternalPath, NodeState
)
from backend.nodes.file_in_node import FileInNode
from backend.nodes.file_out_node import FileOutNode
from backend.nodes.null_node import NullNode

@pytest.fixture
def setup_nodes():
    file_in = Node.create_node(NodeType.FILE_IN, node_name="file_in")
    null_node = Node.create_node(NodeType.NULL, node_name="null")
    file_out = Node.create_node(NodeType.FILE_OUT, node_name="file_out")
    return file_in, null_node, file_out

@pytest.fixture
def connected_nodes(setup_nodes):
    file_in, null_node, file_out = setup_nodes
    null_node.set_input("input", file_in, "output")
    file_out.set_input("input", null_node, "output")
    return file_in, null_node, file_out

def test_node_creation(setup_nodes):
    file_in, null_node, file_out = setup_nodes
    assert isinstance(file_in, FileInNode)
    assert isinstance(null_node, NullNode)
    assert isinstance(file_out, FileOutNode)
    assert file_in.name() == "file_in"
    assert null_node.name() == "null"
    assert file_out.name() == "file_out"

def test_node_connections(connected_nodes):
    file_in, null_node, file_out = connected_nodes
    assert null_node in file_in.outputs()
    assert file_out in null_node.outputs()
    assert file_in in null_node.input_nodes()
    assert null_node in file_out.input_nodes()

def test_node_removal(connected_nodes):
    file_in, null_node, file_out = connected_nodes
    null_node.destroy()
    assert null_node not in file_in.outputs()
    assert len(file_out.input_nodes()) == 0

def test_node_state():
    node = Node.create_node(NodeType.NULL)
    assert node.state() == NodeState.UNCOOKED
    node.set_state(NodeState.COOKING)
    assert node.state() == NodeState.COOKING
    node.set_state(NodeState.UNCHANGED)
    assert node.state() == NodeState.UNCHANGED

def test_node_errors_warnings():
    node = Node.create_node(NodeType.NULL)
    node.add_error("Test error")
    node.add_warning("Test warning")
    assert "Test error" in node.errors()
    assert "Test warning" in node.warnings()
    node.clear_errors()
    node.clear_warnings()
    assert len(node.errors()) == 0
    assert len(node.warnings()) == 0

def test_node_cook(connected_nodes):
    file_in, null_node, file_out = connected_nodes
    file_out.cook()
    assert file_out.cook_count() > 0
    assert file_out.last_cook_time() > 0

def test_mobile_item():
    item = MobileItem("test_item", "/test/path", [0.0, 0.0])
    assert item.name() == "test_item"
    assert item.path() == "/test/path"
    assert item.network_item_type() == NetworkItemType.NODE

def test_mobile_item_bulk_add():
    items_data = [
        {"name": f"item_{i}", "path": f"/test/path/{i}", "position": [float(i), float(i)]}
        for i in range(10)
    ]
    new_items = MobileItem.bulk_add(items_data)
    assert len(new_items) == 10
    assert all(isinstance(item, MobileItem) for item in new_items)
    assert len(set(item.session_id() for item in new_items)) == 10  # All session IDs are unique

def test_node_connection():
    node1 = Node.create_node(NodeType.NULL, "node1")
    node2 = Node.create_node(NodeType.NULL, "node2")
    connection = NodeConnection(node1, node2, "output", "input")
    assert connection.output_node() == node1
    assert connection.input_node() == node2
    assert connection.output_index() == "output"
    assert connection.input_index() == "input"
    assert connection.network_item_type() == NetworkItemType.CONNECTION

def test_internal_path():
    path = InternalPath("/test/path")
    assert str(path) == "/test/path"
    assert path.parent() == InternalPath("/test")
    assert path.name() == "path"
    assert path.relative_to(InternalPath("/test")) == "path"

def test_node_environment():
    env = NodeEnvironment.get_instance()
    assert isinstance(env, NodeEnvironment)
    assert NodeEnvironment.get_instance() is env  # Singleton pattern

    node = Node.create_node(NodeType.NULL, "test_node")
    assert "/test_node" in NodeEnvironment.nodes

    namespace = env.get_namespace()
    assert 'Node' in namespace
    assert 'NodeType' in namespace
    assert 'current_node' in namespace

def test_node_environment_execute():
    env = NodeEnvironment.get_instance()
    result = env.execute("2 + 2")
    assert result == 4

# Error condition tests

def test_duplicate_node_name():
    Node.create_node(NodeType.NULL, "duplicate")
    new_node = Node.create_node(NodeType.NULL, "duplicate")
    assert new_node.name() != "duplicate"  # Should have a suffix like "_1"

def test_invalid_connection():
    node1 = Node.create_node(NodeType.NULL, "node1")
    node2 = Node.create_node(NodeType.NULL, "node2")
    with pytest.raises(KeyError):  # Assuming it raises KeyError for invalid input/output
        node2.set_input("non_existent_input", node1, "non_existent_output")

def test_circular_dependency():
    node1 = Node.create_node(NodeType.NULL, "node1")
    node2 = Node.create_node(NodeType.NULL, "node2")
    node1.set_input("input", node2, "output")
    node2.set_input("input", node1, "output")
    # This should not cause an infinite loop when cooking
    node1.cook()
    assert node1.cook_count() > 0
    assert node2.cook_count() > 0

# Edge case: Test with a large number of nodes
def test_large_node_network():
    nodes = [Node.create_node(NodeType.NULL, f"node_{i}") for i in range(1000)]
    for i in range(999):
        nodes[i+1].set_input("input", nodes[i], "output")
    nodes[-1].cook()
    assert all(node.cook_count() > 0 for node in nodes)

if __name__ == "__main__":
    pytest.main()