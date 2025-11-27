"""
TextLoom API - Focused Test for Failing Endpoints

This script tests ONLY the two failing endpoints:
1. Create TextNode
2. Create FileOutNode

Usage:
    1. Start the API server in another terminal:
       uvicorn api.main:app --reload --port 8000
    
    2. Run this test:
       python test_failing_endpoints.py
"""

import sys
import os
import time
import requests
import json
import logging
from typing import Dict, Any

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


from core.base_classes import NodeEnvironment

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_workspace():
    """Clear all existing nodes."""
    logger.info("Clearing workspace...")
    existing_nodes = NodeEnvironment.list_nodes()
    logger.info(f"Found {len(existing_nodes)} existing nodes")
    
    for path in existing_nodes:
        node = NodeEnvironment.node_from_name(path)
        if node:
            node.destroy()
    
    logger.info("Workspace cleared")


def check_create_node(node_type: str, node_name: str, position: list) -> Dict[str, Any]:
    """
    Test creating a single node.

    Args:
        node_type: Type of node to create (e.g., "text", "file_out")
        node_name: Name for the node
        position: [x, y] position

    Returns:
        Dictionary with test results
    """
    print("\n" + "="*60)
    print(f"TEST: Create {node_type.upper()} Node")
    print("="*60)
    
    url = f"{API_BASE}/nodes"
    data = {
        "type": node_type,
        "name": node_name,
        "position": position
    }
    
    logger.info(f"Sending POST request to {url}")
    logger.debug(f"Request data: {json.dumps(data, indent=2)}")
    
    print(f"\nRequest:")
    print(f"  POST {url}")
    print(f"  Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        logger.info(f"Response status: {response.status_code}")
        
        print(f"\nResponse:")
        print(f"  Status: {response.status_code}")
        
        # Parse response
        try:
            response_data = response.json()
            print(f"  Body: {json.dumps(response_data, indent=2)}")
            logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
        except Exception as e:
            logger.error(f"Failed to parse response JSON: {e}")
            print(f"  Body: {response.text}")
            response_data = {"error": "failed_to_parse", "raw": response.text}
        
        # Check status
        if response.status_code == 201:
            print(f"\n✓ SUCCESS - Node created")
            if 'session_id' in response_data:
                print(f"  Session ID: {response_data['session_id']}")
            if 'path' in response_data:
                print(f"  Path: {response_data['path']}")
            if 'name' in response_data:
                print(f"  Name: {response_data['name']}")
            
            return {
                'success': True,
                'node_type': node_type,
                'status': response.status_code,
                'data': response_data
            }
        else:
            print(f"\n✗ FAILED - Unexpected status code")
            print(f"  Expected: 201")
            print(f"  Got: {response.status_code}")
            
            if 'detail' in response_data:
                print(f"\n  Error Details:")
                detail = response_data['detail']
                if isinstance(detail, dict):
                    for key, value in detail.items():
                        print(f"    {key}: {value}")
                else:
                    print(f"    {detail}")
            
            return {
                'success': False,
                'node_type': node_type,
                'status': response.status_code,
                'error': response_data
            }
            
    except requests.exceptions.ConnectionError:
        logger.error("Connection failed - server not running?")
        print(f"\n✗ FAILED - Connection Error")
        print("  Is the API server running?")
        print("  Start it with: uvicorn api.main:app --reload --port 8000")
        
        return {
            'success': False,
            'node_type': node_type,
            'error': 'connection_failed'
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        print(f"\n✗ FAILED - Exception")
        print(f"  {type(e).__name__}: {e}")
        
        return {
            'success': False,
            'node_type': node_type,
            'error': str(e)
        }


def verify_server_running():
    """Check if the API server is accessible."""
    logger.info("Checking if server is running...")
    print("\n" + "="*60)
    print("SERVER CHECK")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✓ API server is running")
            logger.info("Server is accessible")
            return True
        else:
            print(f"✗ Server responded with status {response.status_code}")
            logger.warning(f"Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server")
        print("\nPlease start the server in another terminal:")
        print("  uvicorn api.main:app --reload --port 8000")
        logger.error("Server not accessible")
        return False
    except Exception as e:
        print(f"✗ Error checking server: {e}")
        logger.error(f"Error checking server: {e}")
        return False


def main():
    """Run the focused tests on the two failing endpoints."""
    print("\n" + "="*60)
    print("TEXTLOOM API - FOCUSED TEST (FAILING ENDPOINTS ONLY)")
    print("="*60)
    print("\nThis test focuses on the two failing node creation endpoints:")
    print("  1. Create TextNode")
    print("  2. Create FileOutNode")
    
    # Clear workspace first
    clear_workspace()
    
    # Check server
    if not verify_server_running():
        print("\n" + "="*60)
        print("TEST ABORTED - Server not running")
        print("="*60)
        return
    
    # Small delay to ensure server is ready
    time.sleep(1)
    
    # Store results
    results = []
    
    # ========================================
    # TEST 1: Create TextNode
    # ========================================
    result1 = check_create_node(
        node_type="text",
        node_name="test_text",
        position=[100.0, 100.0]
    )
    results.append(result1)

    # Small delay between tests
    time.sleep(0.5)

    # ========================================
    # TEST 2: Create FileOutNode
    # ========================================
    result2 = check_create_node(
        node_type="file_out",
        node_name="test_fileout",
        position=[300.0, 100.0]
    )
    results.append(result2)
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests PASSED!")
        logger.info("All tests passed")
    else:
        print(f"\n✗ {total - passed} test(s) FAILED")
        logger.warning(f"{total - passed} tests failed")
        
        print("\nFailed tests:")
        for i, result in enumerate(results, 1):
            if not result['success']:
                print(f"  {i}. Create {result['node_type']} node")
                if 'error' in result:
                    if isinstance(result['error'], dict):
                        if 'detail' in result['error']:
                            detail = result['error']['detail']
                            if isinstance(detail, dict) and 'message' in detail:
                                print(f"     Error: {detail['message']}")
                    else:
                        print(f"     Error: {result['error']}")
    
    print("\n" + "="*60)
    print("DEBUGGING INFORMATION")
    print("="*60)
    print("\nIf tests are failing:")
    print("1. Check the API server console for detailed logs")
    print("2. Look for DEBUG messages showing where the failure occurs")
    print("3. The patch.py file contains enhanced logging - ensure it's applied")
    print("4. Check that nodes are being created in the backend:")
    
    # Check if any nodes were actually created in the backend
    backend_nodes = NodeEnvironment.list_nodes()
    print(f"\nBackend nodes after tests: {len(backend_nodes)}")
    if backend_nodes:
        print("  Created nodes:")
        for path in backend_nodes:
            node = NodeEnvironment.node_from_name(path)
            if node:
                print(f"    - {path} (session_id: {node.session_id()}, type: {node.type()})")
    else:
        print("  No nodes created in backend")
    
    print("\n" + "="*60)
    

if __name__ == "__main__":
    main()