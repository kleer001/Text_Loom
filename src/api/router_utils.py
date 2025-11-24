"""
Shared utilities for API routers.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from core.base_classes import Node, NodeEnvironment


def error_detail(error_type: str, message: str, **kwargs) -> Dict[str, Any]:
    return {"error": error_type, "message": message, **kwargs}


def raise_http_error(status_code: int, error_type: str, message: str, **kwargs):
    raise HTTPException(
        status_code=status_code,
        detail=error_detail(error_type, message, **kwargs)
    )


def find_node_by_session_id(session_id: str) -> Node:
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if node and node.session_id() == session_id:
            return node
    raise_http_error(404, "node_not_found", f"Node with session_id {session_id} does not exist")


def find_node_by_path(path: str) -> Node:
    node = NodeEnvironment.node_from_name(path)
    if not node:
        raise_http_error(404, "node_not_found", f"Node at path '{path}' does not exist")
    return node


def validate_node_exists(path: str, node_label: str = "Node") -> Node:
    node = NodeEnvironment.node_from_name(path)
    if not node:
        raise_http_error(
            404,
            f"{node_label.lower().replace(' ', '_')}_not_found",
            f"{node_label} at path '{path}' does not exist"
        )
    return node


def validate_output_index(node: Node, output_index: int):
    output_names = node.output_names()
    if output_index < 0 or output_index >= len(output_names):
        raise_http_error(
            400,
            "invalid_output_index",
            f"Output index {output_index} is invalid for node {node.name()}"
        )


def validate_input_index(node: Node, input_index: int):
    input_names = node.input_names()
    if input_index < 0 or input_index >= len(input_names):
        raise_http_error(
            400,
            "invalid_input_index",
            f"Input index {input_index} is invalid for node {node.name()}"
        )
