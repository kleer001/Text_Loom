"""
TextLoom API Write Endpoints Testing Script

This script tests all write endpoints:
- Creating nodes
- Updating nodes
- Deleting nodes
- Creating connections
- Deleting connections
- Executing nodes
- Managing global variables

Usage:
    python test_api_write_endpoints.py
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

from core.base_classes import NodeEnvironment

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"


def clear_workspace():
    """Clear all existing nodes."""
    print("\n" + "="*60)
    print("CLEARING WORKSPACE")
    print("="*60)
    
    existing_nodes = NodeEnvironment.list_nodes()
    print(f"Clearing {len(existing_nodes)} existing nodes...")
    for path in existing_nodes:
        node = NodeEnvironment.node_from_name(path)
        if node:
            node.destroy()
    print("✓ Workspace cleared")


def test_request(name: str, method: str, url: str, data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint and return results."""
    print(f"\n{name}")
    print("-" * 60)
    print(f"{method} {url}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, json=data, timeout=5)
        else:
            print(f"✗ Unknown method: {method}")
            return {'success': False, 'error': 'unknown_method'}
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"✓ Expected status code")
            result_data = response.json()
            return {'success': True, 'data': result_data, 'status': response.status_code}
        else:
            print(f"✗ Unexpected status code (expected {expected_status})")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
                return {'success': False, 'status': response.status_code, 'error': error_data}
            except:
                return {'success': False, 'status': response.status_code}
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed - is the server running?")
        return {'success': False, 'error': 'connection_failed'}
    except Exception as e:
        print(f"✗ Error: {e}")
        return {'success': False, 'error': str(e)}


def main():
    """Run all write endpoint tests."""
    print("\n" + "="*60)
    print("TEXTLOOM API WRITE ENDPOINTS TESTING")
    print("="*60)
    
    # Clear workspace first
    clear_workspace()
    
    # Wait for user to start server
    print("\n" + "="*60)
    print("START THE API SERVER")
    print("="*60)
    print("\nIn another terminal, run:")
    print("  uvicorn api.main:app --reload --port 8000")
    print("\nPress Enter once the server is running...")
    input()
    
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test tracking
    results = []
    test_nodes = {}  # Store created node info
    
    print("\n" + "="*60)
    print("TESTING WRITE ENDPOINTS")
    print("="*60)
    
    # ========================================
    # TEST 1: Create TextNode
    # ========================================
    result = test_request(
        "1. Create TextNode",
        "POST",
        f"{API_BASE}/nodes",
        {
            "type": "text",
            "name": "test_text",
            "position": [100.0, 100.0]
        },
        expected_status=201
    )
    results.append(result)
    if result['success']:
        test_nodes['text'] = result['data']
        print(f"✓ Created node: {result['data']['name']} (session_id: {result['data']['session_id']})")
    
    # ========================================
    # TEST 2: Create FileOutNode
    # ========================================
    result = test_request(
        "2. Create FileOutNode",
        "POST",
        f"{API_BASE}/nodes",
        {
            "type": "file_out",  # Use underscore!
            "name": "test_fileout",
            "position": [300.0, 100.0]
        },
        expected_status=201
    )
    results.append(result)
    if result['success']:
        test_nodes['fileout'] = result['data']
        print(f"✓ Created node: {result['data']['name']} (session_id: {result['data']['session_id']})")
    
    # ========================================
    # TEST 3: Update TextNode parameters
    # ========================================
    if 'text' in test_nodes:
        result = test_request(
            "3. Update TextNode Parameters",
            "PUT",
            f"{API_BASE}/nodes/{test_nodes['text']['session_id']}",
            {
                "parameters": {
                    "text_string": "Hello from API!",
                    "pass_through": False
                }
            }
        )
        results.append(result)
        if result['success']:
            print(f"✓ Updated text_string parameter")
            print(f"  New value: {result['data']['parameters']['text_string']['value']}")
    
    # ========================================
    # TEST 4: Update FileOutNode filename
    # ========================================
    if 'fileout' in test_nodes:
        result = test_request(
            "4. Update FileOutNode Filename",
            "PUT",
            f"{API_BASE}/nodes/{test_nodes['fileout']['session_id']}",
            {
                "parameters": {
                    "file_name": "./api_test_output.txt"
                }
            }
        )
        results.append(result)
        if result['success']:
            print(f"✓ Updated file_name parameter")
    
    # ========================================
    # TEST 5: Create connection
    # ========================================
    if 'text' in test_nodes and 'fileout' in test_nodes:
        result = test_request(
            "5. Create Connection (Text → FileOut)",
            "POST",
            f"{API_BASE}/connections",
            {
                "source_node_path": test_nodes['text']['path'],
                "source_output_index": 0,
                "target_node_path": test_nodes['fileout']['path'],
                "target_input_index": 0
            },
            expected_status=201
        )
        results.append(result)
        if result['success']:
            print(f"✓ Connected {result['data']['source_node_path']} → {result['data']['target_node_path']}")
    
    # ========================================
    # TEST 6: Execute FileOutNode
    # ========================================
    if 'fileout' in test_nodes:
        result = test_request(
            "6. Execute FileOutNode",
            "POST",
            f"{API_BASE}/nodes/{test_nodes['fileout']['session_id']}/execute",
            None
        )
        results.append(result)
        if result['success']:
            print(f"✓ Execution completed")
            print(f"  Success: {result['data']['success']}")
            print(f"  Time: {result['data']['execution_time']:.2f}ms")
            print(f"  State: {result['data']['node_state']}")
            if result['data']['errors']:
                print(f"  Errors: {result['data']['errors']}")
            
            # Check if file was created
            if os.path.exists("./api_test_output.txt"):
                with open("./api_test_output.txt", "r") as f:
                    content = f.read()
                print(f"  File created with content: {content}")
    
    # ========================================
    # TEST 7: Set global variable
    # ========================================
    result = test_request(
        "7. Set Global Variable",
        "PUT",
        f"{API_BASE}/globals/TESTVAR",
        {"value": "API Test Value"}
    )
    results.append(result)
    if result['success']:
        print(f"✓ Set TESTVAR = '{result['data']['value']}'")
    
    # ========================================
    # TEST 8: Get global variable
    # ========================================
    result = test_request(
        "8. Get Global Variable",
        "GET",
        f"{API_BASE}/globals/TESTVAR",
        None
    )
    results.append(result)
    if result['success']:
        print(f"✓ Retrieved TESTVAR = '{result['data']['value']}'")
    
    # ========================================
    # TEST 9: List all globals
    # ========================================
    result = test_request(
        "9. List All Globals",
        "GET",
        f"{API_BASE}/globals",
        None
    )
    results.append(result)
    if result['success']:
        print(f"✓ Found {len(result['data']['globals'])} global(s)")
        for key, value in result['data']['globals'].items():
            print(f"    {key} = {value}")
    
    # ========================================
    # TEST 10: Update node UI state
    # ========================================
    if 'text' in test_nodes:
        result = test_request(
            "10. Update Node UI State",
            "PUT",
            f"{API_BASE}/nodes/{test_nodes['text']['session_id']}",
            {
                "position": [150.0, 200.0],
                "selected": True
            }
        )
        results.append(result)
        if result['success']:
            print(f"✓ Updated position to {result['data']['position']}")
            print(f"✓ Set selected = {result['data']['selected']}")
    
    # ========================================
    # TEST 11: Delete connection
    # ========================================
    if 'text' in test_nodes and 'fileout' in test_nodes:
        result = test_request(
            "11. Delete Connection",
            "DELETE",
            f"{API_BASE}/connections",
            {
                "source_node_path": test_nodes['text']['path'],
                "source_output_index": 0,
                "target_node_path": test_nodes['fileout']['path'],
                "target_input_index": 0
            }
        )
        results.append(result)
        if result['success']:
            print(f"✓ Connection deleted")
    
    # ========================================
    # TEST 12: Delete global variable
    # ========================================
    result = test_request(
        "12. Delete Global Variable",
        "DELETE",
        f"{API_BASE}/globals/TESTVAR",
        None
    )
    results.append(result)
    if result['success']:
        print(f"✓ Deleted TESTVAR")
    
    # ========================================
    # TEST 13: Delete nodes
    # ========================================
    if 'text' in test_nodes:
        result = test_request(
            "13. Delete TextNode",
            "DELETE",
            f"{API_BASE}/nodes/{test_nodes['text']['session_id']}",
            None
        )
        results.append(result)
        if result['success']:
            print(f"✓ Deleted text node")
    
    if 'fileout' in test_nodes:
        result = test_request(
            "14. Delete FileOutNode",
            "DELETE",
            f"{API_BASE}/nodes/{test_nodes['fileout']['session_id']}",
            None
        )
        results.append(result)
        if result['success']:
            print(f"✓ Deleted fileout node")
    
    # ========================================
    # TEST 15: Verify workspace is empty
    # ========================================
    result = test_request(
        "15. Verify Empty Workspace",
        "GET",
        f"{API_BASE}/workspace",
        None
    )
    results.append(result)
    if result['success']:
        node_count = len(result['data']['nodes'])
        conn_count = len(result['data']['connections'])
        print(f"✓ Workspace has {node_count} nodes, {conn_count} connections")
    
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
        print("\nFailed tests:")
        for i, r in enumerate(results):
            if not r.get('success'):
                print(f"  - Test {i+1}")
    
    # Cleanup
    if os.path.exists("./api_test_output.txt"):
        os.remove("./api_test_output.txt")
        print("\n✓ Cleaned up test file")
    
    print("\n" + "="*60)
    print("COMPLETE API DOCUMENTATION")
    print("="*60)
    print(f"\nView interactive docs: {BASE_URL}/api/v1/docs")
    print(f"View ReDoc: {BASE_URL}/api/v1/redoc")
    print("\n")


if __name__ == "__main__":
    main()