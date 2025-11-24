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

import logging
import time
from typing import List
from fastapi import APIRouter, HTTPException, Path, Body, status
from api.models import (
    NodeResponse,
    NodeCreateRequest,
    NodeUpdateRequest,
    ExecutionResponse,
    ErrorResponse,
    SuccessResponse,
    NodeTypeInfo,
    node_to_response
)
from api.router_utils import find_node_by_session_id, raise_http_error
from core.base_classes import Node, NodeType, NodeEnvironment, NodeState
from core.enums import generate_node_types
from core.undo_manager import UndoManager
from core.internal_path import InternalPath
from utils.node_loader import discover_node_types

logger = logging.getLogger("api.routers.nodes")
router = APIRouter()


def create_node_type_info(node_type_id: str, node_class) -> NodeTypeInfo:
    label = node_type_id.replace('_', ' ').title()
    return NodeTypeInfo(
        id=node_type_id,
        label=label,
        glyph=node_class.GLYPH
    )


def collect_node_responses(paths: List[str]) -> List[NodeResponse]:
    nodes = []
    for path in paths:
        node = NodeEnvironment.node_from_name(path)
        if node:
            try:
                nodes.append(node_to_response(node))
            except Exception as e:
                logger.error(f"Error converting node {path}: {e}")
    return nodes


def find_child_nodes(parent_path: str) -> List[Node]:
    children = []
    for path in NodeEnvironment.list_nodes():
        if path.startswith(parent_path + '/'):
            child_node = NodeEnvironment.node_from_name(path)
            if child_node:
                children.append(child_node)
    return children


def validate_child_path_updates(target_node: Node, sanitized_name: str) -> List[tuple]:
    old_path = target_node.path()
    current_path_parent = str(target_node._path.parent())
    hypothetical_new_path = f"{current_path_parent.rstrip('/')}/{sanitized_name}"

    children = [
        NodeEnvironment.node_from_name(p)
        for p in NodeEnvironment.list_nodes()
        if p.startswith(old_path + '/')
    ]

    child_updates = []
    for child in children:
        if child:
            old_child_path = child.path()
            relative_path = old_child_path[len(old_path):]
            new_child_path = hypothetical_new_path + relative_path

            try:
                InternalPath(new_child_path)
            except Exception as e:
                raise ValueError(f"Cannot rename: child path '{new_child_path}' is invalid: {e}")

            child_updates.append((child, old_child_path, relative_path))

    return child_updates


def apply_child_path_updates(new_parent_path: str, child_updates: List[tuple]) -> List[Node]:
    affected_nodes = []
    for child, old_child_path, relative_path in child_updates:
        new_child_path = new_parent_path + relative_path

        child._path = InternalPath(new_child_path)
        child._name = new_child_path.split('/')[-1]

        if old_child_path in NodeEnvironment.nodes:
            del NodeEnvironment.nodes[old_child_path]
        NodeEnvironment.nodes[new_child_path] = child

        affected_nodes.append(child)

    return affected_nodes


def update_node_parameters(node: Node, parameters: dict):
    for param_name, param_value in parameters.items():
        if param_name in node._parms:
            node._parms[param_name].set(param_value)
        else:
            raise ValueError(f"Unknown parameter: {param_name}")


def prepare_execution_output(output_data) -> List[List[str]] | None:
    if output_data is None:
        return None

    if isinstance(output_data, list):
        if output_data and isinstance(output_data[0], list):
            return output_data
        return [output_data]

    return [[str(output_data)]]


def determine_execution_success(node: Node) -> bool:
    return (node._state in [NodeState.UNCHANGED, NodeState.COOKED]
            and len(node._errors) == 0)


@router.get(
    "/node-types",
    response_model=List[NodeTypeInfo],
    summary="Get available node types",
    description="Returns a list of all available node types with their glyphs and labels.",
)
def get_node_types() -> List[NodeTypeInfo]:
    node_type_map = discover_node_types()
    node_types = [
        create_node_type_info(node_type_id, node_class)
        for node_type_id, node_class in node_type_map.items()
    ]
    node_types.sort(key=lambda x: x.id)
    return node_types


@router.get(
    "/nodes",
    response_model=List[NodeResponse],
    summary="List all nodes",
    description="Returns a list of all nodes in the current workspace with full details.",
)
def list_nodes() -> List[NodeResponse]:
    return collect_node_responses(NodeEnvironment.list_nodes())


@router.get(
    "/nodes/{session_id}",
    response_model=NodeResponse,
    summary="Get node by session ID",
    description="Returns detailed information about a specific node identified by its unique session ID.",
    responses={
        404: {"description": "Node not found", "model": ErrorResponse}
    }
)
def get_node(session_id: str = Path(..., description="Unique session ID of the node")) -> NodeResponse:
    return node_to_response(find_node_by_session_id(session_id))


@router.post(
    "/nodes",
    response_model=List[NodeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new node",
    description="Creates a new node of the specified type. For loopers, returns the looper and its child nodes.",
    responses={
        201: {"description": "Node(s) created successfully"},
        400: {"description": "Invalid request", "model": ErrorResponse}
    }
)
def create_node(request: NodeCreateRequest) -> List[NodeResponse]:
    available_types = generate_node_types()
    valid_type_names = list(available_types.keys())
    node_type_str = request.type.upper()

    if node_type_str not in valid_type_names:
        raise_http_error(
            400,
            "invalid_node_type",
            f"Unknown node type: '{request.type}'. Use underscores in type names.",
            valid_types=[name.lower() for name in valid_type_names]
        )

    try:
        node_type = getattr(NodeType, node_type_str)
        node = Node.create_node(
            node_type=node_type,
            node_name=request.name,
            parent_path=request.parent_path
        )

        if request.position:
            node._position = tuple(request.position)

        created_nodes = [node]
        if node_type == NodeType.LOOPER:
            created_nodes.extend(find_child_nodes(node.path()))

        responses = [node_to_response(n) for n in created_nodes]

        node_from_env = NodeEnvironment.node_from_name(node.path())
        if node_from_env and node_from_env.session_id() != responses[0].session_id:
            logger.error(f"SESSION_ID MISMATCH: Response={responses[0].session_id}, Env={node_from_env.session_id()}")

        return responses

    except ValueError as e:
        logger.error(f"ValueError creating node: {e}")
        raise_http_error(400, "invalid_request", str(e))
    except Exception as e:
        logger.error(f"Exception creating node: {type(e).__name__}: {e}")
        raise_http_error(500, "internal_error", f"Failed to create node: {str(e)}")


@router.put(
    "/nodes/{session_id}",
    response_model=List[NodeResponse],
    summary="Update a node",
    description="Updates node parameters and/or UI state. Returns the updated node and any affected children.",
    responses={
        200: {"description": "Node and affected children updated successfully"},
        404: {"description": "Node not found", "model": ErrorResponse},
        400: {"description": "Invalid request", "model": ErrorResponse}
    }
)
def update_node(session_id: str, request: NodeUpdateRequest = Body(...)) -> List[NodeResponse]:
    target_node = find_node_by_session_id(session_id)

    undo_parts = []
    if request.name is not None:
        undo_parts.append("name")
    if request.position is not None:
        undo_parts.append("position")
    if request.parameters:
        undo_parts.append("parameters")
    if request.color is not None:
        undo_parts.append("color")

    undo_description = f"Update {target_node.name()} ({', '.join(undo_parts)})"
    UndoManager().push_state(undo_description)
    UndoManager().disable()

    try:
        affected_nodes = [target_node]

        if request.name is not None:
            sanitized_name = Node.sanitize_node_name(request.name)
            if not sanitized_name:
                raise ValueError(f"Invalid node name: '{request.name}'")

            child_updates = validate_child_path_updates(target_node, sanitized_name)

            if not target_node.rename(sanitized_name):
                raise ValueError(f"Name '{sanitized_name}' is already in use")

            affected_nodes.extend(apply_child_path_updates(target_node.path(), child_updates))

        if request.parameters:
            update_node_parameters(target_node, request.parameters)

        if request.position is not None:
            target_node._position = tuple(request.position)

        if request.color is not None:
            target_node._color = tuple(request.color)

        return [node_to_response(node) for node in affected_nodes]

    except ValueError as e:
        logger.error(f"ValueError updating node: {e}")
        raise_http_error(400, "invalid_parameter", str(e))
    except Exception as e:
        logger.error(f"Exception updating node: {type(e).__name__}: {e}")
        raise_http_error(500, "internal_error", f"Failed to update node: {str(e)}")
    finally:
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
def delete_node(session_id: str = Path(..., description="Node session ID")) -> SuccessResponse:
    target_node = find_node_by_session_id(session_id)

    try:
        node_name = target_node.name()
        node_path = target_node.path()

        target_node.destroy()

        return SuccessResponse(
            success=True,
            message=f"Node '{node_name}' at {node_path} deleted successfully"
        )

    except Exception as e:
        raise_http_error(500, "internal_error", f"Failed to delete node: {str(e)}")


@router.post(
    "/nodes/{session_id}/execute",
    response_model=ExecutionResponse,
    summary="Execute/cook a node",
    description="Executes a node, cooking it and all its dependencies. Returns execution results and updated state.",
)
def execute_node(session_id: str = Path(..., description="Node session ID")) -> ExecutionResponse:
    target_node = find_node_by_session_id(session_id)

    try:
        start_time = time.time()
        output_data = target_node.eval()
        execution_time = (time.time() - start_time) * 1000

        success = determine_execution_success(target_node)
        output_list = prepare_execution_output(output_data)
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
        return ExecutionResponse(
            success=False,
            message=f"Execution failed with exception: {str(e)}",
            output_data=None,
            execution_time=0.0,
            node_state=NodeState.UNCOOKED,
            errors=[str(e)],
            warnings=[]
        )
