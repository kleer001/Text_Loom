"""Data models for LLM token usage tracking.

Provides immutable dataclasses for representing token counts and LLM responses
with JSON serialization support for React GUI integration.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int

    def __post_init__(self) -> None:
        if self.input_tokens < 0:
            raise ValueError(f"input_tokens must be >= 0, got {self.input_tokens}")
        if self.output_tokens < 0:
            raise ValueError(f"output_tokens must be >= 0, got {self.output_tokens}")
        if self.total_tokens < 0:
            raise ValueError(f"total_tokens must be >= 0, got {self.total_tokens}")

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    token_usage: Optional[TokenUsage] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "content": self.content
        }
        if self.token_usage:
            result["token_usage"] = self.token_usage.to_dict()
        return result
