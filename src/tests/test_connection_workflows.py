#!/usr/bin/env python3
"""
Comprehensive connection workflow tests.

Tests real-world connection scenarios:
1. Creating node connections
2. Changing node connections (reconnecting)
3. Multi-output node connections (SectionNode, SplitNode)
4. Deleting connections
5. Reconnecting nodes in different configurations
"""

import sys
sys.path.insert(0, '..')

from core.base_classes import Node, NodeType, NodeEnvironment


def cleanup_nodes():
    """Clean up all nodes from environment."""
    NodeEnvironment.nodes.clear()


def test_basic_connection():
    """Test 1: Basic node connection."""
    print("\n" + "="*60)
    print("TEST 1: Basic Node Connection")
    print("="*60)

    cleanup_nodes()

    # Create two text nodes
    text1 = Node.create_node(NodeType.TEXT, "basic_text1")
    text2 = Node.create_node(NodeType.TEXT, "basic_text2")

    print(f"Created nodes: {text1.name()}, {text2.name()}")
    print(f"Initial connections on text2: {len(text2._inputs)}")

    # Connect text1 output to text2 input
    text2.set_input(0, text1, 0)

    # Verify connection
    assert 0 in text2._inputs, "Connection not found in _inputs"
    conn = text2._inputs[0]

    assert conn.output_node() == text1, "Wrong output node"
    assert conn.input_node() == text2, "Wrong input node"
    assert conn.output_index() == 0, f"Wrong output index: {conn.output_index()}"
    assert conn.input_index() == 0, f"Wrong input index: {conn.input_index()}"

    # Verify it's in the output node's outputs
    assert 0 in text1._outputs, "Connection not found in output node's _outputs"
    assert conn in text1._outputs[0], "Connection not in output list"

    print(f"✅ PASS: Connection created successfully")
    print(f"  - text1[{conn.output_index()}] → text2[{conn.input_index()}]")
    print(f"  - Connection ID: {conn.session_id()}")
    return True


def test_changing_connection():
    """Test 2: Changing/replacing a connection."""
    print("\n" + "="*60)
    print("TEST 2: Changing Node Connection (Reconnecting)")
    print("="*60)

    cleanup_nodes()

    # Create three text nodes
    text1 = Node.create_node(NodeType.TEXT, "change_text1")
    text2 = Node.create_node(NodeType.TEXT, "change_text2")
    text3 = Node.create_node(NodeType.TEXT, "change_text3")

    # Initial connection: text1 → text3
    text3.set_input(0, text1, 0)
    initial_conn = text3._inputs[0]
    initial_id = initial_conn.session_id()

    print(f"Initial: {text1.name()}[0] → {text3.name()}[0]")
    print(f"Initial connection ID: {initial_id}")

    # Change connection: text2 → text3 (should replace text1 → text3)
    text3.set_input(0, text2, 0)
    new_conn = text3._inputs[0]
    new_id = new_conn.session_id()

    print(f"Changed: {text2.name()}[0] → {text3.name()}[0]")
    print(f"New connection ID: {new_id}")

    # Verify the connection changed
    assert new_id != initial_id, "Connection ID should be different"
    assert new_conn.output_node() == text2, "Should connect to text2 now"
    assert new_conn.output_node() != text1, "Should not connect to text1"

    # Verify text1's outputs are cleaned up
    if 0 in text1._outputs:
        assert initial_conn not in text1._outputs[0], "Old connection still in text1 outputs"

    # Verify text2's outputs have the new connection
    assert 0 in text2._outputs, "text2 should have output connections"
    assert new_conn in text2._outputs[0], "New connection should be in text2 outputs"

    print(f"✅ PASS: Connection successfully changed")
    print(f"  - Old connection cleaned up")
    print(f"  - New connection established")
    return True


def test_multi_output_connections():
    """Test 3: Connecting to different outputs of multi-output nodes."""
    print("\n" + "="*60)
    print("TEST 3: Multi-Output Node Connections (SectionNode)")
    print("="*60)

    cleanup_nodes()

    # Create section node (3 outputs) and 3 text nodes
    section = Node.create_node(NodeType.SECTION, "section")
    text1 = Node.create_node(NodeType.TEXT, "section_out0")
    text2 = Node.create_node(NodeType.TEXT, "section_out1")
    text3 = Node.create_node(NodeType.TEXT, "section_out2")

    # Verify section has 3 outputs
    output_names = section.output_names()
    print(f"Section outputs: {output_names}")
    assert len(output_names) == 3, f"Expected 3 outputs, got {len(output_names)}"
    assert 0 in output_names, "Missing output 0"
    assert 1 in output_names, "Missing output 1"
    assert 2 in output_names, "Missing output 2"

    # Connect each output to a different text node
    text1.set_input(0, section, 0)  # First section output
    text2.set_input(0, section, 1)  # Second section output
    text3.set_input(0, section, 2)  # Third section output

    print(f"Connected outputs:")
    print(f"  - section[0] ({output_names[0]}) → text1")
    print(f"  - section[1] ({output_names[1]}) → text2")
    print(f"  - section[2] ({output_names[2]}) → text3")

    # Verify all connections exist
    assert 0 in section._outputs, "Missing output 0 connections"
    assert 1 in section._outputs, "Missing output 1 connections"
    assert 2 in section._outputs, "Missing output 2 connections"

    # Verify each output has exactly one connection
    assert len(section._outputs[0]) == 1, f"Output 0 should have 1 connection, has {len(section._outputs[0])}"
    assert len(section._outputs[1]) == 1, f"Output 1 should have 1 connection, has {len(section._outputs[1])}"
    assert len(section._outputs[2]) == 1, f"Output 2 should have 1 connection, has {len(section._outputs[2])}"

    # Verify connections go to correct nodes
    conn0 = section._outputs[0][0]
    conn1 = section._outputs[1][0]
    conn2 = section._outputs[2][0]

    assert conn0.input_node() == text1, "Output 0 should connect to text1"
    assert conn1.input_node() == text2, "Output 1 should connect to text2"
    assert conn2.input_node() == text3, "Output 2 should connect to text3"

    # Verify correct output indices
    assert conn0.output_index() == 0, f"conn0 should use output 0, got {conn0.output_index()}"
    assert conn1.output_index() == 1, f"conn1 should use output 1, got {conn1.output_index()}"
    assert conn2.output_index() == 2, f"conn2 should use output 2, got {conn2.output_index()}"

    print(f"✅ PASS: All three outputs connected correctly")
    print(f"  - Each output has distinct connection")
    print(f"  - Correct output indices preserved")
    return True


def test_deleting_connections():
    """Test 4: Deleting connections."""
    print("\n" + "="*60)
    print("TEST 4: Deleting Connections")
    print("="*60)

    cleanup_nodes()

    # Create nodes and connections
    text1 = Node.create_node(NodeType.TEXT, "delete_text1")
    text2 = Node.create_node(NodeType.TEXT, "delete_text2")
    text3 = Node.create_node(NodeType.TEXT, "delete_text3")

    # Create two connections
    text2.set_input(0, text1, 0)
    text3.set_input(0, text1, 0)

    conn_to_text2 = text2._inputs[0]
    conn_to_text3 = text3._inputs[0]

    print(f"Created connections:")
    print(f"  - text1 → text2 (ID: {conn_to_text2.session_id()[:8]}...)")
    print(f"  - text1 → text3 (ID: {conn_to_text3.session_id()[:8]}...)")

    # Verify initial state
    assert 0 in text2._inputs, "text2 should have input"
    assert 0 in text3._inputs, "text3 should have input"
    assert len(text1._outputs[0]) == 2, f"text1 should have 2 outputs, has {len(text1._outputs[0])}"

    # Delete connection to text2
    print(f"\nDeleting connection to text2...")
    text2.remove_connection(conn_to_text2)

    # Verify text2 connection removed
    assert 0 not in text2._inputs, "text2 should have no input after deletion"

    # Verify text1's outputs updated
    assert len(text1._outputs[0]) == 1, f"text1 should have 1 output left, has {len(text1._outputs[0])}"
    assert conn_to_text2 not in text1._outputs[0], "Deleted connection still in outputs"
    assert conn_to_text3 in text1._outputs[0], "Remaining connection should still exist"

    # Verify text3 connection still exists
    assert 0 in text3._inputs, "text3 should still have input"
    assert text3._inputs[0] == conn_to_text3, "text3 connection should be unchanged"

    print(f"✅ PASS: Connection deleted successfully")
    print(f"  - Removed from input node")
    print(f"  - Removed from output node")
    print(f"  - Other connections preserved")

    # Delete remaining connection
    print(f"\nDeleting connection to text3...")
    text3.remove_connection(conn_to_text3)

    assert 0 not in text3._inputs, "text3 should have no input after deletion"

    # text1 should have no outputs now
    if 0 in text1._outputs:
        assert len(text1._outputs[0]) == 0, "text1 should have no outputs left"

    print(f"✅ PASS: All connections deleted successfully")
    return True


def test_reconnecting_different_configs():
    """Test 5: Reconnecting nodes in different configurations."""
    print("\n" + "="*60)
    print("TEST 5: Reconnecting in Different Configurations")
    print("="*60)

    cleanup_nodes()

    # Create a split node (3 outputs) and multiple text nodes
    split = Node.create_node(NodeType.SPLIT, "recon_split")
    text1 = Node.create_node(NodeType.TEXT, "recon_text1")
    text2 = Node.create_node(NodeType.TEXT, "recon_text2")

    print(f"Split node outputs: {split.output_names()}")

    # Config 1: text1 connected to output 0
    print(f"\nConfig 1: split[0] → text1")
    text1.set_input(0, split, 0)

    assert text1._inputs[0].output_index() == 0, "Should connect to output 0"
    print(f"  ✓ Connected to output 0")

    # Config 2: Reconnect text1 to output 1
    print(f"\nConfig 2: split[1] → text1 (reconnect)")
    text1.set_input(0, split, 1)

    assert text1._inputs[0].output_index() == 1, "Should connect to output 1"
    assert split._outputs[0] == [] or 0 not in split._outputs, "Output 0 should be empty"
    assert len(split._outputs[1]) == 1, "Output 1 should have 1 connection"
    print(f"  ✓ Reconnected to output 1")
    print(f"  ✓ Output 0 cleaned up")

    # Config 3: Add text2 to output 0, text1 stays on output 1
    print(f"\nConfig 3: split[0] → text2, split[1] → text1")
    text2.set_input(0, split, 0)

    assert text1._inputs[0].output_index() == 1, "text1 should still be on output 1"
    assert text2._inputs[0].output_index() == 0, "text2 should be on output 0"
    assert len(split._outputs[0]) == 1, "Output 0 should have 1 connection"
    assert len(split._outputs[1]) == 1, "Output 1 should have 1 connection"
    print(f"  ✓ Both outputs connected simultaneously")

    # Config 4: Swap connections
    print(f"\nConfig 4: Swap - split[0] → text1, split[1] → text2")
    text1.set_input(0, split, 0)  # Move text1 to output 0
    text2.set_input(0, split, 1)  # Move text2 to output 1

    assert text1._inputs[0].output_index() == 0, "text1 should be on output 0 now"
    assert text2._inputs[0].output_index() == 1, "text2 should be on output 1 now"
    print(f"  ✓ Connections swapped successfully")

    # Config 5: Multiple nodes on same output
    print(f"\nConfig 5: split[2] → text1, split[2] → text2 (both on output 2)")
    text1.set_input(0, split, 2)
    text2.set_input(0, split, 2)

    assert text1._inputs[0].output_index() == 2, "text1 should be on output 2"
    assert text2._inputs[0].output_index() == 2, "text2 should be on output 2"
    assert len(split._outputs[2]) == 2, f"Output 2 should have 2 connections, has {len(split._outputs[2])}"
    print(f"  ✓ Multiple nodes connected to same output")

    print(f"\n✅ PASS: All reconnection configurations work correctly")
    return True


def test_complex_workflow():
    """Test 6: Complex real-world workflow."""
    print("\n" + "="*60)
    print("TEST 6: Complex Real-World Workflow")
    print("="*60)

    cleanup_nodes()

    # Simulate: FileIn → Section → (3 outputs) → Text nodes → Merge
    file_in = Node.create_node(NodeType.FILE_IN, "source")
    section = Node.create_node(NodeType.SECTION, "section")
    text1 = Node.create_node(NodeType.TEXT, "process1")
    text2 = Node.create_node(NodeType.TEXT, "process2")
    text3 = Node.create_node(NodeType.TEXT, "process3")
    merge = Node.create_node(NodeType.MERGE, "merge")

    print("Created workflow: FileIn → Section → 3×Text → Merge")

    # Build the pipeline
    section.set_input(0, file_in, 0)
    text1.set_input(0, section, 0)
    text2.set_input(0, section, 1)
    text3.set_input(0, section, 2)
    merge.set_input(0, text1, 0)
    merge.set_input(1, text2, 0)
    merge.set_input(2, text3, 0)

    print("\nConnections created:")
    print(f"  file_in → section")
    print(f"  section[0] → text1")
    print(f"  section[1] → text2")
    print(f"  section[2] → text3")
    print(f"  text1 → merge[0]")
    print(f"  text2 → merge[1]")
    print(f"  text3 → merge[2]")

    # Verify the pipeline
    assert len(section._inputs) == 1, "Section should have 1 input"
    assert len(section._outputs) == 3, "Section should have 3 outputs"
    assert len(merge._inputs) == 3, "Merge should have 3 inputs"

    # Verify merge dynamic input names
    merge_inputs = merge.input_names()
    print(f"\nMerge dynamic inputs: {merge_inputs}")
    assert 0 in merge_inputs, "Merge should have input 0"
    assert 1 in merge_inputs, "Merge should have input 1"
    assert 2 in merge_inputs, "Merge should have input 2"

    # Now modify: Remove text2, connect section[1] directly to merge[1]
    print(f"\nModifying: Bypass text2, connect section[1] → merge[1] directly")

    old_conn = text2._inputs[0]
    text2.remove_connection(old_conn)
    merge.set_input(1, section, 1)

    # Verify modification
    assert 0 not in text2._inputs, "text2 should have no inputs"
    assert merge._inputs[1].output_node() == section, "merge[1] should connect to section"
    assert merge._inputs[1].output_index() == 1, "Should use section output 1"

    print(f"  ✓ text2 bypassed successfully")
    print(f"  ✓ Direct connection established")

    print(f"\n✅ PASS: Complex workflow created and modified successfully")
    return True


def main():
    """Run all connection workflow tests."""
    print("\n" + "="*70)
    print("CONNECTION WORKFLOW TEST SUITE")
    print("="*70)
    print("Testing real-world connection scenarios with integer indices")

    all_passed = True

    tests = [
        ("Basic Connection", test_basic_connection),
        ("Changing Connections", test_changing_connection),
        ("Multi-Output Connections", test_multi_output_connections),
        ("Deleting Connections", test_deleting_connections),
        ("Reconnecting Configs", test_reconnecting_different_configs),
        ("Complex Workflow", test_complex_workflow),
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
        print("✅ ALL CONNECTION WORKFLOW TESTS PASSED!")
        print("\nVerified:")
        print("  ✓ Basic node connections")
        print("  ✓ Changing/replacing connections")
        print("  ✓ Multi-output node connections (Section, Split)")
        print("  ✓ Deleting connections cleanly")
        print("  ✓ Reconnecting in various configurations")
        print("  ✓ Complex real-world workflows")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review failures above")
    print("="*70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
