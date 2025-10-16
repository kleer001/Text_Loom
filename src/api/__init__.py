"""
TextLoom API Package

REST API for the TextLoom node-based text processing system.

This package provides HTTP endpoints for:
- Querying workspace state
- Managing nodes
- Managing connections
- Executing node workflows
- Managing global variables

Usage:
    uvicorn api.main:app --reload --port 8000
"""

__version__ = "1.0.0"
