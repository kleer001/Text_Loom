"""
TextLoom API - Connection Endpoints

Handles connection-related API operations:
- Create connections between nodes
- Delete specific connections
"""

from fastapi import APIRouter, HTTPException, status
from api.models import (
    ConnectionRequest,
    ConnectionDeleteRequest,
    ConnectionResponse,
    SuccessResponse,
    ErrorResponse,
    connection_to_response
)
from api.router_utils import validate_node_exists, validate_output_index, validate_input_index, raise_http_error
from core.base_classes import NodeEnvironment
from core.input_null_node import InputNullNode
import os

router = APIRouter()


def route_connection_target(target_node_path: str, target_input_index: int):
    """
    Routes connection targets to handle special cases like InputNullNode.

    InputNullNode is an internal node within LooperNode that retrieves data from
    the parent LooperNode's inputs. When the GUI sends a connection request to
    InputNullNode (as part of looper_start display), we redirect it to the
    parent LooperNode.

    Returns:
        Tuple of (actual_target_node, actual_input_index)
    """
    target_node = validate_node_exists(target_node_path, "Target node")

    if isinstance(target_node, InputNullNode):
        parent_path = os.path.dirname(target_node.path())
        parent_node = validate_node_exists(parent_path, "Parent looper node")
        return parent_node, target_input_index

    return target_node, target_input_index


def find_connection_in_target_node(target_node, target_input_index):
    connection = target_node._inputs.get(target_input_index)
    if not connection:
        raise_http_error(
            404,
            "connection_not_found",
            f"No connection found at input {target_input_index} of node {target_node.name()}"
        )
    return connection


def validate_connection_match(connection, expected_source_path, expected_source_output):
    if (connection.output_node().path() != expected_source_path or
        connection.output_index() != expected_source_output):
        raise_http_error(
            404,
            "connection_mismatch",
            "Connection at specified input does not match source parameters"
        )


def find_connection_by_id(connection_id: str):
    for node in NodeEnvironment.nodes.values():
        for connection in node._inputs.values():
            if connection and connection.session_id() == connection_id:
                return connection
    raise_http_error(404, "connection_not_found", f"Connection with ID '{connection_id}' does not exist")


@router.post(
    "/connections",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a connection",
    description="Creates a connection from a source node's output to a target node's input. Automatically replaces existing connections.",
    responses={
        201: {"description": "Connection created successfully"},
        404: {"description": "Source or target node not found", "model": ErrorResponse},
        400: {"description": "Invalid connection parameters", "model": ErrorResponse}
    }
)
def create_connection(request: ConnectionRequest) -> ConnectionResponse:
    try:
        source_node = validate_node_exists(request.source_node_path, "Source node")
        target_node, target_input_index = route_connection_target(
            request.target_node_path,
            request.target_input_index
        )

        validate_output_index(source_node, request.source_output_index)
        validate_input_index(target_node, target_input_index)

        target_node.set_input(
            target_input_index,
            source_node,
            request.source_output_index
        )

        connection = target_node._inputs.get(target_input_index)
        if not connection:
            raise_http_error(500, "connection_failed", "Connection was not created (backend rejected it)")

        return connection_to_response(connection)

    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "internal_error", f"Failed to create connection: {str(e)}")


@router.delete(
    "/connections",
    response_model=SuccessResponse,
    summary="Delete a connection",
    description="Deletes a specific connection between two nodes.",
    responses={
        200: {"description": "Connection deleted successfully"},
        404: {"description": "Connection not found", "model": ErrorResponse}
    }
)
def delete_connection(request: ConnectionDeleteRequest) -> SuccessResponse:
    try:
        target_node, target_input_index = route_connection_target(
            request.target_node_path,
            request.target_input_index
        )
        connection = find_connection_in_target_node(target_node, target_input_index)
        validate_connection_match(connection, request.source_node_path, request.source_output_index)

        target_node.remove_connection(connection)

        return SuccessResponse(
            success=True,
            message=f"Connection from {request.source_node_path}[{request.source_output_index}] to {request.target_node_path}[{request.target_input_index}] deleted"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "internal_error", f"Failed to delete connection: {str(e)}")


@router.delete(
    "/connections/{connection_id}",
    response_model=SuccessResponse,
    summary="Delete a connection by ID",
    description="Deletes a connection using its session ID.",
    responses={
        200: {"description": "Connection deleted successfully"},
        404: {"description": "Connection not found", "model": ErrorResponse}
    }
)
def delete_connection_by_id(connection_id: str) -> SuccessResponse:
    try:
        connection = find_connection_by_id(connection_id)
        target_node = connection.input_node()
        target_node.remove_connection(connection)

        return SuccessResponse(
            success=True,
            message=f"Connection {connection_id} deleted"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "internal_error", f"Failed to delete connection: {str(e)}")
