import sys
import os
import pytest
from datetime import datetime

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.token_manager import TokenManager, get_token_manager
from core.models import TokenUsage


@pytest.fixture
def token_manager():
    manager = get_token_manager()
    manager.reset()
    return manager


@pytest.fixture
def sample_token_usage():
    return TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)


@pytest.fixture
def another_token_usage():
    return TokenUsage(input_tokens=200, output_tokens=100, total_tokens=300)


def test_singleton_pattern():
    manager1 = TokenManager()
    manager2 = TokenManager()
    manager3 = get_token_manager()

    assert manager1 is manager2
    assert manager2 is manager3


def test_initial_state(token_manager):
    totals = token_manager.get_totals()

    assert totals["input_tokens"] == 0
    assert totals["output_tokens"] == 0
    assert totals["total_tokens"] == 0
    assert len(token_manager.get_history()) == 0


def test_add_single_usage(token_manager, sample_token_usage):
    token_manager.add_usage("test_node", sample_token_usage)

    totals = token_manager.get_totals()
    assert totals["input_tokens"] == 100
    assert totals["output_tokens"] == 50
    assert totals["total_tokens"] == 150

    history = token_manager.get_history()
    assert len(history) == 1
    assert history[0]["node_name"] == "test_node"
    assert history[0]["input_tokens"] == 100
    assert history[0]["output_tokens"] == 50
    assert history[0]["total_tokens"] == 150
    assert "timestamp" in history[0]


def test_add_multiple_usages(token_manager, sample_token_usage, another_token_usage):
    token_manager.add_usage("node1", sample_token_usage)
    token_manager.add_usage("node2", another_token_usage)

    totals = token_manager.get_totals()
    assert totals["input_tokens"] == 300
    assert totals["output_tokens"] == 150
    assert totals["total_tokens"] == 450

    history = token_manager.get_history()
    assert len(history) == 2


def test_get_node_totals(token_manager, sample_token_usage, another_token_usage):
    token_manager.add_usage("node1", sample_token_usage)
    token_manager.add_usage("node1", sample_token_usage)
    token_manager.add_usage("node2", another_token_usage)

    node1_totals = token_manager.get_node_totals("node1")
    assert node1_totals["input_tokens"] == 200
    assert node1_totals["output_tokens"] == 100
    assert node1_totals["total_tokens"] == 300

    node2_totals = token_manager.get_node_totals("node2")
    assert node2_totals["input_tokens"] == 200
    assert node2_totals["output_tokens"] == 100
    assert node2_totals["total_tokens"] == 300

    nonexistent_totals = token_manager.get_node_totals("nonexistent")
    assert nonexistent_totals["input_tokens"] == 0
    assert nonexistent_totals["output_tokens"] == 0
    assert nonexistent_totals["total_tokens"] == 0


def test_reset(token_manager, sample_token_usage):
    token_manager.add_usage("test_node", sample_token_usage)

    totals_before = token_manager.get_totals()
    assert totals_before["total_tokens"] > 0

    token_manager.reset()

    totals_after = token_manager.get_totals()
    assert totals_after["input_tokens"] == 0
    assert totals_after["output_tokens"] == 0
    assert totals_after["total_tokens"] == 0
    assert len(token_manager.get_history()) == 0


def test_history_immutability(token_manager, sample_token_usage):
    token_manager.add_usage("test_node", sample_token_usage)

    history1 = token_manager.get_history()
    history2 = token_manager.get_history()

    assert history1 is not history2
    assert history1 == history2

    history1.append({"fake": "entry"})
    history3 = token_manager.get_history()
    assert len(history3) == 1


def test_totals_immutability(token_manager, sample_token_usage):
    token_manager.add_usage("test_node", sample_token_usage)

    totals1 = token_manager.get_totals()
    totals2 = token_manager.get_totals()

    assert totals1 is not totals2
    assert totals1 == totals2

    totals1["input_tokens"] = 999
    totals3 = token_manager.get_totals()
    assert totals3["input_tokens"] == 100


def test_timestamp_format(token_manager, sample_token_usage):
    token_manager.add_usage("test_node", sample_token_usage)

    history = token_manager.get_history()
    timestamp_str = history[0]["timestamp"]

    try:
        datetime.fromisoformat(timestamp_str)
        timestamp_valid = True
    except ValueError:
        timestamp_valid = False

    assert timestamp_valid
