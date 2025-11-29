"""
Test REPL Token Tracking Functions

This script demonstrates using token tracking functions in the REPL.
It can be run directly or loaded into the REPL with:
    python src/repl/tloom_shell.py -s src/tests/test_repl_tokens.py

Usage (direct):
    python src/tests/test_repl_tokens.py
"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from repl.helpers import (
    create, connect, run, token_totals, token_history,
    node_tokens, reset_tokens, clear
)
from core.token_manager import get_token_manager
from core.models import TokenUsage


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_token_totals():
    """Test token_totals() helper function"""
    print_section("Test: token_totals()")

    token_manager = get_token_manager()
    token_manager.reset()

    token_manager.add_usage("query1", TokenUsage(
        input_tokens=100,
        output_tokens=200,
        total_tokens=300
    ))

    totals = token_totals()
    print(f"Session Totals: {totals}")

    assert totals['input_tokens'] == 100
    assert totals['output_tokens'] == 200
    assert totals['total_tokens'] == 300
    print("✅ PASS")


def test_token_history():
    """Test token_history() helper function"""
    print_section("Test: token_history()")

    token_manager = get_token_manager()
    token_manager.reset()

    token_manager.add_usage("query1", TokenUsage(
        input_tokens=50,
        output_tokens=100,
        total_tokens=150
    ))

    token_manager.add_usage("query2", TokenUsage(
        input_tokens=75,
        output_tokens=125,
        total_tokens=200
    ))

    history = token_history()
    print(f"History entries: {len(history)}")

    for i, entry in enumerate(history, 1):
        print(f"  {i}. {entry['node_name']}: {entry['total_tokens']} tokens @ {entry['timestamp']}")

    assert len(history) == 2
    assert history[0]['node_name'] == 'query1'
    assert history[1]['node_name'] == 'query2'
    print("✅ PASS")


def test_node_tokens():
    """Test node_tokens() helper function"""
    print_section("Test: node_tokens(node_name)")

    token_manager = get_token_manager()
    token_manager.reset()

    token_manager.add_usage("query_node_1", TokenUsage(
        input_tokens=25,
        output_tokens=75,
        total_tokens=100
    ))

    token_manager.add_usage("query_node_1", TokenUsage(
        input_tokens=30,
        output_tokens=90,
        total_tokens=120
    ))

    token_manager.add_usage("query_node_2", TokenUsage(
        input_tokens=50,
        output_tokens=150,
        total_tokens=200
    ))

    node1_totals = node_tokens("query_node_1")
    node2_totals = node_tokens("query_node_2")

    print(f"query_node_1 totals: {node1_totals}")
    print(f"query_node_2 totals: {node2_totals}")

    assert node1_totals['total_tokens'] == 220
    assert node2_totals['total_tokens'] == 200
    print("✅ PASS")


def test_reset_tokens():
    """Test reset_tokens() helper function"""
    print_section("Test: reset_tokens()")

    token_manager = get_token_manager()
    token_manager.add_usage("test", TokenUsage(
        input_tokens=100,
        output_tokens=200,
        total_tokens=300
    ))

    print("Before reset:")
    print(f"  Totals: {token_totals()}")
    print(f"  History entries: {len(token_history())}")

    reset_tokens()

    print("\nAfter reset:")
    totals = token_totals()
    history = token_history()
    print(f"  Totals: {totals}")
    print(f"  History entries: {len(history)}")

    assert totals['total_tokens'] == 0
    assert len(history) == 0
    print("✅ PASS")


def test_repl_workflow():
    """Test complete REPL workflow with token tracking"""
    print_section("Test: Complete REPL Workflow")

    clear()
    reset_tokens()

    print("Creating test nodes with REPL helpers...")

    text1 = create('text', 'prompt1', text_string='["What is 2+2?"]', pass_through=False)
    print(f"  ✓ Created {text1.path()}")

    text2 = create('text', 'prompt2', text_string='["Name a planet"]', pass_through=False)
    print(f"  ✓ Created {text2.path()}")

    print("\nNote: QueryNode would normally track tokens automatically")
    print("For this test, we simulate token usage manually")

    token_manager = get_token_manager()
    token_manager.add_usage("query1", TokenUsage(
        input_tokens=10,
        output_tokens=30,
        total_tokens=40
    ))

    token_manager.add_usage("query2", TokenUsage(
        input_tokens=15,
        output_tokens=25,
        total_tokens=40
    ))

    print("\n📊 Session Token Totals:")
    totals = token_totals()
    print(f"   Input:  {totals['input_tokens']}")
    print(f"   Output: {totals['output_tokens']}")
    print(f"   Total:  {totals['total_tokens']}")

    print("\n📜 Token History:")
    for i, entry in enumerate(token_history(), 1):
        print(f"   {i}. {entry['node_name']}: {entry['total_tokens']} tokens")

    print("\n📈 Per-Node Totals:")
    print(f"   query1: {node_tokens('query1')['total_tokens']} tokens")
    print(f"   query2: {node_tokens('query2')['total_tokens']} tokens")

    assert totals['total_tokens'] == 80
    assert len(token_history()) == 2
    print("\n✅ PASS")


def main():
    """Run all REPL token tracking tests"""
    print("\n" + "="*60)
    print("  REPL TOKEN TRACKING TESTS")
    print("="*60)

    tests = [
        test_token_totals,
        test_token_history,
        test_node_tokens,
        test_reset_tokens,
        test_repl_workflow
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1

    print_section("SUMMARY")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All REPL token tracking tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
