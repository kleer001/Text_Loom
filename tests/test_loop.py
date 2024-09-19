import pytest
from backend.base_classes import Node, NodeType, NodeEnvironment

@pytest.fixture(scope="function")
def node_environment():
    NodeEnvironment._instance = None
    return NodeEnvironment.get_instance()

def test_looper_internal_node_creation(node_environment):
    looper_node = Node.create_node(NodeType.LOOPER, node_name="test_looper", parent_path="/")
    assert looper_node._input_node is not None, "Internal input node was not created"