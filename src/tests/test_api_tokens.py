"""
TextLoom API Token Endpoints Testing Script

This script tests the token tracking API endpoints:
1. Creates a test workspace with QueryNode
2. Starts the API server
3. Executes LLM queries to generate token usage
4. Tests all token-related endpoints

Usage:
    python test_api_tokens.py
"""

import sys
import os
import time
import requests
import json
from typing import Dict, Any

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeEnvironment
from core.token_manager import get_token_manager
from core.models import TokenUsage

API_BASE = "http://127.0.0.1:8000/api/v1"


def setup_test_data():
    """Populate token manager with test data."""
    print("\n" + "="*60)
    print("SETTING UP TEST TOKEN DATA")
    print("="*60)

    token_manager = get_token_manager()
    token_manager.reset()

    print("\nAdding simulated token usage...")

    token_manager.add_usage("query_node_1", TokenUsage(
        input_tokens=25,
        output_tokens=75,
        total_tokens=100
    ))
    print("  ✓ Added usage for query_node_1: 25 in, 75 out, 100 total")

    token_manager.add_usage("query_node_1", TokenUsage(
        input_tokens=30,
        output_tokens=90,
        total_tokens=120
    ))
    print("  ✓ Added usage for query_node_1: 30 in, 90 out, 120 total")

    token_manager.add_usage("query_node_2", TokenUsage(
        input_tokens=50,
        output_tokens=150,
        total_tokens=200
    ))
    print("  ✓ Added usage for query_node_2: 50 in, 150 out, 200 total")

    totals = token_manager.get_totals()
    print(f"\n✓ Total tokens in manager: {totals['total_tokens']}")
    print("✓ Test data ready!")


def test_get_totals():
    """Test GET /api/v1/tokens/totals"""
    print("\n" + "="*60)
    print("TEST: GET /tokens/totals")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE}/tokens/totals")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n📊 Session Totals:")
            print(f"  Input Tokens:  {data['input_tokens']}")
            print(f"  Output Tokens: {data['output_tokens']}")
            print(f"  Total Tokens:  {data['total_tokens']}")

            if data['total_tokens'] == 420:
                print("\n✅ PASS: Correct total (25+30+50 in, 75+90+150 out = 420)")
                return True
            else:
                print(f"\n❌ FAIL: Expected 420 total tokens, got {data['total_tokens']}")
                return False
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_get_history():
    """Test GET /api/v1/tokens/history"""
    print("\n" + "="*60)
    print("TEST: GET /tokens/history")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE}/tokens/history")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n📜 History Count: {data['count']}")

            if data['count'] == 3:
                print("\n✅ PASS: Correct history count (3 entries)")
                print("\nHistory Entries:")
                for i, entry in enumerate(data['history'], 1):
                    print(f"  {i}. {entry['node_name']}: {entry['total_tokens']} tokens @ {entry['timestamp']}")
                return True
            else:
                print(f"\n❌ FAIL: Expected 3 history entries, got {data['count']}")
                return False
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_get_node_totals():
    """Test GET /api/v1/tokens/node/{node_name}"""
    print("\n" + "="*60)
    print("TEST: GET /tokens/node/query_node_1")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE}/tokens/node/query_node_1")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n📈 Node Totals (query_node_1):")
            print(f"  Input Tokens:  {data['input_tokens']}")
            print(f"  Output Tokens: {data['output_tokens']}")
            print(f"  Total Tokens:  {data['total_tokens']}")

            if data['total_tokens'] == 220:
                print("\n✅ PASS: Correct node total (100 + 120 = 220)")
                return True
            else:
                print(f"\n❌ FAIL: Expected 220 total tokens, got {data['total_tokens']}")
                return False
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_get_node_totals_nonexistent():
    """Test GET /api/v1/tokens/node/{node_name} for nonexistent node"""
    print("\n" + "="*60)
    print("TEST: GET /tokens/node/nonexistent_node")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE}/tokens/node/nonexistent_node")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n📈 Node Totals (nonexistent_node):")
            print(f"  Total Tokens: {data['total_tokens']}")

            if data['total_tokens'] == 0:
                print("\n✅ PASS: Returns zero for nonexistent node")
                return True
            else:
                print(f"\n❌ FAIL: Expected 0 tokens, got {data['total_tokens']}")
                return False
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_reset_tokens():
    """Test POST /api/v1/tokens/reset"""
    print("\n" + "="*60)
    print("TEST: POST /tokens/reset")
    print("="*60)

    try:
        response = requests.post(f"{API_BASE}/tokens/reset")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ {data['message']}")

            totals_response = requests.get(f"{API_BASE}/tokens/totals")
            totals = totals_response.json()

            if totals['total_tokens'] == 0:
                print("\n✅ PASS: Token data reset successfully")
                return True
            else:
                print(f"\n❌ FAIL: Expected 0 tokens after reset, got {totals['total_tokens']}")
                return False
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get(f"http://127.0.0.1:8000/")
        return response.status_code == 200
    except:
        return False


def main():
    """Run all token API tests"""
    print("\n" + "="*60)
    print("TEXTLOOM TOKEN API TESTS")
    print("="*60)

    if not check_api_server():
        print("\n❌ ERROR: API server not running!")
        print("\nPlease start the server first:")
        print("  cd src")
        print("  uvicorn api.main:app --reload --port 8000")
        sys.exit(1)

    print("\n✓ API server is running")

    setup_test_data()

    results = []

    results.append(("GET /tokens/totals", test_get_totals()))
    results.append(("GET /tokens/history", test_get_history()))
    results.append(("GET /tokens/node/{node_name}", test_get_node_totals()))
    results.append(("GET /tokens/node/{nonexistent}", test_get_node_totals_nonexistent()))
    results.append(("POST /tokens/reset", test_reset_tokens()))

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
