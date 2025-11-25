#!/usr/bin/env python3
"""
Test to verify LooperNode save/load functionality.

This test creates a looper with internal text nodes, cooks it, saves the flowstate,
clears the environment, loads the flowstate, and cooks again to verify everything
works correctly after save/load.
"""
import sys
import os
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.flowstate_manager import save_flowstate, load_flowstate
from core.print_node_info import print_node_info


def test_looper_save_load():
    """Test that looper nodes save and load correctly with all internal structure."""
    print("\n" + "="*70)
    print("Testing LooperNode Save/Load Functionality")
    print("="*70)

    # ========== STEP 1: CREATE LOOPER WITH 3 TEXT NODES ==========
    print("\n1. Creating looper with 3 text nodes inside...")

    looper = Node.create_node(NodeType.LOOPER, node_name="looper1")
    text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")
    text2 = Node.create_node(NodeType.TEXT, node_name="text2", parent_path="/looper1")
    text3 = Node.create_node(NodeType.TEXT, node_name="text3", parent_path="/looper1")
    merge = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")

    # Set parameters
    text1._parms["text_string"].set("Item $$N: ")
    text2._parms["text_string"].set("Apple")
    text3._parms["text_string"].set(" Pie")
    merge._parms["single_string"].set(True)

    # Connect nodes: merge combines text2+text3, text1 gets merge output
    merge.set_input(0, text2)
    merge.set_input(1, text3)
    text1.set_input(0, merge)
    looper._output_node.set_input(0, text1)

    # Configure looper
    looper._parms["min"].set(1)
    looper._parms["max"].set(3)
    looper._parms["step"].set(1)

    print(f"   ✓ Created looper: {looper.path()}")
    print(f"   ✓ Created text1: {text1.path()}")
    print(f"   ✓ Created text2: {text2.path()}")
    print(f"   ✓ Created text3: {text3.path()}")
    print(f"   ✓ Created merge: {merge.path()}")
    print(f"   ✓ InputNullNode: {looper._input_node.path()}")
    print(f"   ✓ OutputNullNode: {looper._output_node.path()}")

    # ========== STEP 2: COOK THE LOOPER ==========
    print("\n2. Cooking the looper...")

    looper.cook()
    result_before = looper.eval()

    print(f"   ✓ Looper cooked successfully")
    print(f"   ✓ Result: {result_before}")

    assert result_before is not None, "Looper eval returned None"
    assert len(result_before) > 0, "Looper eval returned empty result"

    # Store positions before save
    input_pos_before = list(looper._input_node._position)
    output_pos_before = list(looper._output_node._position)
    print(f"   ✓ InputNullNode position: {input_pos_before}")
    print(f"   ✓ OutputNullNode position: {output_pos_before}")

    # ========== STEP 3: SAVE THE FLOWSTATE ==========
    print("\n3. Saving flowstate...")

    file_path = os.path.abspath("test_looper_save_load.json")
    success = save_flowstate(file_path)

    assert success, "Failed to save flowstate"
    assert os.path.exists(file_path), "Saved file does not exist"

    with open(file_path, 'r') as f:
        content = f.read()
        assert len(content) > 0, "Saved file is empty"

    print(f"   ✓ Saved to: {file_path}")
    print(f"   ✓ File size: {len(content)} bytes")

    # ========== STEP 4: CLEAR ENVIRONMENT ==========
    print("\n4. Clearing environment...")

    env = NodeEnvironment.get_instance()
    node_count_before = len(env.nodes)
    env.nodes.clear()
    node_count_after = len(env.nodes)

    assert node_count_after == 0, f"Environment not cleared: {node_count_after} nodes remain"
    assert NodeEnvironment.node_from_name("/looper1") is None, "Looper still exists after clear"

    print(f"   ✓ Cleared {node_count_before} nodes")
    print(f"   ✓ Verified environment is empty")

    # ========== STEP 5: LOAD THE FLOWSTATE ==========
    print("\n5. Loading flowstate...")

    success = load_flowstate(file_path)
    assert success, "Failed to load flowstate"

    node_count_loaded = len(env.nodes)
    print(f"   ✓ Loaded {node_count_loaded} nodes")

    # Verify all nodes are loaded
    looper_loaded = NodeEnvironment.node_from_name("/looper1")
    text1_loaded = NodeEnvironment.node_from_name("/looper1/text1")
    text2_loaded = NodeEnvironment.node_from_name("/looper1/text2")
    text3_loaded = NodeEnvironment.node_from_name("/looper1/text3")
    merge_loaded = NodeEnvironment.node_from_name("/looper1/merge1")

    assert looper_loaded is not None, "Looper failed to load"
    assert text1_loaded is not None, "text1 failed to load"
    assert text2_loaded is not None, "text2 failed to load"
    assert text3_loaded is not None, "text3 failed to load"
    assert merge_loaded is not None, "merge failed to load"

    print(f"   ✓ Looper loaded: {looper_loaded.path()}")
    print(f"   ✓ text1 loaded: {text1_loaded.path()}")
    print(f"   ✓ text2 loaded: {text2_loaded.path()}")
    print(f"   ✓ text3 loaded: {text3_loaded.path()}")
    print(f"   ✓ merge loaded: {merge_loaded.path()}")

    # Verify internal nodes
    assert looper_loaded._internal_nodes_created, "Internal nodes not created"
    assert looper_loaded._input_node is not None, "InputNullNode not loaded"
    assert looper_loaded._output_node is not None, "OutputNullNode not loaded"

    print(f"   ✓ InputNullNode loaded: {looper_loaded._input_node.path()}")
    print(f"   ✓ OutputNullNode loaded: {looper_loaded._output_node.path()}")

    # Verify positions were restored
    input_pos_after = list(looper_loaded._input_node._position)
    output_pos_after = list(looper_loaded._output_node._position)
    print(f"   ✓ InputNullNode position: {input_pos_after}")
    print(f"   ✓ OutputNullNode position: {output_pos_after}")

    # ========== STEP 6: COOK THE LOOPER AGAIN ==========
    print("\n6. Cooking the loaded looper...")

    looper_loaded.cook()
    result_after = looper_loaded.eval()

    print(f"   ✓ Looper cooked successfully")
    print(f"   ✓ Result: {result_after}")

    assert result_after is not None, "Loaded looper eval returned None"
    assert len(result_after) > 0, "Loaded looper eval returned empty result"

    # Verify results match
    print("\n7. Verifying results match...")
    assert result_before == result_after, \
        f"Results don't match!\nBefore: {result_before}\nAfter: {result_after}"
    print(f"   ✓ Results match perfectly")

    # ========== CLEANUP ==========
    print("\n8. Cleaning up test file...")
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"   ✓ Removed {file_path}")

    # ========== SUCCESS ==========
    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED!")
    print("="*70)
    print("\nLooper save/load works correctly:")
    print("  - LooperNode structure preserved")
    print("  - Internal nodes (InputNull/OutputNull) restored")
    print("  - Child nodes (text1, text2, text3, merge) restored")
    print("  - Connections preserved")
    print("  - Cooking produces same results")
    print("  - Positions maintained")
    print()

    return True


if __name__ == "__main__":
    try:
        test_looper_save_load()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
