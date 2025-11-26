#!/usr/bin/env python3
"""
Test for looper connection routing.

This test verifies that connections to InputNullNode (displayed as looper_start in GUI)
are correctly routed to the parent LooperNode.

Background:
- LooperNode creates internal InputNullNode and OutputNullNode
- GUI displays these as looper_start and looper_end
- When user connects to looper_start, GUI sends InputNullNode path
- API should redirect this to the parent LooperNode
"""

import sys
sys.path.insert(0, '..')

from core.base_classes import Node, NodeType, NodeEnvironment
from api.routers.connections import route_connection_target
from core.input_null_node import InputNullNode


def cleanup_nodes():
    """Clean up all nodes from environment."""
    NodeEnvironment.nodes.clear()


def test_looper_connection_routing():
    """Test that connections to InputNullNode are routed to parent LooperNode."""
    print("\n" + "="*70)
    print("TEST: Looper Connection Routing")
    print("="*70)

    cleanup_nodes()

    # Create a looper node (which creates internal InputNullNode and OutputNullNode)
    looper = Node.create_node(NodeType.LOOPER, "test_looper")

    # Wait for internal nodes to be created
    import time
    time.sleep(0.1)

    # Verify internal nodes exist
    input_null_node = NodeEnvironment.node_from_name("/test_looper/inputNullNode")
    assert input_null_node is not None, "InputNullNode should exist"
    assert isinstance(input_null_node, InputNullNode), "Should be InputNullNode instance"

    print(f"✓ Created LooperNode at: {looper.path()}")
    print(f"✓ InputNullNode at: {input_null_node.path()}")

    # Test the routing function
    target_node, target_input_index = route_connection_target(
        input_null_node.path(),
        0
    )

    print(f"\nRouting test:")
    print(f"  Input path: {input_null_node.path()}")
    print(f"  Routed to: {target_node.path()}")
    print(f"  Node type: {type(target_node).__name__}")

    # Verify the connection was routed to the parent LooperNode
    assert target_node.path() == looper.path(), f"Should route to LooperNode, got {target_node.path()}"
    assert target_input_index == 0, f"Input index should be preserved, got {target_input_index}"

    print("✅ PASS: Connection correctly routed to parent LooperNode")
    return True


def test_looper_connection_creation():
    """Test creating actual connection to looper via InputNullNode path."""
    print("\n" + "="*70)
    print("TEST: Looper Connection Creation")
    print("="*70)

    cleanup_nodes()

    # Create source node (text node)
    text_node = Node.create_node(NodeType.TEXT, "source_text")
    text_node._parms["text"].set("Test data")
    text_node.cook()

    # Create looper node
    looper = Node.create_node(NodeType.LOOPER, "target_looper")

    # Wait for internal nodes
    import time
    time.sleep(0.1)

    input_null_node = NodeEnvironment.node_from_name("/target_looper/inputNullNode")
    assert input_null_node is not None, "InputNullNode should exist"

    print(f"✓ Created source TextNode at: {text_node.path()}")
    print(f"✓ Created LooperNode at: {looper.path()}")
    print(f"✓ InputNullNode at: {input_null_node.path()}")

    # Simulate GUI behavior: route connection through InputNullNode path
    target_node, target_input_index = route_connection_target(
        input_null_node.path(),
        0
    )

    # Create the connection
    target_node.set_input(
        target_input_index,
        text_node,
        0
    )

    # Verify connection was created on the LooperNode
    connection = looper._inputs.get(0)
    assert connection is not None, "Connection should exist on LooperNode"
    assert connection.output_node().path() == text_node.path(), "Connection should come from text_node"
    assert connection.input_node().path() == looper.path(), "Connection should go to looper"

    print(f"\nConnection verification:")
    print(f"  Source: {connection.output_node().path()}")
    print(f"  Target: {connection.input_node().path()}")
    print(f"  Input index: {connection.input_index()}")

    print("✅ PASS: Connection created successfully via routing")
    return True


def test_regular_node_not_routed():
    """Test that regular nodes are not affected by routing."""
    print("\n" + "="*70)
    print("TEST: Regular Node Not Routed")
    print("="*70)

    cleanup_nodes()

    # Create regular text node
    text_node = Node.create_node(NodeType.TEXT, "regular_text")

    print(f"✓ Created regular TextNode at: {text_node.path()}")

    # Test routing with regular node
    target_node, target_input_index = route_connection_target(
        text_node.path(),
        0
    )

    # Verify no routing occurred
    assert target_node.path() == text_node.path(), "Regular node should not be routed"
    assert target_input_index == 0, "Input index should be unchanged"

    print(f"\nRouting test:")
    print(f"  Input path: {text_node.path()}")
    print(f"  Routed to: {target_node.path()}")
    print(f"  Result: No routing (correct)")

    print("✅ PASS: Regular nodes are not affected by routing")
    return True


def main():
    """Run all looper connection routing tests."""
    print("\n" + "="*70)
    print("LOOPER CONNECTION ROUTING TEST SUITE")
    print("="*70)
    print("Testing connection routing for InputNullNode → LooperNode")

    all_passed = True

    tests = [
        ("Looper Connection Routing", test_looper_connection_routing),
        ("Looper Connection Creation", test_looper_connection_creation),
        ("Regular Node Not Routed", test_regular_node_not_routed),
    ]

    for test_name, test_func in tests:
        try:
            if not test_func():
                print(f"\n❌ FAILED: {test_name}")
                all_passed = False
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    # Final summary
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL LOOPER CONNECTION ROUTING TESTS PASSED!")
        print("\nVerified:")
        print("  ✓ InputNullNode connections routed to parent LooperNode")
        print("  ✓ Actual connections created successfully")
        print("  ✓ Regular nodes not affected by routing")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review failures above")
    print("="*70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
