import sys
import os
import pytest
from unittest.mock import Mock, patch

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState
from core.models import TokenUsage, LLMResponse
from core.token_manager import get_token_manager


@pytest.fixture
def text_node():
    node = Node.create_node(NodeType.TEXT, node_name="test_text")
    node._parms["text_string"].set('["test prompt"]')
    node._parms["pass_through"].set(False)
    return node


@pytest.fixture
def query_node():
    node = Node.create_node(NodeType.QUERY, node_name="test_query")
    return node


@pytest.fixture
def mock_llm_response_with_tokens():
    usage = TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30)
    return LLMResponse(content="Test LLM response", token_usage=usage)


@pytest.fixture
def mock_llm_response_no_tokens():
    return LLMResponse(content="Test LLM response", token_usage=None)


@pytest.fixture(autouse=True)
def reset_token_manager():
    manager = get_token_manager()
    manager.reset()
    yield
    manager.reset()


def test_query_node_has_track_tokens_parameter(query_node):
    assert "track_tokens" in query_node._parms
    assert query_node._parms["track_tokens"].eval() == True


def test_query_node_has_token_usage_parameter(query_node):
    assert "token_usage" in query_node._parms
    assert query_node._parms["token_usage"].eval() == ""


def test_query_node_tracks_tokens_when_enabled(text_node, query_node, mock_llm_response_with_tokens):
    query_node.set_input(0, text_node)
    query_node._parms["track_tokens"].set(True)

    with patch('core.query_node.get_clean_llm_response_with_tokens', return_value=mock_llm_response_with_tokens):
        output = query_node.eval()

        assert output == ["Test LLM response"]

        token_usage_display = query_node._parms["token_usage"].eval()
        assert "Input: 10" in token_usage_display
        assert "Output: 20" in token_usage_display
        assert "Total: 30" in token_usage_display

        token_manager = get_token_manager()
        totals = token_manager.get_totals()
        assert totals["input_tokens"] == 10
        assert totals["output_tokens"] == 20
        assert totals["total_tokens"] == 30


def test_query_node_skips_tracking_when_disabled(text_node, query_node):
    query_node.set_input(0, text_node)
    query_node._parms["track_tokens"].set(False)

    mock_response = {"response": "Test response"}
    with patch('core.llm_utils.query_llm', return_value=mock_response):
        with patch('core.llm_utils.get_response', return_value="Test response"):
            output = query_node.eval()

            assert output == ["Test response"]

            token_usage_display = query_node._parms["token_usage"].eval()
            assert token_usage_display == "Token tracking disabled"

            token_manager = get_token_manager()
            totals = token_manager.get_totals()
            assert totals["total_tokens"] == 0


def test_query_node_handles_multiple_prompts(text_node, query_node, mock_llm_response_with_tokens):
    text_node._parms["text_string"].set('["prompt1", "prompt2", "prompt3"]')
    text_node.set_state(NodeState.UNCOOKED)

    query_node.set_input(0, text_node)
    query_node._parms["track_tokens"].set(True)
    query_node._parms["limit"].set(False)

    with patch('core.query_node.get_clean_llm_response_with_tokens', return_value=mock_llm_response_with_tokens):
        output = query_node.eval()

        assert len(output) == 3
        assert all(item == "Test LLM response" for item in output)

        token_usage_display = query_node._parms["token_usage"].eval()
        assert "Input: 30" in token_usage_display
        assert "Output: 60" in token_usage_display
        assert "Total: 90" in token_usage_display

        token_manager = get_token_manager()
        totals = token_manager.get_totals()
        assert totals["total_tokens"] == 90


def test_query_node_handles_missing_token_usage(text_node, query_node, mock_llm_response_no_tokens):
    query_node.set_input(0, text_node)
    query_node._parms["track_tokens"].set(True)

    with patch('core.query_node.get_clean_llm_response_with_tokens', return_value=mock_llm_response_no_tokens):
        output = query_node.eval()

        assert output == ["Test LLM response"]

        token_usage_display = query_node._parms["token_usage"].eval()
        assert "Input: 0" in token_usage_display
        assert "Output: 0" in token_usage_display
        assert "Total: 0" in token_usage_display

        token_manager = get_token_manager()
        totals = token_manager.get_totals()
        assert totals["total_tokens"] == 0


def test_query_node_accumulates_tokens_across_multiple_cooks(text_node, query_node, mock_llm_response_with_tokens):
    query_node.set_input(0, text_node)
    query_node._parms["track_tokens"].set(True)

    with patch('core.query_node.get_clean_llm_response_with_tokens', return_value=mock_llm_response_with_tokens):
        query_node.eval()

        token_manager = get_token_manager()
        totals_first = token_manager.get_totals()
        assert totals_first["total_tokens"] == 30

        query_node.set_state(NodeState.UNCOOKED)
        query_node.eval()

        totals_second = token_manager.get_totals()
        assert totals_second["total_tokens"] == 60


def test_query_node_tracks_per_node_usage(mock_llm_response_with_tokens):
    text_node1 = Node.create_node(NodeType.TEXT, node_name="text1")
    text_node1._parms["text_string"].set('["prompt1"]')
    text_node1._parms["pass_through"].set(False)

    text_node2 = Node.create_node(NodeType.TEXT, node_name="text2")
    text_node2._parms["text_string"].set('["prompt2"]')
    text_node2._parms["pass_through"].set(False)

    query_node1 = Node.create_node(NodeType.QUERY, node_name="query1")
    query_node1.set_input(0, text_node1)
    query_node1._parms["track_tokens"].set(True)

    query_node2 = Node.create_node(NodeType.QUERY, node_name="query2")
    query_node2.set_input(0, text_node2)
    query_node2._parms["track_tokens"].set(True)

    with patch('core.query_node.get_clean_llm_response_with_tokens', return_value=mock_llm_response_with_tokens):
        query_node1.eval()
        query_node2.eval()

        token_manager = get_token_manager()

        query1_totals = token_manager.get_node_totals("query1")
        assert query1_totals["total_tokens"] == 30

        query2_totals = token_manager.get_node_totals("query2")
        assert query2_totals["total_tokens"] == 30

        global_totals = token_manager.get_totals()
        assert global_totals["total_tokens"] == 60


def test_query_node_handles_errors_gracefully(text_node, query_node):
    query_node.set_input(0, text_node)
    query_node._parms["track_tokens"].set(True)

    with patch('core.query_node.get_clean_llm_response_with_tokens', side_effect=Exception("Test error")):
        output = query_node.eval()

        assert output == [""]
        assert len(query_node.errors()) > 0

        token_manager = get_token_manager()
        totals = token_manager.get_totals()
        assert totals["total_tokens"] == 0
