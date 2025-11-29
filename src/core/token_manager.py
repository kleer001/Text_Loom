"""Singleton manager for centralized LLM token usage tracking.

Provides session-wide and per-node token usage tracking with timestamped history.
Supports accumulation across multiple queries and provides data structures ready
for JSON serialization to React GUI. Thread-safe for concurrent access.
"""

from typing import Dict, List, Any
from datetime import datetime
from threading import Lock
from core.models import TokenUsage


class TokenManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TokenManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._history: List[Dict[str, Any]] = []
        self._session_totals = self._create_empty_totals()
        self._node_cache: Dict[str, Dict[str, int]] = {}
        self._data_lock = Lock()
        self._initialized = True

    def _create_empty_totals(self) -> Dict[str, int]:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

    def add_usage(self, node_name: str, token_usage: TokenUsage) -> None:
        with self._data_lock:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "node_name": node_name,
                "input_tokens": token_usage.input_tokens,
                "output_tokens": token_usage.output_tokens,
                "total_tokens": token_usage.total_tokens
            }
            self._history.append(entry)

            self._session_totals["input_tokens"] += token_usage.input_tokens
            self._session_totals["output_tokens"] += token_usage.output_tokens
            self._session_totals["total_tokens"] += token_usage.total_tokens

            if node_name not in self._node_cache:
                self._node_cache[node_name] = self._create_empty_totals()

            self._node_cache[node_name]["input_tokens"] += token_usage.input_tokens
            self._node_cache[node_name]["output_tokens"] += token_usage.output_tokens
            self._node_cache[node_name]["total_tokens"] += token_usage.total_tokens

    def get_totals(self) -> Dict[str, int]:
        with self._data_lock:
            return self._session_totals.copy()

    def get_history(self) -> List[Dict[str, Any]]:
        with self._data_lock:
            return self._history.copy()

    def reset(self) -> None:
        with self._data_lock:
            self._history.clear()
            self._session_totals = self._create_empty_totals()
            self._node_cache.clear()

    def get_node_totals(self, node_name: str) -> Dict[str, int]:
        with self._data_lock:
            if node_name in self._node_cache:
                return self._node_cache[node_name].copy()
            else:
                return self._create_empty_totals()


def get_token_manager() -> TokenManager:
    return TokenManager()
