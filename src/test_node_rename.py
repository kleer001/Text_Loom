"""
Test script for node renaming functionality.

This script tests the new node rename API endpoint.

Usage:
    1. Start the API server: uvicorn api.main:app --reload --port 8000
    2. Run this script: python test_node_rename.py
"""

import sys
import os
import requests
import json

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"


def clear_workspace():
    """Clear all existing nodes."""
    print("\nClearing workspace...")
    existing_nodes = NodeEnvironment.list_nodes()
    for path in existing_nodes:
        node = NodeEnvironment.node_from_name(path)
        if node:
            node.destroy()
    print("✓ Workspace cleared\n")


def test_node_rename():
    """Test node renaming through the API."""
    print("="*60)
    print("TESTING NODE RENAME FUNCTIONALITY")
    print("="*60)

    # Clear workspace
    clear_workspace()

    # Step 1: Create a test node
    print("\n1. Creating a test node...")
    create_data = {
        "type": "text",
        "name": "original_name",
        "position": [100.0, 200.0]
    }

    response = requests.post(f"{API_BASE}/nodes", json=create_data)
    if response.status_code != 201:
        print(f"✗ Failed to create node: {response.status_code}")
        print(response.json())
        return False

    node_data = response.json()
    session_id = node_data['session_id']
    print(f"✓ Created node with session_id: {session_id}")
    print(f"  Name: {node_data['name']}")
    print(f"  Path: {node_data['path']}")

    # Step 2: Rename the node
    print("\n2. Renaming node to 'new_name'...")
    update_data = {
        "name": "new_name"
    }

    response = requests.put(f"{API_BASE}/nodes/{session_id}", json=update_data)
    if response.status_code != 200:
        print(f"✗ Failed to rename node: {response.status_code}")
        print(response.json())
        return False

    node_data = response.json()
    print(f"✓ Successfully renamed node")
    print(f"  New name: {node_data['name']}")
    print(f"  New path: {node_data['path']}")

    # Step 3: Verify the name was updated
    if node_data['name'] != 'new_name':
        print(f"✗ Name was not updated correctly: {node_data['name']}")
        return False

    if node_data['path'] != '/new_name':
        print(f"✗ Path was not updated correctly: {node_data['path']}")
        return False

    print("✓ Name and path updated correctly")

    # Step 4: Try to rename with invalid name (should fail)
    print("\n3. Testing invalid name (should fail)...")
    update_data = {
        "name": "invalid-name-with-dashes"
    }

    response = requests.put(f"{API_BASE}/nodes/{session_id}", json=update_data)
    if response.status_code == 400:
        print("✓ Invalid name rejected as expected")
        print(f"  Error: {response.json()['detail']['message']}")
    else:
        print(f"✗ Expected 400 error, got {response.status_code}")
        return False

    # Step 5: Create another node and try to rename to an existing name (should fail)
    print("\n4. Testing duplicate name (should fail)...")
    create_data = {
        "type": "text",
        "name": "another_node",
        "position": [200.0, 300.0]
    }

    response = requests.post(f"{API_BASE}/nodes", json=create_data)
    if response.status_code != 201:
        print(f"✗ Failed to create second node: {response.status_code}")
        return False

    second_node = response.json()
    second_session_id = second_node['session_id']
    print(f"✓ Created second node: {second_node['name']}")

    # Try to rename second node to same name as first node
    update_data = {
        "name": "new_name"  # Already used by first node
    }

    response = requests.put(f"{API_BASE}/nodes/{second_session_id}", json=update_data)
    if response.status_code == 400:
        print("✓ Duplicate name rejected as expected")
        print(f"  Error: {response.json()['detail']['message']}")
    else:
        print(f"✗ Expected 400 error, got {response.status_code}")
        return False

    # Step 6: Test renaming with valid special characters (underscores and numbers)
    print("\n5. Testing valid name with underscores and numbers...")
    update_data = {
        "name": "my_node_123"
    }

    response = requests.put(f"{API_BASE}/nodes/{second_session_id}", json=update_data)
    if response.status_code != 200:
        print(f"✗ Failed to rename node: {response.status_code}")
        print(response.json())
        return False

    node_data = response.json()
    print(f"✓ Successfully renamed to: {node_data['name']}")

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)

    # Cleanup
    clear_workspace()

    return True


if __name__ == "__main__":
    try:
        success = test_node_rename()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection failed - is the API server running?")
        print("  Start it with: uvicorn api.main:app --reload --port 8000")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
