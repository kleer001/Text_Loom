#!/usr/bin/env python3
"""
Comprehensive test script for integer index standardization.

Tests that all node types correctly use integer indices for inputs/outputs
and that connections work properly with the new system.
"""

import sys
sys.path.insert(0, '..')

from core.base_classes import Node, NodeType, NodeEnvironment


def test_node_indices(node_type: NodeType, expected_inputs: int, expected_outputs: int):
    """Test that a node type uses integer indices correctly."""
    print(f"\n{'='*60}")
    print(f"Testing {node_type.value}")
    print('='*60)

    # Create node
    node = Node.create_node(node_type, f"test_{node_type.value}")

    # Check input_names returns Dict[int, str]
    input_names = node.input_names()
    print(f"Input names: {input_names}")

    for idx, name in input_names.items():
        if not isinstance(idx, int):
            print(f"❌ FAIL: Input index {idx} is {type(idx).__name__}, expected int")
            return False
        if not isinstance(name, str):
            print(f"❌ FAIL: Input name {name} is {type(name).__name__}, expected str")
            return False

    if len(input_names) != expected_inputs:
        print(f"⚠️  WARNING: Expected {expected_inputs} inputs, got {len(input_names)}")

    # Check output_names returns Dict[int, str]
    output_names = node.output_names()
    print(f"Output names: {output_names}")

    for idx, name in output_names.items():
        if not isinstance(idx, int):
            print(f"❌ FAIL: Output index {idx} is {type(idx).__name__}, expected int")
            return False
        if not isinstance(name, str):
            print(f"❌ FAIL: Output name {name} is {type(name).__name__}, expected str")
            return False

    if len(output_names) != expected_outputs:
        print(f"⚠️  WARNING: Expected {expected_outputs} outputs, got {len(output_names)}")

    print(f"✅ PASS: All indices are integers")
    return True


def test_connection_creation():
    """Test that connections work with integer indices."""
    print(f"\n{'='*60}")
    print("Testing Connection Creation with Integer Indices")
    print('='*60)

    # Create two text nodes
    text1 = Node.create_node(NodeType.TEXT, "connection_test_1")
    text2 = Node.create_node(NodeType.TEXT, "connection_test_2")

    # Test valid connection with integers
    try:
        text2.set_input(0, text1, 0)
        print("✅ PASS: Connection created with integer indices (0, 0)")
    except Exception as e:
        print(f"❌ FAIL: Could not create connection with integers: {e}")
        return False

    # Verify connection exists and has integer indices
    conn = text2._inputs.get(0)
    if not conn:
        print("❌ FAIL: Connection not found in _inputs")
        return False

    if not isinstance(conn.input_index(), int):
        print(f"❌ FAIL: Connection input_index is {type(conn.input_index()).__name__}, expected int")
        return False

    if not isinstance(conn.output_index(), int):
        print(f"❌ FAIL: Connection output_index is {type(conn.output_index()).__name__}, expected int")
        return False

    print(f"✅ PASS: Connection has integer indices: input={conn.input_index()}, output={conn.output_index()}")

    # Test that string indices are rejected
    text3 = Node.create_node(NodeType.TEXT, "connection_test_3")
    try:
        text3.set_input("input", text1, "output")  # type: ignore
        print("❌ FAIL: String indices should be rejected but were accepted!")
        return False
    except TypeError as e:
        print(f"✅ PASS: String indices correctly rejected: {e}")

    return True


def test_multi_output_node():
    """Test multi-output nodes (SplitNode, SectionNode, FolderNode)."""
    print(f"\n{'='*60}")
    print("Testing Multi-Output Node (SplitNode)")
    print('='*60)

    split = Node.create_node(NodeType.SPLIT, "split_test")

    # SplitNode has 3 outputs
    output_names = split.output_names()
    print(f"Split node outputs: {output_names}")

    if len(output_names) != 3:
        print(f"❌ FAIL: Expected 3 outputs, got {len(output_names)}")
        return False

    # Check all indices are 0, 1, 2
    expected_indices = {0, 1, 2}
    actual_indices = set(output_names.keys())

    if actual_indices != expected_indices:
        print(f"❌ FAIL: Expected indices {expected_indices}, got {actual_indices}")
        return False

    print(f"✅ PASS: SplitNode has correct integer indices: {actual_indices}")

    # Test connecting to different outputs
    text1 = Node.create_node(NodeType.TEXT, "split_out_0")
    text2 = Node.create_node(NodeType.TEXT, "split_out_1")

    try:
        text1.set_input(0, split, 0)  # Connect to first output
        text2.set_input(0, split, 1)  # Connect to second output
        print("✅ PASS: Successfully connected to multiple integer-indexed outputs")
    except Exception as e:
        print(f"❌ FAIL: Could not connect to outputs: {e}")
        return False

    return True


def test_dynamic_input_node():
    """Test MergeNode with dynamic inputs."""
    print(f"\n{'='*60}")
    print("Testing Dynamic Input Node (MergeNode)")
    print('='*60)

    merge = Node.create_node(NodeType.MERGE, "merge_test")
    text1 = Node.create_node(NodeType.TEXT, "merge_in_1")
    text2 = Node.create_node(NodeType.TEXT, "merge_in_2")

    # Initially, MergeNode has no inputs
    print(f"Initial input names: {merge.input_names()}")

    # Add first connection
    merge.set_input(0, text1, 0)
    input_names_after_1 = merge.input_names()
    print(f"After 1st connection: {input_names_after_1}")

    if 0 not in input_names_after_1:
        print(f"❌ FAIL: Input 0 not found after connection")
        return False

    # Add second connection
    merge.set_input(1, text2, 0)
    input_names_after_2 = merge.input_names()
    print(f"After 2nd connection: {input_names_after_2}")

    if 0 not in input_names_after_2 or 1 not in input_names_after_2:
        print(f"❌ FAIL: Inputs 0 and 1 not found after two connections")
        return False

    print(f"✅ PASS: MergeNode dynamically creates integer-indexed inputs")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("INTEGER INDEX STANDARDIZATION TEST SUITE")
    print("="*60)

    all_passed = True

    # Test each node type
    node_tests = [
        (NodeType.TEXT, 1, 1),
        (NodeType.JSON, 1, 1),
        (NodeType.FILE_OUT, 1, 1),
        (NodeType.FILE_IN, 0, 1),
        (NodeType.MAKE_LIST, 1, 1),
        (NodeType.SPLIT, 1, 3),
        (NodeType.SECTION, 1, 3),
        (NodeType.FOLDER, 0, 3),
        (NodeType.MERGE, 0, 1),  # Dynamic inputs
        (NodeType.LOOPER, 1, 1),
        (NodeType.QUERY, 1, 1),
    ]

    for node_type, exp_in, exp_out in node_tests:
        if not test_node_indices(node_type, exp_in, exp_out):
            all_passed = False

    # Test connection functionality
    if not test_connection_creation():
        all_passed = False

    if not test_multi_output_node():
        all_passed = False

    if not test_dynamic_input_node():
        all_passed = False

    # Final summary
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("Integer index standardization is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the failures above.")
    print('='*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
