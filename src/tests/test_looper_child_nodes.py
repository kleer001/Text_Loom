#!/usr/bin/env python3
"""
Test to verify looper node child nodes are properly created and registered.
This validates the fix for the looper node GUI visibility issue.
"""
import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType

def test_looper_child_nodes():
    """Test that looper node creates and registers child nodes correctly."""
    print("\n" + "="*60)
    print("Testing Looper Node Child Node Creation and Registration")
    print("="*60)

    # Create a looper node
    print("\n1. Creating looper node...")
    looper = Node.create_node(NodeType.LOOPER, node_name="test_looper")
    print(f"   ✓ Looper node created: {looper.path()}")

    # Verify child nodes exist as attributes
    print("\n2. Checking child nodes exist as attributes...")
    assert hasattr(looper, '_input_node'), "Looper missing _input_node attribute"
    assert hasattr(looper, '_output_node'), "Looper missing _output_node attribute"
    assert looper._input_node is not None, "_input_node is None"
    assert looper._output_node is not None, "_output_node is None"
    print(f"   ✓ _input_node: {looper._input_node.path()}")
    print(f"   ✓ _output_node: {looper._output_node.path()}")

    # Verify child nodes are in children list
    print("\n3. Checking child nodes are in _children list...")
    assert len(looper._children) == 2, f"Expected 2 children, got {len(looper._children)}"
    print(f"   ✓ Looper has {len(looper._children)} children")

    # Verify child nodes are registered in NodeEnvironment (CRITICAL FOR GUI)
    print("\n4. Checking child nodes are registered in NodeEnvironment...")
    all_nodes = NodeEnvironment.list_nodes()
    print(f"   All registered nodes: {all_nodes}")

    input_node_path = looper._input_node.path()
    output_node_path = looper._output_node.path()

    assert input_node_path in all_nodes, f"inputNullNode not registered! Path: {input_node_path}"
    assert output_node_path in all_nodes, f"outputNullNode not registered! Path: {output_node_path}"
    print(f"   ✓ inputNullNode registered: {input_node_path}")
    print(f"   ✓ outputNullNode registered: {output_node_path}")

    # Verify we can retrieve them from NodeEnvironment
    print("\n5. Verifying child nodes can be retrieved from NodeEnvironment...")
    retrieved_input = NodeEnvironment.node_from_name(input_node_path)
    retrieved_output = NodeEnvironment.node_from_name(output_node_path)

    assert retrieved_input is not None, "Cannot retrieve inputNullNode from NodeEnvironment"
    assert retrieved_output is not None, "Cannot retrieve outputNullNode from NodeEnvironment"
    assert retrieved_input is looper._input_node, "Retrieved input node is not the same object"
    assert retrieved_output is looper._output_node, "Retrieved output node is not the same object"
    print(f"   ✓ inputNullNode retrieved successfully")
    print(f"   ✓ outputNullNode retrieved successfully")

    # Verify correct names
    print("\n6. Verifying child node names...")
    assert looper._input_node.name() == "inputNullNode", f"Wrong input node name: {looper._input_node.name()}"
    assert looper._output_node.name() == "outputNullNode", f"Wrong output node name: {looper._output_node.name()}"
    print(f"   ✓ Child nodes have correct names")

    # Verify node types
    print("\n7. Verifying child node types...")
    assert looper._input_node.type() == NodeType.INPUT_NULL, "Wrong input node type"
    assert looper._output_node.type() == NodeType.OUTPUT_NULL, "Wrong output node type"
    print(f"   ✓ Child nodes have correct types")

    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nLooper node child nodes are properly created and registered.")
    print("They will appear in API responses and be visible in the GUI.")
    print()

    return True

if __name__ == "__main__":
    try:
        test_looper_child_nodes()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
