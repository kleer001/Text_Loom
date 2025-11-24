"""
Test the core node rename functionality directly (without API).

This tests the rename() method on Node instances.
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeEnvironment


def test_node_rename_core():
    """Test node renaming at the core level."""
    print("="*60)
    print("TESTING CORE NODE RENAME FUNCTIONALITY")
    print("="*60)

    # Clear workspace
    print("\nClearing workspace...")
    existing_nodes = NodeEnvironment.list_nodes()
    for path in existing_nodes:
        node = NodeEnvironment.node_from_name(path)
        if node:
            node.destroy()
    print("✓ Workspace cleared")

    # Test 1: Create a node and rename it
    print("\n1. Creating a text node...")
    node1 = Node.create_node(NodeType.TEXT, "original_name")
    print(f"✓ Created node: {node1.name()} at {node1.path()}")

    print("\n2. Renaming node to 'new_name'...")
    success = node1.rename("new_name")
    if not success:
        print("✗ Rename failed")
        return False

    print(f"✓ Renamed successfully")
    print(f"  New name: {node1.name()}")
    print(f"  New path: {node1.path()}")

    if node1.name() != "new_name":
        print(f"✗ Name not updated correctly: {node1.name()}")
        return False

    if node1.path() != "/new_name":
        print(f"✗ Path not updated correctly: {node1.path()}")
        return False

    # Verify in NodeEnvironment
    retrieved = NodeEnvironment.node_from_name("/new_name")
    if retrieved is None:
        print("✗ Node not found in NodeEnvironment with new path")
        return False

    if retrieved is not node1:
        print("✗ Retrieved node is not the same object")
        return False

    print("✓ Node correctly registered in NodeEnvironment")

    # Test 2: Try to rename to an existing name (should fail)
    print("\n3. Creating second node...")
    node2 = Node.create_node(NodeType.TEXT, "another_node")
    print(f"✓ Created second node: {node2.name()}")

    print("\n4. Trying to rename second node to existing name (should fail)...")
    success = node2.rename("new_name")
    if success:
        print("✗ Rename should have failed but succeeded")
        return False

    print("✓ Rename correctly rejected")
    print(f"  Node name unchanged: {node2.name()}")

    # Test 3: Test sanitization by the API (simulate what the API does)
    print("\n5. Testing name sanitization...")
    sanitized = Node.sanitize_node_name("my_node_123")
    print(f"  'my_node_123' -> '{sanitized}'")
    if sanitized != "my_node_123":
        print("✗ Valid name was incorrectly sanitized")
        return False

    sanitized = Node.sanitize_node_name("invalid-name-with-dashes")
    print(f"  'invalid-name-with-dashes' -> '{sanitized}'")
    if sanitized != "invalidnamewithdashes":
        print(f"✗ Expected 'invalidnamewithdashes', got '{sanitized}'")
        return False

    print("✓ Sanitization works correctly")

    # Test 4: Rename with sanitized name
    print("\n6. Renaming with underscores and numbers...")
    success = node2.rename("test_node_456")
    if not success:
        print("✗ Rename failed")
        return False

    print(f"✓ Renamed to: {node2.name()}")

    print("\n" + "="*60)
    print("ALL CORE TESTS PASSED!")
    print("="*60)

    # Cleanup
    print("\nCleaning up...")
    node1.destroy()
    node2.destroy()
    print("✓ Cleanup complete")

    return True


if __name__ == "__main__":
    try:
        success = test_node_rename_core()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
