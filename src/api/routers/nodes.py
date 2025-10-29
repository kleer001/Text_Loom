"""
TextLoom API - Node Endpoints

Handles node-related API operations:
- List all nodes
- Get single node details
- Create new nodes
- Update existing nodes
- Delete nodes
- Execute nodes
"""

from typing import List
import time
from fastapi import APIRouter, HTTPException, Path, Body, status
from api.models import (
    NodeResponse,
    NodeCreateRequest,
    NodeUpdateRequest,
    ExecutionResponse,
    ErrorResponse,
    SuccessResponse,
    node_to_response
)
from core.base_classes import Node, NodeType, NodeEnvironment, NodeState
from core.enums import generate_node_types
from core.undo_manager import UndoManager

import logging
logger = logging.getLogger("api.routers.nodes")

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
                            "state": "UNCHANGED",
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
                        "state": "UNCHANGED",
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

    return node_to_response(target_node)


@router.post(
    "/nodes",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new node",
    description="Creates a new node of the specified type. Name collisions are automatically handled by the backend.",
    responses={
        201: {"description": "Node created successfully"},
        400: {"description": "Invalid request", "model": ErrorResponse}
    }
)
def create_node(request: 'NodeCreateRequest') -> 'NodeResponse':
    """
    Create a new node with enhanced logging.
    
    The backend automatically handles name collisions by appending _1, _2, etc.
    The response includes the actual name and path assigned to the node.
    
    Node type must match enum names exactly (case-insensitive).
    Use underscores: "file_out" not "fileout", "make_list" not "makelist".
    
    Args:
        request: Node creation parameters
        
    Returns:
        NodeResponse: Complete details of the created node
        
    Raises:
        HTTPException: 400 if node type is invalid or creation fails
    """
    from fastapi import HTTPException, status
    from api.models import node_to_response
    from core.base_classes import Node, NodeType
    from core.node_environment import generate_node_types
    
    logger.info(f"Creating node: type={request.type}, name={request.name}, parent={request.parent_path}")
    
    # Get available node types dynamically
    available_types = generate_node_types()
    valid_type_names = list(available_types.keys())
    
    # Convert to uppercase for enum lookup
    node_type_str = request.type.upper()
    
    # Check if type exists
    if node_type_str not in valid_type_names:
        logger.warning(f"Invalid node type: {request.type}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_node_type",
                "message": f"Unknown node type: '{request.type}'. Use underscores in type names (e.g., 'file_out' not 'fileout').",
                "valid_types": [name.lower() for name in valid_type_names]
            }
        )
    
    try:
        # Get the NodeType enum value
        node_type = getattr(NodeType, node_type_str)
        logger.debug(f"  Resolved NodeType: {node_type}")
        
        # Create the node (backend handles name collisions)
        logger.debug(f"  Calling Node.create_node()")
        node = Node.create_node(
            node_type=node_type,
            node_name=request.name,
            parent_path=request.parent_path
        )
        
        logger.info(f"  Node created: path={node.path()}, session_id={node.session_id()}")
        logger.debug(f"  Node has _parms: {hasattr(node, '_parms')}")
        logger.debug(f"  Node has _inputs: {hasattr(node, '_inputs')}")
        logger.debug(f"  Node has _outputs: {hasattr(node, '_outputs')}")

        # Set initial position if provided
        if request.position:
            node._position = tuple(request.position)
            logger.debug(f"  Position set: {request.position}")

        # Convert to response
        logger.debug(f"  Converting node to response")
        response = node_to_response(node)

        logger.info(f"  Successfully created node {node.path()} with session_id {node.session_id()} (type: {type(node.session_id())})")
        logger.info(f"  Response session_id: {response.session_id} (type: {type(response.session_id)})")
        logger.info(f"  Node is in NodeEnvironment: {node.path() in NodeEnvironment.nodes}")
        return response
        
    except ValueError as e:
        logger.error(f"ValueError creating node: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Exception creating node: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to create node: {str(e)}"
            }
        )




@router.put(
    "/nodes/{session_id}",
    response_model=NodeResponse,
    summary="Update a node",
    description="Updates node parameters and/or UI state. Only provided fields are updated (partial update).",
    responses={
        200: {"description": "Node updated successfully"},
        404: {"description": "Node not found", "model": ErrorResponse},
        400: {"description": "Invalid request", "model": ErrorResponse}
    }
)
def update_node(
    session_id: int,
    request: NodeUpdateRequest = Body(...)
) -> NodeResponse:
    """
    Update an existing node.

    Supports partial updates - only the provided fields are modified.
    Can update parameters, position, color, and selection state.

    Args:
        session_id: The unique session identifier for the node
        request: Update parameters

    Returns:
        NodeResponse: Updated node details

    Raises:
        HTTPException: 404 if node not found, 400 if update invalid
    """
    logger.info(f"[UPDATE_NODE] === START UPDATE REQUEST ===")
    logger.info(f"[UPDATE_NODE] Incoming session_id={session_id}, type={type(session_id)}")
    logger.info(f"[UPDATE_NODE] Request: {request}")
    if request.position is not None:
        logger.info(f"[UPDATE_NODE] Position update requested: {request.position}")

    # Find the node with enhanced logging
    target_node = None
    all_paths = NodeEnvironment.list_nodes()
    logger.info(f"[UPDATE_NODE] Searching through {len(all_paths)} nodes for session_id={session_id}")
    logger.debug(f"[UPDATE_NODE] session_id type: {type(session_id)}, value: {session_id}")

    for path in all_paths:
        node = NodeEnvironment.node_from_name(path)
        if node:
            node_sid = node.session_id()
            logger.debug(f"[UPDATE_NODE] Checking node {path}: session_id={node_sid} (type: {type(node_sid)})")
            if node_sid == session_id:
                target_node = node
                logger.info(f"[UPDATE_NODE] ✓ Found matching node at {path}")
                logger.info(f"[UPDATE_NODE] ✓ Node session_id={node_sid} matches requested={session_id}")
                logger.info(f"[UPDATE_NODE] ✓ Current node position: {node._position}")
                break

    if not target_node:
        logger.warning(f"Node with session_id {session_id} not found")
        logger.warning(f"  Available nodes and their session_ids:")
        for path in all_paths[:10]:  # Log first 10 nodes to avoid spam
            node = NodeEnvironment.node_from_name(path)
            if node:
                logger.warning(f"    {path}: session_id={node.session_id()}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "node_not_found",
                "message": f"Node with session_id {session_id} does not exist"
            }
        )

    # Build undo operation description
    undo_parts = []
    if request.position is not None:
        undo_parts.append("position")
    if request.parameters:
        undo_parts.append("parameters")
    if request.color is not None:
        undo_parts.append("color")
    if request.selected is not None:
        undo_parts.append("selection")

    undo_description = f"Update {target_node.name()} ({', '.join(undo_parts)})"
    logger.info(f"[UPDATE_NODE] Pushing undo state: {undo_description}")
    UndoManager().push_state(undo_description)

    # Disable undo during updates to prevent parm.set() from pushing duplicate states
    UndoManager().disable()
    try:
        # Update parameters if provided
        if request.parameters:
            for param_name, param_value in request.parameters.items():
                if param_name in target_node._parms:
                    target_node._parms[param_name].set(param_value)
                else:
                    raise ValueError(f"Unknown parameter: {param_name}")

        # Update UI state if provided
        if request.position is not None:
            old_position = target_node._position
            logger.info(f"[UPDATE_NODE] Updating position: {old_position} -> {request.position}")
            target_node._position = tuple(request.position)
            logger.info(f"[UPDATE_NODE] Position updated. New position: {target_node._position}")

        if request.color is not None:
            logger.debug(f"[UPDATE_NODE] Updating color to {request.color}")
            target_node._color = tuple(request.color)

        if request.selected is not None:
            logger.debug(f"[UPDATE_NODE] Updating selected to {request.selected}")
            target_node._selected = request.selected

        logger.info(f"[UPDATE_NODE] Successfully updated node {target_node.path()}")
        logger.info(f"[UPDATE_NODE] Node session_id before response: {target_node.session_id()}")

        response = node_to_response(target_node)

        logger.info(f"[UPDATE_NODE] Response generated:")
        logger.info(f"[UPDATE_NODE]   - session_id: {response.session_id}")
        logger.info(f"[UPDATE_NODE]   - position: {response.position}")
        logger.info(f"[UPDATE_NODE] === END UPDATE REQUEST ===")

        return response
        
    except ValueError as e:
        logger.error(f"ValueError updating node: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_parameter",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Exception updating node: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to update node: {str(e)}"
            }
        )
    finally:
        # Re-enable undo system
        UndoManager().enable()


@router.delete(
    "/nodes/{session_id}",
    response_model=SuccessResponse,
    summary="Delete a node",
    description="Deletes a node and automatically removes all its connections.",
    responses={
        200: {"description": "Node deleted successfully"},
        404: {"description": "Node not found", "model": ErrorResponse}
    }
)
def delete_node(
    session_id: int = Path(..., description="Node session ID")
) -> SuccessResponse:
    """
    Delete a node.
    
    The node's destroy() method automatically handles disconnecting all
    input and output connections before removal.
    
    Args:
        session_id: The unique session identifier for the node
        
    Returns:
        SuccessResponse: Confirmation of deletion
        
    Raises:
        HTTPException: 404 if node not found
    """
    # Find the node
    target_node = None
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if node and node.session_id() == session_id:
            target_node = node
            break
    
    if not target_node:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "node_not_found",
                "message": f"Node with session_id {session_id} does not exist"
            }
        )
    
    try:
        node_name = target_node.name()
        node_path = target_node.path()
        
        # Destroy the node (handles all connections automatically)
        target_node.destroy()
        
        return SuccessResponse(
            success=True,
            message=f"Node '{node_name}' at {node_path} deleted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to delete node: {str(e)}"
            }
        )


@router.post(
    "/nodes/{session_id}/execute",
    response_model=ExecutionResponse,
    summary="Execute/cook a node",
    description="Executes a node, cooking it and all its dependencies. Returns execution results and updated state.",
    responses={
        200: {"description": "Execution completed (check success field for result)"},
        404: {"description": "Node not found", "model": ErrorResponse}
    }
)
def execute_node(
    session_id: int = Path(..., description="Node session ID")
) -> ExecutionResponse:
    """
    Execute a node (cook it).
    
    Triggers the node's eval() method, which cooks the node and all its
    dependencies. Returns execution results including any output data,
    errors, and performance metrics.
    
    Note: Even if execution fails, returns HTTP 200 with success=false.
    This distinguishes between HTTP errors and domain execution errors.
    
    Args:
        session_id: The unique session identifier for the node
        
    Returns:
        ExecutionResponse: Execution results including output data and status
        
    Raises:
        HTTPException: 404 if node not found
    """
    # Find the node
    target_node = None
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if node and node.session_id() == session_id:
            target_node = node
            break
    
    if not target_node:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "node_not_found",
                "message": f"Node with session_id {session_id} does not exist"
            }
        )
    
    try:
        # Record start time
        start_time = time.time()
        
        # Execute the node
        output_data = target_node.eval()
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Determine success based on node state and errors
        success = (target_node._state in [NodeState.UNCHANGED, NodeState.COOKED] 
                   and len(target_node._errors) == 0)
        
        # Prepare output data (handle single vs multiple outputs)
        output_list = None
        if output_data is not None:
            if isinstance(output_data, list):
                # Check if it's a list of lists (multi-output) or just list of strings
                if output_data and isinstance(output_data[0], list):
                    output_list = output_data  # Multi-output node
                else:
                    output_list = [output_data]  # Single output, wrap it
            else:
                output_list = [[str(output_data)]]  # Fallback
        
        message = "Execution completed successfully" if success else "Execution completed with errors"
        
        return ExecutionResponse(
            success=success,
            message=message,
            output_data=output_list,
            execution_time=execution_time,
            node_state=NodeState(target_node._state),
            errors=list(target_node._errors),
            warnings=list(target_node._warnings)
        )
        
    except Exception as e:
        # Execution threw an exception
        return ExecutionResponse(
            success=False,
            message=f"Execution failed with exception: {str(e)}",
            output_data=None,
            execution_time=0.0,
            node_state=NodeState.UNCOOKED,
            errors=[str(e)],
            warnings=[]
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