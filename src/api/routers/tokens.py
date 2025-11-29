"""
TextLoom API - Token Tracking Endpoints

Handles token usage tracking for LLM queries:
- Get session-wide token totals
- Get per-node token totals
- Get token usage history with timestamps
- Reset token tracking
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Path
from pydantic import BaseModel, Field
from api.router_utils import raise_http_error
from api.models import SuccessResponse
from core.token_manager import get_token_manager

router = APIRouter()


class TokenTotalsResponse(BaseModel):
    """Session-wide token usage totals.

    Example:
        {
            "input_tokens": 1250,
            "output_tokens": 3400,
            "total_tokens": 4650
        }
    """
    input_tokens: int = Field(..., description="Total input tokens across all queries")
    output_tokens: int = Field(..., description="Total output tokens across all queries")
    total_tokens: int = Field(..., description="Total tokens (input + output)")


class TokenHistoryEntry(BaseModel):
    """Single token usage history entry.

    Example:
        {
            "timestamp": "2025-11-29T10:30:45.123456",
            "node_name": "query_node_1",
            "input_tokens": 25,
            "output_tokens": 75,
            "total_tokens": 100
        }
    """
    timestamp: str = Field(..., description="ISO 8601 timestamp of the query")
    node_name: str = Field(..., description="Name of the node that made the query")
    input_tokens: int = Field(..., description="Input tokens for this query")
    output_tokens: int = Field(..., description="Output tokens for this query")
    total_tokens: int = Field(..., description="Total tokens for this query")


class TokenHistoryResponse(BaseModel):
    """Complete token usage history.

    Example:
        {
            "count": 15,
            "history": [...]
        }
    """
    count: int = Field(..., description="Number of queries in history")
    history: List[TokenHistoryEntry] = Field(..., description="Chronological list of token usage entries")


@router.get(
    "/tokens/totals",
    response_model=TokenTotalsResponse,
    summary="Get session-wide token totals",
    description="Returns the cumulative token usage across all LLM queries in the current session.",
)
def get_token_totals() -> TokenTotalsResponse:
    """Get session-wide token usage totals."""
    try:
        token_manager = get_token_manager()
        totals = token_manager.get_totals()
        return TokenTotalsResponse(**totals)
    except Exception as e:
        raise_http_error(500, "internal_error", f"Error retrieving token totals: {str(e)}")


@router.get(
    "/tokens/history",
    response_model=TokenHistoryResponse,
    summary="Get token usage history",
    description="Returns a chronological list of all LLM queries with their token usage and timestamps.",
)
def get_token_history() -> TokenHistoryResponse:
    """Get complete token usage history."""
    try:
        token_manager = get_token_manager()
        history = token_manager.get_history()
        return TokenHistoryResponse(
            count=len(history),
            history=[TokenHistoryEntry(**entry) for entry in history]
        )
    except Exception as e:
        raise_http_error(500, "internal_error", f"Error retrieving token history: {str(e)}")


@router.get(
    "/tokens/node/{node_name}",
    response_model=TokenTotalsResponse,
    summary="Get per-node token totals",
    description="Returns the cumulative token usage for a specific node across all its queries.",
)
def get_node_token_totals(
    node_name: str = Path(..., description="Name of the node to query")
) -> TokenTotalsResponse:
    """Get token usage totals for a specific node."""
    try:
        token_manager = get_token_manager()
        totals = token_manager.get_node_totals(node_name)
        return TokenTotalsResponse(**totals)
    except Exception as e:
        raise_http_error(500, "internal_error", f"Error retrieving node token totals: {str(e)}")


@router.post(
    "/tokens/reset",
    response_model=SuccessResponse,
    summary="Reset token tracking",
    description="Clears all token usage data including totals and history. This cannot be undone.",
)
def reset_token_tracking() -> SuccessResponse:
    """Reset all token tracking data."""
    try:
        token_manager = get_token_manager()
        token_manager.reset()
        return SuccessResponse(success=True, message="Token tracking data reset successfully")
    except Exception as e:
        raise_http_error(500, "reset_failed", f"Error resetting token tracking: {str(e)}")
