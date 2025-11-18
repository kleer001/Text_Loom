"""
TextLoom API - Workspace Endpoints

Handles workspace-related API operations:
- Get complete workspace state (nodes, connections, globals)
- Export workspace to flowstate format
- Import workspace from flowstate format
- Clear workspace
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from api.models import WorkspaceState, NodeResponse, ConnectionResponse, SuccessResponse, node_to_response, connection_to_response
from core.base_classes import NodeEnvironment
from core.global_store import GlobalStore
from core.flowstate_manager import save_flowstate, load_flowstate
from core.undo_manager import UndoManager
from typing import Dict, Any
from pydantic import BaseModel
import tempfile
import json
import os


class UndoStatusResponse(BaseModel):
    """Response model for undo/redo status."""
    can_undo: bool
    can_redo: bool
    undo_description: str
    redo_description: str


class UndoRedoResponse(BaseModel):
    """Response model for undo/redo operations."""
    success: bool
    operation: str
    message: str

router = APIRouter()


@router.get(
    "/workspace",
    response_model=WorkspaceState,
    summary="Get complete workspace state",
    description="Returns the entire workspace including all nodes, connections, and global variables.",
    responses={
        200: {
            "description": "Complete workspace state",
            "content": {
                "application/json": {
                    "example": {
                        "nodes": [
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
                        ],
                        "connections": [
                            {
                                "source_node_session_id": 123456789,
                                "source_node_path": "/text1",
                                "source_output_index": 0,
                                "source_output_name": "output",
                                "target_node_session_id": 987654321,
                                "target_node_path": "/fileout1",
                                "target_input_index": 0,
                                "target_input_name": "input"
                            }
                        ],
                        "globals": {
                            "LASTRUN": "2024-10-14",
                            "PROJECT_NAME": "My Project"
                        }
                    }
                }
            }
        }
    }
)
def get_workspace() -> WorkspaceState:
    """
    Get complete workspace state.
    
    Returns all nodes, connections, and global variables in the current
    workspace. This is typically called on frontend initialization to
    reconstruct the full workspace state.
    
    Returns:
        WorkspaceState: Complete workspace including:
            - nodes: All nodes with full details
            - connections: All connections between nodes
            - globals: All global variables
    """
    try:
        # Get all nodes
        all_node_paths = NodeEnvironment.list_nodes()
        nodes = []
        
        for path in all_node_paths:
            node = NodeEnvironment.node_from_name(path)
            if node:
                try:
                    node_response = node_to_response(node)
                    nodes.append(node_response)
                except Exception as e:
                    print(f"Error converting node {path}: {e}")
                    continue
        
        # Get all connections (deduplicated)
        # Strategy: iterate through all nodes' outputs to build connection list
        connections_set = set()
        connections = []
        
        for path in all_node_paths:
            node = NodeEnvironment.node_from_name(path)
            if not node:
                continue
            
            # Iterate through all output indices
            for output_idx, output_connections in node._outputs.items():
                # Each output can have multiple connections
                for conn in output_connections:
                    # Use a tuple as unique identifier to deduplicate
                    conn_id = (
                        conn.output_node().path(),
                        conn.output_index(),
                        conn.input_node().path(),
                        conn.input_index()
                    )
                    
                    if conn_id not in connections_set:
                        connections_set.add(conn_id)
                        try:
                            conn_response = connection_to_response(conn)
                            connections.append(conn_response)
                        except Exception as e:
                            print(f"Error converting connection {conn_id}: {e}")
                            continue
        
        # Get global variables
        globals_dict = GlobalStore.list()
        
        return WorkspaceState(
            nodes=nodes,
            connections=connections,
            globals=globals_dict
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error retrieving workspace state: {str(e)}"
            }
        )


@router.get(
    "/workspace/export",
    summary="Export workspace as flowstate JSON",
    description="Exports the current workspace to Text Loom flowstate format (JSON). Used for file downloads.",
    responses={
        200: {
            "description": "Workspace exported successfully",
            "content": {"application/json": {}}
        }
    }
)
def export_workspace() -> JSONResponse:
    """
    Export the current workspace to flowstate JSON format.

    Creates a temporary file, saves the workspace using flowstate_manager,
    then returns the JSON content for download by the frontend.

    Returns:
        JSONResponse: The flowstate JSON data
    """
    try:
        # Create a temporary file to save the flowstate
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tl', delete=False) as tmp:
            tmp_path = tmp.name

        # Save current workspace to temp file
        success = save_flowstate(tmp_path)
        if not success:
            raise Exception("Failed to save flowstate to temporary file")

        # Read the JSON back
        with open(tmp_path, 'r', encoding='utf-8') as f:
            flowstate_data = json.load(f)

        # Clean up temp file
        os.unlink(tmp_path)

        return JSONResponse(content=flowstate_data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "export_failed",
                "message": f"Error exporting workspace: {str(e)}"
            }
        )


@router.post(
    "/workspace/import",
    response_model=SuccessResponse,
    summary="Import workspace from flowstate JSON",
    description="Imports a workspace from Text Loom flowstate format (JSON). Clears current workspace first.",
    responses={
        200: {
            "description": "Workspace imported successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Workspace imported successfully"
                    }
                }
            }
        }
    }
)
def import_workspace(flowstate_data: Dict[str, Any] = Body(...)) -> SuccessResponse:
    """
    Import a workspace from flowstate JSON format.

    Accepts the flowstate JSON data, saves it to a temporary file,
    then loads it using the flowstate_manager.

    Args:
        flowstate_data: The flowstate JSON data (entire file contents)

    Returns:
        SuccessResponse: Success confirmation
    """
    try:
        # Create a temporary file with the flowstate data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tl', delete=False) as tmp:
            json.dump(flowstate_data, tmp, indent=2)
            tmp_path = tmp.name

        # Load the flowstate from temp file
        success = load_flowstate(tmp_path)

        # Clean up temp file
        os.unlink(tmp_path)

        if not success:
            raise Exception("Failed to load flowstate from data")

        return SuccessResponse(
            success=True,
            message="Workspace imported successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "import_failed",
                "message": f"Error importing workspace: {str(e)}"
            }
        )


@router.post(
    "/workspace/clear",
    response_model=SuccessResponse,
    summary="Clear the entire workspace",
    description="Deletes all nodes, connections, and global variables. Used for 'New Workspace'.",
    responses={
        200: {
            "description": "Workspace cleared successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Workspace cleared successfully"
                    }
                }
            }
        }
    }
)
def clear_workspace() -> SuccessResponse:
    """
    Clear the entire workspace.

    Removes all nodes, connections, and global variables.
    This is used when creating a new workspace.

    Returns:
        SuccessResponse: Success confirmation
    """
    try:
        # Clear all nodes
        NodeEnvironment.nodes.clear()

        # Clear global variables
        global_store = GlobalStore()
        for key in list(global_store.list().keys()):
            global_store.delete(key)

        return SuccessResponse(
            success=True,
            message="Workspace cleared successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "clear_failed",
                "message": f"Error clearing workspace: {str(e)}"
            }
        )


@router.get(
    "/workspace/undo-status",
    response_model=UndoStatusResponse,
    summary="Get undo/redo status",
    description="Returns whether undo and redo operations are available, along with descriptions.",
    responses={
        200: {
            "description": "Undo/redo status",
            "content": {
                "application/json": {
                    "example": {
                        "can_undo": True,
                        "can_redo": False,
                        "undo_description": "Update text1 (parameters)",
                        "redo_description": ""
                    }
                }
            }
        }
    }
)
def get_undo_status() -> UndoStatusResponse:
    """
    Get the current undo/redo status.

    Returns whether undo and redo operations are available,
    along with descriptions of what would be undone/redone.

    Returns:
        UndoStatusResponse: Undo/redo availability and descriptions
    """
    try:
        undo_mgr = UndoManager()

        can_undo = len(undo_mgr.undo_stack) > 0
        can_redo = len(undo_mgr.redo_stack) > 0

        # Get the most recent operation names
        undo_desc = ""
        redo_desc = ""

        if can_undo:
            undo_desc = undo_mgr.undo_stack[-1][0]  # operation name
        if can_redo:
            redo_desc = undo_mgr.redo_stack[-1][0]  # operation name

        return UndoStatusResponse(
            can_undo=can_undo,
            can_redo=can_redo,
            undo_description=undo_desc,
            redo_description=redo_desc
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error getting undo status: {str(e)}"
            }
        )


@router.post(
    "/workspace/undo",
    response_model=UndoRedoResponse,
    summary="Undo last operation",
    description="Undoes the most recent operation in the workspace.",
    responses={
        200: {
            "description": "Undo completed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "operation": "Update text1 (parameters)",
                        "message": "Undo completed"
                    }
                }
            }
        }
    }
)
def undo_operation() -> UndoRedoResponse:
    """
    Undo the most recent operation.

    Restores the workspace to its previous state before the last operation.

    Returns:
        UndoRedoResponse: Result of the undo operation
    """
    try:
        undo_mgr = UndoManager()

        if len(undo_mgr.undo_stack) == 0:
            return UndoRedoResponse(
                success=False,
                operation="",
                message="Nothing to undo"
            )

        operation_name = undo_mgr.undo()

        return UndoRedoResponse(
            success=True,
            operation=operation_name or "",
            message="Undo completed"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "undo_failed",
                "message": f"Error performing undo: {str(e)}"
            }
        )


@router.post(
    "/workspace/redo",
    response_model=UndoRedoResponse,
    summary="Redo last undone operation",
    description="Redoes the most recently undone operation.",
    responses={
        200: {
            "description": "Redo completed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "operation": "Update text1 (parameters)",
                        "message": "Redo completed"
                    }
                }
            }
        }
    }
)
def redo_operation() -> UndoRedoResponse:
    """
    Redo the most recently undone operation.

    Restores the workspace to its state after the undone operation.

    Returns:
        UndoRedoResponse: Result of the redo operation
    """
    try:
        undo_mgr = UndoManager()

        if len(undo_mgr.redo_stack) == 0:
            return UndoRedoResponse(
                success=False,
                operation="",
                message="Nothing to redo"
            )

        operation_name = undo_mgr.redo()

        return UndoRedoResponse(
            success=True,
            operation=operation_name or "",
            message="Redo completed"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "redo_failed",
                "message": f"Error performing redo: {str(e)}"
            }
        )