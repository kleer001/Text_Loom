#!/usr/bin/env python3
"""
Test to verify that node positions are correctly saved and restored.
This test addresses the bug where positions weren't being persisted.
"""
import sys
import os
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(parent_dir, 'src'))

from core.base_classes import NodeEnvironment, Node, NodeType
from core.flowstate_manager import save_flowstate, load_flowstate


def test_position_persistence():
    print("=" * 60)
    print("Testing Node Position Persistence")
    print("=" * 60)

    env = NodeEnvironment.get_instance()
    env.nodes.clear()

    print("\n1. Creating nodes with specific positions...")
    text1 = Node.create_node(NodeType.TEXT, node_name="text1")
    text2 = Node.create_node(NodeType.TEXT, node_name="text2")
    text3 = Node.create_node(NodeType.TEXT, node_name="text3")

    position1 = [100.0, 200.0]
    position2 = [300.0, 400.0]
    position3 = [500.0, 600.0]

    text1._position = tuple(position1)
    text2._position = tuple(position2)
    text3._position = tuple(position3)

    color1 = (1.0, 0.0, 0.0)
    color2 = (0.0, 1.0, 0.0)
    color3 = (0.0, 0.0, 1.0)

    text1._color = color1
    text2._color = color2
    text3._color = color3

    text1._selected = True
    text2._selected = False
    text3._selected = True

    print(f"   text1 position: {text1._position}, color: {text1._color}, selected: {text1._selected}")
    print(f"   text2 position: {text2._position}, color: {text2._color}, selected: {text2._selected}")
    print(f"   text3 position: {text3._position}, color: {text3._color}, selected: {text3._selected}")

    test_file = os.path.join(parent_dir, "test_positions.json")

    print(f"\n2. Saving flowstate to {test_file}...")
    result = save_flowstate(test_file)
    assert result, "Failed to save flowstate"
    print("   ✓ Save successful")

    print("\n3. Verifying saved data contains position information...")
    with open(test_file, 'r') as f:
        import json
        data = json.load(f)
        text1_data = data["nodes"]["/text1"]

        assert "_position" in text1_data, "Position not saved in file!"
        assert "_color" in text1_data, "Color not saved in file!"
        assert "_selected" in text1_data, "Selected not saved in file!"

        saved_position = text1_data["_position"]
        saved_color = text1_data["_color"]
        saved_selected = text1_data["_selected"]

        print(f"   ✓ Found _position in save data: {saved_position}")
        print(f"   ✓ Found _color in save data: {saved_color}")
        print(f"   ✓ Found _selected in save data: {saved_selected}")

        assert saved_position == position1, f"Position mismatch: {saved_position} != {position1}"
        assert saved_color == list(color1), f"Color mismatch: {saved_color} != {list(color1)}"
        assert saved_selected == True, f"Selected mismatch: {saved_selected} != True"

    print("\n4. Clearing environment...")
    env.nodes.clear()
    assert len(env.nodes) == 0, "Environment not cleared"
    print("   ✓ Environment cleared")

    print("\n5. Loading flowstate...")
    result = load_flowstate(test_file)
    assert result, "Failed to load flowstate"
    print("   ✓ Load successful")

    print("\n6. Verifying positions were restored...")
    text1_loaded = NodeEnvironment.node_from_name("/text1")
    text2_loaded = NodeEnvironment.node_from_name("/text2")
    text3_loaded = NodeEnvironment.node_from_name("/text3")

    assert text1_loaded is not None, "text1 not loaded"
    assert text2_loaded is not None, "text2 not loaded"
    assert text3_loaded is not None, "text3 not loaded"

    print(f"   text1 position: {text1_loaded._position}, color: {text1_loaded._color}, selected: {text1_loaded._selected}")
    print(f"   text2 position: {text2_loaded._position}, color: {text2_loaded._color}, selected: {text2_loaded._selected}")
    print(f"   text3 position: {text3_loaded._position}, color: {text3_loaded._color}, selected: {text3_loaded._selected}")

    assert text1_loaded._position == tuple(position1), f"text1 position not restored: {text1_loaded._position} != {tuple(position1)}"
    assert text2_loaded._position == tuple(position2), f"text2 position not restored: {text2_loaded._position} != {tuple(position2)}"
    assert text3_loaded._position == tuple(position3), f"text3 position not restored: {text3_loaded._position} != {tuple(position3)}"

    assert text1_loaded._color == color1, f"text1 color not restored: {text1_loaded._color} != {color1}"
    assert text2_loaded._color == color2, f"text2 color not restored: {text2_loaded._color} != {color2}"
    assert text3_loaded._color == color3, f"text3 color not restored: {text3_loaded._color} != {color3}"

    assert text1_loaded._selected == True, f"text1 selected not restored: {text1_loaded._selected} != True"
    assert text2_loaded._selected == False, f"text2 selected not restored: {text2_loaded._selected} != False"
    assert text3_loaded._selected == True, f"text3 selected not restored: {text3_loaded._selected} != True"

    print("   ✓ All positions restored correctly!")
    print("   ✓ All colors restored correctly!")
    print("   ✓ All selected states restored correctly!")

    print("\n7. Cleaning up test file...")
    if os.path.exists(test_file):
        os.remove(test_file)
    print("   ✓ Test file removed")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Position persistence is working!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_position_persistence()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
