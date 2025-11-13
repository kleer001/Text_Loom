#!/usr/bin/env python3
"""
API-level connection tests.

Tests connections through the API layer to ensure:
1. API accepts integer indices
2. API rejects non-integer indices
3. API validation works correctly
4. ConnectionResponse has correct integer types
"""

import sys
sys.path.insert(0, '..')

from core.base_classes import Node, NodeType, NodeEnvironment
from api.models import (
    ConnectionRequest,
    ConnectionDeleteRequest,
    connection_to_response
)


def cleanup_nodes():
    """Clean up all nodes from environment."""
    NodeEnvironment.nodes.clear()


def test_api_connection_request_integers():
    """Test that ConnectionRequest accepts integer indices."""
    print("\n" + "="*60)
    print("TEST 1: API ConnectionRequest with Integer Indices")
    print("="*60)

    # Create a valid ConnectionRequest with integers
    request = ConnectionRequest(
        source_node_path="/text1",
        source_output_index=0,  # Integer
        target_node_path="/text2",
        target_input_index=0    # Integer
    )

    print(f"ConnectionRequest created:")
    print(f"  source_output_index: {request.source_output_index} (type: {type(request.source_output_index).__name__})")
    print(f"  target_input_index: {request.target_input_index} (type: {type(request.target_input_index).__name__})")

    # Verify types
    assert isinstance(request.source_output_index, int), "source_output_index should be int"
    assert isinstance(request.target_input_index, int), "target_input_index should be int"

    print("✅ PASS: ConnectionRequest accepts integer indices")
    return True


def test_api_connection_request_validation():
    """Test that ConnectionRequest validates index types."""
    print("\n" + "="*60)
    print("TEST 2: API ConnectionRequest Type Validation")
    print("="*60)

    # Try to create request with string indices (should fail with Pydantic)
    try:
        request = ConnectionRequest(
            source_node_path="/text1",
            source_output_index="output",  # String - should fail
            target_node_path="/text2",
            target_input_index=0
        )
        print("❌ FAIL: Should have rejected string index")
        return False
    except Exception as e:
        print(f"✅ PASS: Correctly rejected string index")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)[:100]}...")

    # Try with float (should coerce to int or fail)
    try:
        request = ConnectionRequest(
            source_node_path="/text1",
            source_output_index=0.0,  # Float
            target_node_path="/text2",
            target_input_index=0
        )
        # Pydantic might coerce 0.0 → 0
        if isinstance(request.source_output_index, int):
            print(f"✅ PASS: Float coerced to int: {request.source_output_index}")
        else:
            print(f"⚠️  WARNING: Float not coerced: {type(request.source_output_index).__name__}")
    except Exception as e:
        print(f"✅ PASS: Correctly rejected float")
        print(f"  Error: {str(e)[:100]}...")

    return True


def test_api_connection_response():
    """Test that connection_to_response returns integer indices."""
    print("\n" + "="*60)
    print("TEST 3: API ConnectionResponse Integer Indices")
    print("="*60)

    cleanup_nodes()

    # Create real nodes and connection
    text1 = Node.create_node(NodeType.TEXT, "api_text1")
    text2 = Node.create_node(NodeType.TEXT, "api_text2")
    text2.set_input(0, text1, 0)

    connection = text2._inputs[0]

    # Convert to API response
    response = connection_to_response(connection)

    print(f"ConnectionResponse:")
    print(f"  source_output_index: {response.source_output_index} (type: {type(response.source_output_index).__name__})")
    print(f"  target_input_index: {response.target_input_index} (type: {type(response.target_input_index).__name__})")

    # Verify types are integers
    assert isinstance(response.source_output_index, int), f"source_output_index should be int, got {type(response.source_output_index).__name__}"
    assert isinstance(response.target_input_index, int), f"target_input_index should be int, got {type(response.target_input_index).__name__}"

    # Verify values
    assert response.source_output_index == 0, f"Expected 0, got {response.source_output_index}"
    assert response.target_input_index == 0, f"Expected 0, got {response.target_input_index}"

    print("✅ PASS: ConnectionResponse has correct integer indices")
    return True


def test_api_multi_output_response():
    """Test ConnectionResponse with multi-output node."""
    print("\n" + "="*60)
    print("TEST 4: API Response for Multi-Output Node")
    print("="*60)

    cleanup_nodes()

    # Create section node with 3 outputs
    section = Node.create_node(NodeType.SECTION, "api_section")
    text1 = Node.create_node(NodeType.TEXT, "api_out1")
    text2 = Node.create_node(NodeType.TEXT, "api_out2")

    # Connect to different outputs
    text1.set_input(0, section, 1)  # Output 1
    text2.set_input(0, section, 2)  # Output 2

    # Convert both connections to responses
    conn1 = text1._inputs[0]
    conn2 = text2._inputs[0]

    response1 = connection_to_response(conn1)
    response2 = connection_to_response(conn2)

    print(f"Connection 1 (section[1] → text1):")
    print(f"  source_output_index: {response1.source_output_index} (type: {type(response1.source_output_index).__name__})")

    print(f"Connection 2 (section[2] → text2):")
    print(f"  source_output_index: {response2.source_output_index} (type: {type(response2.source_output_index).__name__})")

    # Verify correct indices
    assert response1.source_output_index == 1, f"Expected 1, got {response1.source_output_index}"
    assert response2.source_output_index == 2, f"Expected 2, got {response2.source_output_index}"

    # Verify types
    assert isinstance(response1.source_output_index, int), "Should be int"
    assert isinstance(response2.source_output_index, int), "Should be int"

    print("✅ PASS: Multi-output indices correctly preserved as integers")
    return True


def test_api_delete_request():
    """Test ConnectionDeleteRequest with integer indices."""
    print("\n" + "="*60)
    print("TEST 5: API ConnectionDeleteRequest")
    print("="*60)

    # Create delete request with integers
    request = ConnectionDeleteRequest(
        source_node_path="/text1",
        source_output_index=2,  # Integer
        target_node_path="/text2",
        target_input_index=1    # Integer
    )

    print(f"ConnectionDeleteRequest:")
    print(f"  source_output_index: {request.source_output_index} (type: {type(request.source_output_index).__name__})")
    print(f"  target_input_index: {request.target_input_index} (type: {type(request.target_input_index).__name__})")

    # Verify types
    assert isinstance(request.source_output_index, int), "Should be int"
    assert isinstance(request.target_input_index, int), "Should be int"

    print("✅ PASS: ConnectionDeleteRequest uses integer indices")
    return True


def test_api_json_serialization():
    """Test that API models serialize to JSON correctly."""
    print("\n" + "="*60)
    print("TEST 6: JSON Serialization of Integer Indices")
    print("="*60)

    cleanup_nodes()

    # Create connection
    text1 = Node.create_node(NodeType.TEXT, "json_text1")
    text2 = Node.create_node(NodeType.TEXT, "json_text2")
    text2.set_input(0, text1, 0)

    connection = text2._inputs[0]
    response = connection_to_response(connection)

    # Serialize to dict (what would be sent as JSON)
    json_dict = response.model_dump()

    print(f"JSON serialization:")
    print(f"  source_output_index: {json_dict['source_output_index']} (type: {type(json_dict['source_output_index']).__name__})")
    print(f"  target_input_index: {json_dict['target_input_index']} (type: {type(json_dict['target_input_index']).__name__})")

    # Verify JSON has integers (not strings)
    assert isinstance(json_dict['source_output_index'], int), "JSON should contain int"
    assert isinstance(json_dict['target_input_index'], int), "JSON should contain int"

    # Verify JSON representation
    import json
    json_str = json.dumps(json_dict)
    print(f"\nJSON string excerpt: ...{json_str[100:200]}...")

    # Verify the JSON contains numbers, not quoted strings
    assert '"source_output_index": 0' in json_str or '"source_output_index":0' in json_str, "Should be number in JSON"

    print("✅ PASS: Integer indices serialize correctly to JSON")
    return True


def main():
    """Run all API connection tests."""
    print("\n" + "="*70)
    print("API CONNECTION TEST SUITE")
    print("="*70)
    print("Testing API layer with integer indices")

    all_passed = True

    tests = [
        ("ConnectionRequest Integers", test_api_connection_request_integers),
        ("ConnectionRequest Validation", test_api_connection_request_validation),
        ("ConnectionResponse", test_api_connection_response),
        ("Multi-Output Response", test_api_multi_output_response),
        ("ConnectionDeleteRequest", test_api_delete_request),
        ("JSON Serialization", test_api_json_serialization),
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
        print("✅ ALL API CONNECTION TESTS PASSED!")
        print("\nVerified:")
        print("  ✓ API models accept integer indices")
        print("  ✓ API models reject non-integer indices")
        print("  ✓ ConnectionResponse returns integers")
        print("  ✓ Multi-output indices preserved")
        print("  ✓ JSON serialization correct")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review failures above")
    print("="*70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
