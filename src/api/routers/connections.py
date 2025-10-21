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
from core.base_classes import NodeEnvironment

router = APIRouter()


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
    """
    Create a connection between two nodes.
    
    If the target input already has a connection, it will be automatically
    replaced with the new connection (this is how the backend works).
    
    Args:
        request: Connection parameters specifying source and target
        
    Returns:
        ConnectionResponse: Details of the created connection
        
    Raises:
        HTTPException: 404 if nodes not found, 400 if connection invalid
    """
    try:
        # Find source node
        source_node = NodeEnvironment.node_from_name(request.source_node_path)
        if not source_node:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "source_node_not_found",
                    "message": f"Source node at path '{request.source_node_path}' does not exist"
                }
            )
        
        # Find target node
        target_node = NodeEnvironment.node_from_name(request.target_node_path)
        if not target_node:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "target_node_not_found",
                    "message": f"Target node at path '{request.target_node_path}' does not exist"
                }
            )
        
        # Validate output index
        if request.source_output_index < 0 or request.source_output_index >= len(source_node.output_names()):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_output_index",
                    "message": f"Source output index {request.source_output_index} is invalid for node {source_node.name()}"
                }
            )
        
        # Validate input index
        if request.target_input_index < 0 or request.target_input_index >= len(target_node.input_names()):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_input_index",
                    "message": f"Target input index {request.target_input_index} is invalid for node {target_node.name()}"
                }
            )
        
        # Create the connection (backend handles replacement of existing)
        target_node.set_input(
            request.target_input_index,
            source_node,
            request.source_output_index
        )
        
        # Find the newly created connection
        connection = target_node._inputs.get(request.target_input_index)
        
        if not connection:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "connection_failed",
                    "message": "Connection was not created (backend rejected it)"
                }
            )
        
        return connection_to_response(connection)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to create connection: {str(e)}"
            }
        )


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
    """
    Delete a specific connection.
    
    Removes the connection from both the source node's outputs and
    the target node's inputs.
    
    Args:
        request: Connection identification parameters
        
    Returns:
        SuccessResponse: Confirmation of deletion
        
    Raises:
        HTTPException: 404 if connection not found
    """
    try:
        # Find target node
        target_node = NodeEnvironment.node_from_name(request.target_node_path)
        if not target_node:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "target_node_not_found",
                    "message": f"Target node at path '{request.target_node_path}' does not exist"
                }
            )
        
        # Check if connection exists at this input
        connection = target_node._inputs.get(request.target_input_index)
        
        if not connection:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "connection_not_found",
                    "message": f"No connection found at input {request.target_input_index} of node {target_node.name()}"
                }
            )
        
        # Verify this is the connection we want to delete
        if (connection.output_node().path() != request.source_node_path or
            connection.output_index() != request.source_output_index):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "connection_mismatch",
                    "message": "Connection at specified input does not match source parameters"
                }
            )
        
        # Remove the connection
        target_node.remove_connection(connection)
        
        return SuccessResponse(
            success=True,
            message=f"Connection from {request.source_node_path}[{request.source_output_index}] to {request.target_node_path}[{request.target_input_index}] deleted"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to delete connection: {str(e)}"
            }
        )