#!/usr/bin/env python3
"""
Quick test to verify NodeConnection session ID functionality.
"""

import sys
sys.path.insert(0, '..')

from core.base_classes import NodeEnvironment
from core.node_connection import NodeConnection
from core.node import Node
from core.enums import NodeType


def test_connection_session_ids():
    """Test that connections get unique session IDs."""
    print("Testing NodeConnection session ID functionality...")

    # Create some test nodes
    text_node = Node.create_node(NodeType.TEXT, node_name="test_text")
    fileout_node = Node.create_node(NodeType.FILE_OUT, node_name="test_fileout")

    print(f"✓ Created nodes: {text_node.path()} and {fileout_node.path()}")

    # Create a connection
    fileout_node.set_input(0, text_node, 0)
    connection = fileout_node._inputs[0]

    print(f"✓ Created connection with session_id: {connection.session_id()}")

    # Verify the session ID exists and is a string
    assert connection.session_id() is not None
    assert isinstance(connection.session_id(), str)
    assert len(connection.session_id()) > 0
    print(f"✓ Session ID is valid: {connection.session_id()}")

    # Create another connection and verify it has a different ID
    text_node2 = Node.create_node(NodeType.TEXT, node_name="test_text2")
    fileout_node2 = Node.create_node(NodeType.FILE_OUT, node_name="test_fileout2")
    fileout_node2.set_input(0, text_node2, 0)
    connection2 = fileout_node2._inputs[0]

    print(f"✓ Created second connection with session_id: {connection2.session_id()}")

    # Verify IDs are different
    assert connection.session_id() != connection2.session_id()
    print(f"✓ Session IDs are unique")

    # Verify IDs are tracked in the class variable
    assert connection.session_id() in NodeConnection._existing_session_ids
    assert connection2.session_id() in NodeConnection._existing_session_ids
    print(f"✓ Session IDs are tracked in class variable")

    # Test __repr__
    repr_str = repr(connection)
    assert "session_id=" in repr_str
    assert connection.session_id() in repr_str
    print(f"✓ __repr__ includes session_id: {repr_str[:80]}...")

    print("\n✅ All tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_connection_session_ids()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
