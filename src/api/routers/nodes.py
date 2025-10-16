"""
TextLoom API - Node Endpoints

Handles node-related API operations:
- List all nodes
- Get single node details
"""

from typing import List
from fastapi import APIRouter, HTTPException, Path
from api.models import NodeResponse, ErrorResponse, node_to_response
from core.base_classes import NodeEnvironment

router = APIRouter()


@router.get(
    "/nodes",
    response_model=List[NodeResponse],
    summary="List all nodes",
    description="Returns a list of all nodes in the current workspace with full details.",
    responses={
        200: {
            "description": "List of all nodes",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "session_id": 123456789,
                            "name": "text1",
                            "path": "/text1",
                            "type": "text",
                            "state": "unchanged",
                            "parameters": {},
                            "inputs": [],
                            "outputs": [],
                            "errors": [],
                            "warnings": [],
                            "position": [100.0, 200.0],
                            "color": [1.0, 1.0, 1.0],
                            "selected": False,
                            "is_time_dependent": False,
                            "cook_count": 0,
                            "last_cook_time": 0.0
                        }
                    ]
                }
            }
        }
    }
)
def list_nodes() -> List[NodeResponse]:
    """
    Get all nodes in the workspace.
    
    Returns complete node information including parameters, connections,
    state, and UI properties for all nodes in the current workspace.
    
    Returns:
        List[NodeResponse]: Array of all nodes with full details
    """
    all_node_paths = NodeEnvironment.list_nodes()
    nodes = []
    
    for path in all_node_paths:
        node = NodeEnvironment.node_from_name(path)
        if node:
            try:
                node_response = node_to_response(node)
                nodes.append(node_response)
            except Exception as e:
                # Log error but continue with other nodes
                print(f"Error converting node {path}: {e}")
                continue
    
    return nodes


@router.get(
    "/nodes/{session_id}",
    response_model=NodeResponse,
    summary="Get node by session ID",
    description="Returns detailed information about a specific node identified by its unique session ID.",
    responses={
        200: {
            "description": "Node details",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": 123456789,
                        "name": "text1",
                        "path": "/text1",
                        "type": "text",
                        "state": "unchanged",
                        "parameters": {
                            "text_string": {
                                "type": "STRING",
                                "value": "Hello World",
                                "default": "",
                                "read_only": False
                            },
                            "pass_through": {
                                "type": "TOGGLE",
                                "value": True,
                                "default": True,
                                "read_only": False
                            }
                        },
                        "inputs": [
                            {
                                "index": 0,
                                "name": "input",
                                "data_type": "List[str]",
                                "connected": False
                            }
                        ],
                        "outputs": [
                            {
                                "index": 0,
                                "name": "output",
                                "data_type": "List[str]",
                                "connection_count": 1
                            }
                        ],
                        "errors": [],
                        "warnings": [],
                        "position": [100.0, 200.0],
                        "color": [1.0, 1.0, 1.0],
                        "selected": False,
                        "is_time_dependent": False,
                        "cook_count": 5,
                        "last_cook_time": 0.023
                    }
                }
            }
        },
        404: {
            "description": "Node not found",
            "model": ErrorResponse
        }
    }
)
def get_node(
    session_id: int = Path(..., description="Unique session ID of the node")
) -> NodeResponse:
    """
    Get detailed information about a specific node.
    
    Retrieves complete node state including all parameters, connections,
    errors, warnings, and UI properties.
    
    Args:
        session_id: The unique session identifier for the node
        
    Returns:
        NodeResponse: Complete node information
        
    Raises:
        HTTPException: 404 if node with given session_id not found
    """
    # Find node by session_id
    all_node_paths = NodeEnvironment.list_nodes()
    target_node = None
    
    for path in all_node_paths:
        node = NodeEnvironment.node_from_name(path)
        if node and node.session_id() == session_id:
            target_node = node
            break
    
    if not target_node:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "node_not_found",
                "message": f"Node with session_id {session_id} does not exist",
                "session_id": session_id
            }
        )
    
    try:
        return node_to_response(target_node)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error retrieving node details: {str(e)}",
                "session_id": session_id
            }
        )