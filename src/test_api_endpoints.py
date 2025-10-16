"""
TextLoom API Endpoint Testing Script

This script:
1. Creates a test workspace with nodes
2. Starts the API server in a subprocess
3. Tests all read-only endpoints
4. Displays results

Usage:
    python test_api_endpoints.py
"""

import sys
import os
import time
import requests
import json
from typing import Dict, Any

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeEnvironment
from core.global_store import GlobalStore

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"


def setup_test_workspace():
    """Create a simple test workspace with nodes and connections."""
    print("\n" + "="*60)
    print("SETTING UP TEST WORKSPACE")
    print("="*60)
    
    # Clear any existing nodes
    existing_nodes = NodeEnvironment.list_nodes()
    print(f"Clearing {len(existing_nodes)} existing nodes...")
    
    # Create test nodes
    print("\nCreating test nodes...")
    
    # Text node with some content
    text_node = Node.create_node(NodeType.TEXT, node_name="api_test_text")
    text_node._parms["text_string"].set("Hello from TextLoom API!")
    text_node._parms["pass_through"].set(False)
    print(f"  ✓ Created TextNode: {text_node.path()} (session_id: {text_node.session_id()})")
    
    # FileOut node
    fileout_node = Node.create_node(NodeType.FILE_OUT, node_name="api_test_output")
    fileout_node._parms["file_name"].set("./api_test_output.txt")
    print(f"  ✓ Created FileOutNode: {fileout_node.path()} (session_id: {fileout_node.session_id()})")
    
    # Null node (pass-through)
    null_node = Node.create_node(NodeType.NULL, node_name="api_test_null")
    print(f"  ✓ Created NullNode: {null_node.path()} (session_id: {null_node.session_id()})")
    
    # Connect nodes: TextNode -> NullNode -> FileOutNode
    print("\nCreating connections...")
    null_node.set_input(0, text_node)
    print(f"  ✓ Connected {text_node.path()} -> {null_node.path()}")
    
    fileout_node.set_input(0, null_node)
    print(f"  ✓ Connected {null_node.path()} -> {fileout_node.path()}")
    
    # Set some global variables
    print("\nSetting global variables...")
    GlobalStore.set("TEST_VAR", "API Testing")
    GlobalStore.set("VERSION", "1.0.0")
    print(f"  ✓ Set TEST_VAR = 'API Testing'")
    print(f"  ✓ Set VERSION = '1.0.0'")
    
    print("\n✓ Test workspace ready!")
    return {
        'text_node': text_node,
        'fileout_node': fileout_node,
        'null_node': null_node
    }


def test_endpoint(name: str, url: str, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint and return results."""
    print(f"\n{name}")
    print("-" * 60)
    print(f"GET {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✓ Expected status code")
            data = response.json()
            print(f"Response size: {len(json.dumps(data))} bytes")
            return {'success': True, 'data': data, 'status': response.status_code}
        else:
            print(f"✗ Unexpected status code (expected {expected_status})")
            return {'success': False, 'status': response.status_code}
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed - is the server running?")
        return {'success': False, 'error': 'connection_failed'}
    except Exception as e:
        print(f"✗ Error: {e}")
        return {'success': False, 'error': str(e)}


def main():
    """Run all API tests."""
    print("\n" + "="*60)
    print("TEXTLOOM API ENDPOINT TESTING")
    print("="*60)
    
    # Step 1: Setup test workspace
    nodes = setup_test_workspace()
    
    # Step 2: Wait for user to start server
    print("\n" + "="*60)
    print("START THE API SERVER")
    print("="*60)
    print("\nIn another terminal, run:")
    print("  uvicorn api.main:app --reload --port 8000")
    print("\nPress Enter once the server is running...")
    input()
    
    # Give server a moment to fully start
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Step 3: Test endpoints
    print("\n" + "="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    results = []
    
    # Test root endpoint
    result = test_endpoint(
        "1. Root Health Check",
        BASE_URL
    )
    results.append(result)
    if result['success']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test API info
    result = test_endpoint(
        "2. API Info",
        API_BASE
    )
    results.append(result)
    if result['success']:
        print(f"Endpoints: {list(result['data']['endpoints'].keys())}")
    
    # Test workspace endpoint
    result = test_endpoint(
        "3. Get Workspace",
        f"{API_BASE}/workspace"
    )
    results.append(result)
    if result['success']:
        data = result['data']
        print(f"Nodes: {len(data['nodes'])}")
        print(f"Connections: {len(data['connections'])}")
        print(f"Globals: {len(data['globals'])}")
        
        # Show node details
        if data['nodes']:
            print("\nNodes found:")
            for node in data['nodes']:
                print(f"  - {node['name']} ({node['type']}) at {node['path']}")
        
        # Show connections
        if data['connections']:
            print("\nConnections found:")
            for conn in data['connections']:
                print(f"  - {conn['source_node_path']} -> {conn['target_node_path']}")
        
        # Show globals
        if data['globals']:
            print("\nGlobals found:")
            for key, value in data['globals'].items():
                print(f"  - {key} = {value}")
    
    # Test list nodes endpoint
    result = test_endpoint(
        "4. List All Nodes",
        f"{API_BASE}/nodes"
    )
    results.append(result)
    if result['success']:
        nodes_list = result['data']
        print(f"Found {len(nodes_list)} nodes")
        if nodes_list:
            first_node = nodes_list[0]
            print(f"\nFirst node details:")
            print(f"  Session ID: {first_node['session_id']}")
            print(f"  Name: {first_node['name']}")
            print(f"  Type: {first_node['type']}")
            print(f"  Path: {first_node['path']}")
            print(f"  Parameters: {len(first_node['parameters'])}")
    
    # Test get specific node
    if result['success'] and nodes_list:
        session_id = nodes_list[0]['session_id']
        result = test_endpoint(
            f"5. Get Node by Session ID ({session_id})",
            f"{API_BASE}/nodes/{session_id}"
        )
        results.append(result)
        if result['success']:
            node = result['data']
            print(f"\nNode: {node['name']}")
            print(f"Parameters:")
            for pname, pinfo in node['parameters'].items():
                print(f"  - {pname}: {pinfo['value']} ({pinfo['type']})")
    
    # Test 404 error
    result = test_endpoint(
        "6. Test 404 Error (Invalid Session ID)",
        f"{API_BASE}/nodes/999999999",
        expected_status=404
    )
    results.append(result)
    if result['status'] == 404:
        print("✓ Correctly returned 404 for non-existent node")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r.get('success'))
    total = len(results)
    
    print(f"\nTests passed: {successful}/{total}")
    
    if successful == total:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {total - successful} test(s) failed")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. View interactive API docs:")
    print(f"   {BASE_URL}/api/v1/docs")
    print("\n2. Try the ReDoc documentation:")
    print(f"   {BASE_URL}/api/v1/redoc")
    print("\n3. Test with curl:")
    print(f"   curl {API_BASE}/workspace | jq")
    print("\n")


if __name__ == "__main__":
    main()
