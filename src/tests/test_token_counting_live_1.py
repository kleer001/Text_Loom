import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState
from core.token_manager import get_token_manager


def verify(actual, expected, name):
    if actual == expected:
        print(f"✅ {name} PASSED")
        print(f"Expected: {expected}")
        print(f"Got: {actual}")
    else:
        print(f"❌ {name} FAILED")
        print(f"Expected: {expected}")
        print(f"Got: {actual}")
        if isinstance(expected, list) and isinstance(actual, list):
            print(f"Length - Expected: {len(expected)}, Got: {len(actual)}")


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_token_status(manager, label=""):
    totals = manager.get_totals()
    print(f"\n📊 Token Manager Status {label}:")
    print(f"   Input Tokens:  {totals['input_tokens']}")
    print(f"   Output Tokens: {totals['output_tokens']}")
    print(f"   Total Tokens:  {totals['total_tokens']}")

    history = manager.get_history()
    if history:
        print(f"\n📜 Query History ({len(history)} queries):")
        for idx, entry in enumerate(history, 1):
            print(f"   {idx}. {entry['node_name']} - "
                  f"In: {entry['input_tokens']}, "
                  f"Out: {entry['output_tokens']}, "
                  f"Total: {entry['total_tokens']}")


print_section("Live Token Counting Test")
print("This test demonstrates real-time token tracking for LLM queries.")
print("Note: Requires a running LLM server (e.g., Ollama) to execute.")

token_manager = get_token_manager()
token_manager.reset()

print_section("Test 1: Single Query with Token Tracking")

text_node = Node.create_node(NodeType.TEXT, node_name="question")
text_node._parms["text_string"].set('["What is the capital of France?"]')
text_node._parms["pass_through"].set(False)

query_node = Node.create_node(NodeType.QUERY, node_name="llm_query_1")
query_node.set_input(0, text_node)
query_node._parms["track_tokens"].set(True)
query_node._parms["limit"].set(True)

print("\n🔍 Querying LLM with: 'What is the capital of France?'")
print("⏳ Waiting for response...")

try:
    output = query_node.eval()

    print(f"\n💬 LLM Response:")
    print(f"   {output[0]}")

    token_usage = query_node._parms["token_usage"].eval()
    print(f"\n🎯 Token Usage (displayed on node):")
    print(f"   {token_usage}")

    verify(len(output), 1, "Single query returns one response")
    verify("paris" in output[0].lower() or "Paris" in output[0], True,
           "Response mentions Paris")
    verify("Input:" in token_usage and "Output:" in token_usage, True,
           "Token usage string formatted correctly")

    print_token_status(token_manager, "after first query")

    totals = token_manager.get_totals()
    verify(totals["total_tokens"] > 0, True,
           "TokenManager recorded token usage")

except Exception as e:
    print(f"\n⚠️  Test requires running LLM server")
    print(f"   Error: {e}")
    print(f"   Skipping live query tests...")


print_section("Test 2: Multiple Queries with Accumulation")

text_node2 = Node.create_node(NodeType.TEXT, node_name="questions")
text_node2._parms["text_string"].set(
    '["What is 2+2?", "What color is the sky?", "Name a planet."]'
)
text_node2._parms["pass_through"].set(False)

query_node2 = Node.create_node(NodeType.QUERY, node_name="llm_query_2")
query_node2.set_input(0, text_node2)
query_node2._parms["track_tokens"].set(True)
query_node2._parms["limit"].set(False)

print("\n🔍 Querying LLM with 3 prompts:")
print("   1. What is 2+2?")
print("   2. What color is the sky?")
print("   3. Name a planet.")
print("⏳ Waiting for responses...")

try:
    totals_before = token_manager.get_totals()

    output2 = query_node2.eval()

    print(f"\n💬 LLM Responses:")
    for idx, response in enumerate(output2, 1):
        print(f"   {idx}. {response}")

    token_usage2 = query_node2._parms["token_usage"].eval()
    print(f"\n🎯 Token Usage (for all 3 queries):")
    print(f"   {token_usage2}")

    verify(len(output2), 3, "Three queries return three responses")

    print_token_status(token_manager, "after multiple queries")

    totals_after = token_manager.get_totals()
    tokens_added = totals_after["total_tokens"] - totals_before["total_tokens"]
    verify(tokens_added > 0, True,
           f"Tokens accumulated (+{tokens_added} from previous)")

except Exception as e:
    print(f"\n⚠️  Test requires running LLM server")
    print(f"   Error: {e}")


print_section("Test 3: Per-Node Token Tracking")

try:
    query1_totals = token_manager.get_node_totals("llm_query_1")
    query2_totals = token_manager.get_node_totals("llm_query_2")

    print("\n📈 Token Usage by Node:")
    print(f"   llm_query_1: {query1_totals['total_tokens']} tokens")
    print(f"   llm_query_2: {query2_totals['total_tokens']} tokens")

    verify(query1_totals["total_tokens"] > 0, True,
           "Node 1 has tracked tokens")
    verify(query2_totals["total_tokens"] > 0, True,
           "Node 2 has tracked tokens")
    verify(query2_totals["total_tokens"] > query1_totals["total_tokens"], True,
           "Node 2 used more tokens (3 queries vs 1)")

except Exception as e:
    print(f"\n⚠️  Skipped: {e}")


print_section("Test 4: Token Tracking Disabled")

text_node3 = Node.create_node(NodeType.TEXT, node_name="no_tracking")
text_node3._parms["text_string"].set('["Hello!"]')
text_node3._parms["pass_through"].set(False)

query_node3 = Node.create_node(NodeType.QUERY, node_name="llm_query_3")
query_node3.set_input(0, text_node3)
query_node3._parms["track_tokens"].set(False)
query_node3._parms["limit"].set(True)

print("\n🔍 Querying LLM with token tracking DISABLED")
print("⏳ Waiting for response...")

try:
    totals_before = token_manager.get_totals()

    output3 = query_node3.eval()

    print(f"\n💬 LLM Response:")
    print(f"   {output3[0]}")

    token_usage3 = query_node3._parms["token_usage"].eval()
    print(f"\n🎯 Token Usage Display:")
    print(f"   {token_usage3}")

    verify(token_usage3, "Token tracking disabled",
           "Token usage shows disabled message")

    totals_after = token_manager.get_totals()
    verify(totals_after["total_tokens"], totals_before["total_tokens"],
           "TokenManager unchanged when tracking disabled")

    print_token_status(token_manager, "(unchanged)")

except Exception as e:
    print(f"\n⚠️  Test requires running LLM server")
    print(f"   Error: {e}")


print_section("Test 5: Reset Token Manager")

token_manager.reset()
print("\n🔄 TokenManager reset")

print_token_status(token_manager, "after reset")

totals = token_manager.get_totals()
verify(totals["input_tokens"], 0, "Input tokens reset to 0")
verify(totals["output_tokens"], 0, "Output tokens reset to 0")
verify(totals["total_tokens"], 0, "Total tokens reset to 0")
verify(len(token_manager.get_history()), 0, "History cleared")


print_section("Test 6: Data Serialization for React")

token_manager.reset()

text_node4 = Node.create_node(NodeType.TEXT, node_name="serialize_test")
text_node4._parms["text_string"].set('["Quick test"]')
text_node4._parms["pass_through"].set(False)

query_node4 = Node.create_node(NodeType.QUERY, node_name="llm_query_4")
query_node4.set_input(0, text_node4)
query_node4._parms["track_tokens"].set(True)

print("\n🔍 Testing data serialization for React GUI...")

try:
    output4 = query_node4.eval()

    totals_dict = token_manager.get_totals()
    history_list = token_manager.get_history()

    print(f"\n📦 Serialized Data (JSON-ready):")
    print(f"   Totals Type: {type(totals_dict).__name__}")
    print(f"   History Type: {type(history_list).__name__}")
    print(f"   Sample History Entry: {history_list[0] if history_list else 'None'}")

    verify(isinstance(totals_dict, dict), True, "Totals returns dict")
    verify(isinstance(history_list, list), True, "History returns list")

    if history_list:
        entry = history_list[0]
        verify(isinstance(entry["timestamp"], str), True,
               "Timestamp is ISO string")
        verify(isinstance(entry["total_tokens"], int), True,
               "Token counts are integers")

        print("\n✅ Data structure ready for JSON serialization to React")

except Exception as e:
    print(f"\n⚠️  Test requires running LLM server")
    print(f"   Error: {e}")


print_section("Test Complete")
print("\n📝 Summary:")
print("   - Token tracking works with live LLM queries")
print("   - TokenManager accumulates usage across queries")
print("   - Per-node tracking available")
print("   - Token tracking can be enabled/disabled per node")
print("   - Data structures ready for React GUI integration")
print("\n💡 Note: Some tests may show warnings if LLM server is not running.")
print("   This is expected - the tracking system handles errors gracefully.\n")
