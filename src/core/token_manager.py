from typing import Dict, List, Any
from datetime import datetime
from core.models import TokenUsage


class TokenManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._history: List[Dict[str, Any]] = []
        self._session_totals = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }
        self._initialized = True

    def add_usage(self, node_name: str, token_usage: TokenUsage) -> None:
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

    def get_totals(self) -> Dict[str, int]:
        return self._session_totals.copy()

    def get_history(self) -> List[Dict[str, Any]]:
        return self._history.copy()

    def reset(self) -> None:
        self._history.clear()
        self._session_totals = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

    def get_node_totals(self, node_name: str) -> Dict[str, int]:
        node_totals = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }
        for entry in self._history:
            if entry["node_name"] == node_name:
                node_totals["input_tokens"] += entry["input_tokens"]
                node_totals["output_tokens"] += entry["output_tokens"]
                node_totals["total_tokens"] += entry["total_tokens"]
        return node_totals


def get_token_manager() -> TokenManager:
    return TokenManager()
