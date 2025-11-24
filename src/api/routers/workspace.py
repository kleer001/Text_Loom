"""
TextLoom API - Workspace Endpoints

Handles workspace-related API operations:
- Get complete workspace state (nodes, connections, globals)
- Export workspace to flowstate format
- Import workspace from flowstate format
- Clear workspace
"""

import logging
import tempfile
import json
import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from api.models import WorkspaceState, NodeResponse, ConnectionResponse, SuccessResponse, node_to_response, connection_to_response
from api.router_utils import raise_http_error
from core.base_classes import NodeEnvironment, NodeType
from core.global_store import GlobalStore
from core.flowstate_manager import save_flowstate, load_flowstate, NODE_ATTRIBUTES
from core.undo_manager import UndoManager

logger = logging.getLogger("api.routers.workspace")
router = APIRouter()


class UndoStatusResponse(BaseModel):
    can_undo: bool
    can_redo: bool
    undo_description: str
    redo_description: str


class UndoRedoResponse(BaseModel):
    success: bool
    operation: str
    message: str


def migrate_node_attributes():
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if not node:
            continue

        for attr in NODE_ATTRIBUTES:
            public_attr = getattr(node, attr, None)
            if public_attr is None or callable(public_attr):
                continue

            if hasattr(node, f'_{attr}'):
                setattr(node, f'_{attr}', public_attr)
                delattr(node, attr)

        if isinstance(node._node_type, str):
            node._node_type = getattr(NodeType, node._node_type.split('.')[-1].upper())


def collect_all_nodes() -> list[NodeResponse]:
    nodes = []
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if node:
            try:
                nodes.append(node_to_response(node))
            except Exception as e:
                logger.error(f"Error converting node {path}: {e}")
    return nodes


def collect_all_connections() -> list[ConnectionResponse]:
    connections_set = set()
    connections = []

    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if not node:
            continue

        for output_idx, output_connections in node._outputs.items():
            for conn in output_connections:
                conn_id = (
                    conn.output_node().path(),
                    conn.output_index(),
                    conn.input_node().path(),
                    conn.input_index()
                )

                if conn_id not in connections_set:
                    connections_set.add(conn_id)
                    try:
                        connections.append(connection_to_response(conn))
                    except Exception as e:
                        logger.error(f"Error converting connection {conn_id}: {e}")

    return connections


def save_workspace_to_temp_file() -> str:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tl', delete=False) as tmp:
        tmp_path = tmp.name

    if not save_flowstate(tmp_path):
        raise Exception("Failed to save flowstate to temporary file")

    return tmp_path


def load_workspace_from_temp_file(flowstate_data: Dict[str, Any]) -> str:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tl', delete=False) as tmp:
        json.dump(flowstate_data, tmp, indent=2)
        return tmp.name


def read_and_cleanup_temp_file(tmp_path: str) -> Dict[str, Any]:
    try:
        with open(tmp_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    finally:
        os.unlink(tmp_path)


def clear_all_globals():
    global_store = GlobalStore()
    for key in list(global_store.list().keys()):
        global_store.delete(key)


@router.get(
    "/workspace",
    response_model=WorkspaceState,
    summary="Get complete workspace state",
    description="Returns the entire workspace including all nodes, connections, and global variables.",
)
def get_workspace() -> WorkspaceState:
    try:
        return WorkspaceState(
            nodes=collect_all_nodes(),
            connections=collect_all_connections(),
            globals=GlobalStore.list()
        )
    except Exception as e:
        raise_http_error(500, "internal_error", f"Error retrieving workspace state: {str(e)}")


@router.get(
    "/workspace/export",
    summary="Export workspace as flowstate JSON",
    description="Exports the current workspace to Text Loom flowstate format (JSON).",
)
def export_workspace() -> JSONResponse:
    try:
        tmp_path = save_workspace_to_temp_file()
        flowstate_data = read_and_cleanup_temp_file(tmp_path)
        return JSONResponse(content=flowstate_data)
    except Exception as e:
        raise_http_error(500, "export_failed", f"Error exporting workspace: {str(e)}")


@router.post(
    "/workspace/import",
    response_model=SuccessResponse,
    summary="Import workspace from flowstate JSON",
    description="Imports a workspace from Text Loom flowstate format (JSON). Clears current workspace first.",
)
def import_workspace(flowstate_data: Dict[str, Any] = Body(...)) -> SuccessResponse:
    try:
        tmp_path = load_workspace_from_temp_file(flowstate_data)

        success = load_flowstate(tmp_path)
        os.unlink(tmp_path)

        if not success:
            raise Exception("Failed to load flowstate from data")

        migrate_node_attributes()
        return SuccessResponse(success=True, message="Workspace imported successfully")

    except Exception as e:
        raise_http_error(500, "import_failed", f"Error importing workspace: {str(e)}")


@router.post(
    "/workspace/clear",
    response_model=SuccessResponse,
    summary="Clear the entire workspace",
    description="Deletes all nodes, connections, and global variables.",
)
def clear_workspace() -> SuccessResponse:
    try:
        NodeEnvironment.nodes.clear()
        clear_all_globals()
        return SuccessResponse(success=True, message="Workspace cleared successfully")
    except Exception as e:
        raise_http_error(500, "clear_failed", f"Error clearing workspace: {str(e)}")


@router.get(
    "/workspace/undo-status",
    response_model=UndoStatusResponse,
    summary="Get undo/redo status",
    description="Returns whether undo and redo operations are available, along with descriptions.",
)
def get_undo_status() -> UndoStatusResponse:
    try:
        undo_mgr = UndoManager()

        can_undo = len(undo_mgr.undo_stack) > 0
        can_redo = len(undo_mgr.redo_stack) > 0

        undo_desc = undo_mgr.undo_stack[-1][0] if can_undo else ""
        redo_desc = undo_mgr.redo_stack[-1][0] if can_redo else ""

        return UndoStatusResponse(
            can_undo=can_undo,
            can_redo=can_redo,
            undo_description=undo_desc,
            redo_description=redo_desc
        )

    except Exception as e:
        raise_http_error(500, "internal_error", f"Error getting undo status: {str(e)}")


@router.post(
    "/workspace/undo",
    response_model=UndoRedoResponse,
    summary="Undo last operation",
    description="Undoes the most recent operation in the workspace.",
)
def undo_operation() -> UndoRedoResponse:
    try:
        undo_mgr = UndoManager()

        if len(undo_mgr.undo_stack) == 0:
            return UndoRedoResponse(success=False, operation="", message="Nothing to undo")

        operation_name = undo_mgr.undo()
        return UndoRedoResponse(success=True, operation=operation_name or "", message="Undo completed")

    except Exception as e:
        raise_http_error(500, "undo_failed", f"Error performing undo: {str(e)}")


@router.post(
    "/workspace/redo",
    response_model=UndoRedoResponse,
    summary="Redo last undone operation",
    description="Redoes the most recently undone operation.",
)
def redo_operation() -> UndoRedoResponse:
    try:
        undo_mgr = UndoManager()

        if len(undo_mgr.redo_stack) == 0:
            return UndoRedoResponse(success=False, operation="", message="Nothing to redo")

        operation_name = undo_mgr.redo()
        return UndoRedoResponse(success=True, operation=operation_name or "", message="Redo completed")

    except Exception as e:
        raise_http_error(500, "redo_failed", f"Error performing redo: {str(e)}")


@router.post(
    "/workspace/undo/disable",
    response_model=SuccessResponse,
    summary="Disable undo tracking",
    description="Temporarily disables undo state tracking. Used during batch operations.",
)
def disable_undo() -> SuccessResponse:
    try:
        UndoManager().disable()
        return SuccessResponse(success=True, message="Undo tracking disabled")
    except Exception as e:
        raise_http_error(500, "disable_failed", f"Error disabling undo: {str(e)}")


@router.post(
    "/workspace/undo/enable",
    response_model=SuccessResponse,
    summary="Enable undo tracking",
    description="Re-enables undo state tracking after being disabled.",
)
def enable_undo() -> SuccessResponse:
    try:
        UndoManager().enable()
        return SuccessResponse(success=True, message="Undo tracking enabled")
    except Exception as e:
        raise_http_error(500, "enable_failed", f"Error enabling undo: {str(e)}")
