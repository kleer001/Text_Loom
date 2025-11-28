from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int

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
