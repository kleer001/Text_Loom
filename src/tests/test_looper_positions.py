#!/usr/bin/env python3
"""
Test to verify looper node internal nodes have proper initial positions.
"""
import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType

def test_looper_position_initialization():
    """Test that looper node internal nodes are created with proper position offsets."""
    print("\n" + "="*60)
    print("Testing Looper Node Internal Node Position Initialization")
    print("="*60)

    print("\n1. Creating looper node at default position [0.0, 0.0]...")
    looper = Node.create_node(
        NodeType.LOOPER,
        node_name="test_looper_pos"
    )
    print(f"   ✓ Looper node created: {looper.path()}")
    print(f"   ✓ Looper position: {looper._position}")

    print("\n2. Checking InputNullNode position...")
    input_node = looper._input_node
    assert input_node is not None, "InputNullNode not created"
    print(f"   InputNullNode position: {input_node._position}")

    expected_input_x = 0.0
    expected_input_y = 0.0
    assert input_node._position[0] == expected_input_x, \
        f"InputNullNode x position should be {expected_input_x}, got {input_node._position[0]}"
    assert input_node._position[1] == expected_input_y, \
        f"InputNullNode y position should be {expected_input_y}, got {input_node._position[1]}"
    print(f"   ✓ InputNullNode at expected position [{expected_input_x}, {expected_input_y}]")

    print("\n3. Checking OutputNullNode position...")
    output_node = looper._output_node
    assert output_node is not None, "OutputNullNode not created"
    print(f"   OutputNullNode position: {output_node._position}")

    expected_output_x = 150.0  # 0.0 + 150.0 offset
    expected_output_y = 0.0
    assert output_node._position[0] == expected_output_x, \
        f"OutputNullNode x position should be {expected_output_x}, got {output_node._position[0]}"
    assert output_node._position[1] == expected_output_y, \
        f"OutputNullNode y position should be {expected_output_y}, got {output_node._position[1]}"
    print(f"   ✓ OutputNullNode at expected position [{expected_output_x}, {expected_output_y}]")

    print("\n4. Verifying 150-pixel horizontal offset between nodes...")
    offset_x = output_node._position[0] - input_node._position[0]
    offset_y = output_node._position[1] - input_node._position[1]
    assert offset_x == 150.0, f"Expected x offset of 150.0, got {offset_x}"
    assert offset_y == 0.0, f"Expected y offset of 0.0, got {offset_y}"
    print(f"   ✓ Offset verified: x={offset_x}, y={offset_y}")

    print("\n" + "="*60)
    print("✓ ALL POSITION TESTS PASSED!")
    print("="*60)
    print("\nLooper node internal nodes are properly positioned with 150-pixel offset.")
    print()

    return True

if __name__ == "__main__":
    try:
        test_looper_position_initialization()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
