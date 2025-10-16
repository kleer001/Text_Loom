"""
TextLoom API - Workspace Endpoints

Handles workspace-related API operations:
- Get complete workspace state (nodes, connections, globals)
"""

from fastapi import APIRouter, HTTPException
from api.models import WorkspaceState, NodeResponse, ConnectionResponse, node_to_response, connection_to_response
from core.base_classes import NodeEnvironment
from core.global_store import GlobalStore

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