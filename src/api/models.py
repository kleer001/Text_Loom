"""
TextLoom API Data Transfer Objects (DTOs)

Pydantic models for the TextLoom web API. These models define the structure
of requests and responses, providing automatic validation and serialization.

Design Decisions:
- Uses session_id as unique node identifier
- Exposes raw parameter values (not evaluated expressions)
- Includes UI state (position, color, selected)
- Supports all node types uniformly
- Validates structure but delegates business logic to backend
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

import logging
from typing import Any
from typing import Union

# Set up logging
logger = logging.getLogger("api.patch")
logger.setLevel(logging.DEBUG)


# ============================================================================
# Enums
# ============================================================================

class NodeStateEnum(str, Enum):
    COOKING = "cooking"
    UNCHANGED = "unchanged"
    UNCOOKED = "uncooked"
    COOKED = "cooked"


# ============================================================================
# Parameter Models
# ============================================================================

class ParameterInfo(BaseModel):
    """
    Information about a single node parameter.
    
    Example:
        {
            "type": "STRING",
            "value": "Hello World",
            "default": "",
            "read_only": false
        }
    """
    type: str = Field(..., description="Parameter type: STRING, INT, FLOAT, TOGGLE, BUTTON, STRINGLIST")
    value: Any = Field(..., description="Current parameter value (raw, not evaluated)")
    default: Any = Field(..., description="Default value for this parameter")
    read_only: bool = Field(default=False, description="Whether this parameter is read-only (e.g., output values)")


# ============================================================================
# Input/Output Models
# ============================================================================


class InputInfo(BaseModel):
    """
    Information about a node's input socket.

    Example:
        {
            "index": 0,
            "name": "input",
            "data_type": "List[str]",
            "connected": true
        }
    """
    index: int = Field(..., description="Input index (integer)")
    name: str = Field(..., description="Display name of this input")
    data_type: str = Field(..., description="Expected data type")
    connected: bool = Field(..., description="Whether this input has a connection")


class OutputInfo(BaseModel):
    """
    Information about a node's output socket.

    Example:
        {
            "index": 0,
            "name": "output",
            "data_type": "List[str]",
            "connection_count": 2
        }
    """
    index: int = Field(..., description="Output index (integer)")
    name: str = Field(..., description="Display name of this output")
    data_type: str = Field(..., description="Output data type")
    connection_count: int = Field(default=0, description="Number of connections from this output")





# ============================================================================
# Node Models
# ============================================================================

class NodeResponse(BaseModel):
    """
    Complete node state for API responses.
    
    Example:
        {
            "session_id": 123456789,
            "name": "text1",
            "path": "/text1",
            "type": "text",
            "state": "UNCHANGED",
            "parameters": {
                "text_string": {
                    "type": "STRING",
                    "value": "Hello",
                    "default": "",
                    "read_only": false
                }
            },
            "inputs": [
                {
                    "index": 0,
                    "name": "input",
                    "data_type": "List[str]",
                    "connected": false
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
            "is_time_dependent": false,
            "cook_count": 5,
            "last_cook_time": 0.023
        }
    """
    # Core identification
    session_id: str = Field(..., description="Unique session identifier")
    name: str = Field(..., description="Node name (may not be unique)")
    path: str = Field(..., description="Full path (unique identifier)")
    type: str = Field(..., description="Node type (e.g., 'text', 'fileout', 'query')")
    glyph: str = Field(default="", description="Node type glyph character")
    group: str = Field(default="", description="Node functional group color (e.g., 'orange', 'grey', 'green', 'purple')")

    # Processing state
    state: NodeStateEnum = Field(..., description="Current processing state")
    errors: List[str] = Field(default_factory=list, description="Critical error messages")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warning messages")
    
    # Configuration
    parameters: Dict[str, ParameterInfo] = Field(default_factory=dict, description="Node parameters")
    inputs: List[InputInfo] = Field(default_factory=list, description="Input sockets")
    outputs: List[OutputInfo] = Field(default_factory=list, description="Output sockets")
    
    # UI state
    position: List[float] = Field(default=[0.0, 0.0], description="[x, y] position in editor")
    color: List[float] = Field(default=[1.0, 1.0, 1.0], description="[r, g, b] color (0-1 range)")

    # Performance metrics
    is_time_dependent: bool = Field(default=False, description="Whether node recooks on every eval")
    cook_count: int = Field(default=0, description="Number of times node has cooked")
    last_cook_time: float = Field(default=0.0, description="Last cook duration in milliseconds")


class NodeTypeInfo(BaseModel):
    id: str = Field(..., description="Node type identifier (e.g., 'text', 'looper')")
    label: str = Field(..., description="Display name")
    glyph: str = Field(..., description="Unicode glyph character")


class NodeCreateRequest(BaseModel):
    """
    Request to create a new node.

    Example:
        {
            "type": "text",
            "name": "my_text_node",
            "parent_path": "/",
            "position": [100.0, 200.0]
        }
    """
    type: str = Field(..., description="Node type to create (e.g., 'text', 'fileout', 'query')")
    name: Optional[str] = Field(None, description="Desired node name (auto-generated if not provided)")
    parent_path: str = Field(default="/", description="Parent path for node (use '/' for root, '/looper1' for inside looper)")
    position: Optional[List[float]] = Field(None, description="Initial [x, y] position")


class NodeUpdateRequest(BaseModel):
    """
    Request to update node parameters and/or UI state.

    Example:
        {
            "name": "new_node_name",
            "parameters": {
                "text_string": "Updated text",
                "pass_through": true
            },
            "position": [150.0, 250.0]
        }
    """
    name: Optional[str] = Field(None, description="New node name (must be unique in parent path)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameter updates (key: value pairs)")
    position: Optional[List[float]] = Field(None, description="New [x, y] position")
    color: Optional[List[float]] = Field(None, description="New [r, g, b] color")


# ============================================================================
# Connection Models
# ============================================================================

class ConnectionResponse(BaseModel):
    """
    A connection between two nodes.

    Example:
        {
            "connection_id": "123e4567-e89b-12d3-a456-426614174000",
            "source_node_session_id": 123456,
            "source_node_path": "/text1",
            "source_output_index": 0,
            "source_output_name": "output",
            "target_node_session_id": 789012,
            "target_node_path": "/fileout1",
            "target_input_index": 0,
            "target_input_name": "input"
        }
    """
    # Unique connection identifier
    connection_id: str = Field(..., description="Unique connection session ID")

    # Source (output) side
    source_node_session_id: str = Field(..., description="Source node's session ID")
    source_node_path: str = Field(..., description="Source node's path")
    source_output_index: int = Field(..., description="Output socket index (integer)")
    source_output_name: str = Field(..., description="Output socket name")

    # Target (input) side
    target_node_session_id: str = Field(..., description="Target node's session ID")
    target_node_path: str = Field(..., description="Target node's path")
    target_input_index: int = Field(..., description="Input socket index (integer)")
    target_input_name: str = Field(..., description="Input socket name")


class ConnectionRequest(BaseModel):
    """
    Request to create a connection between two nodes.

    Example:
        {
            "source_node_path": "/text1",
            "source_output_index": 0,
            "target_node_path": "/fileout1",
            "target_input_index": 0
        }
    """
    source_node_path: str = Field(..., description="Source node path")
    source_output_index: int = Field(default=0, description="Output socket index (integer)")
    target_node_path: str = Field(..., description="Target node path")
    target_input_index: int = Field(default=0, description="Input socket index (integer)")


class ConnectionDeleteRequest(BaseModel):
    """
    Request to delete a specific connection.

    Example:
        {
            "source_node_path": "/text1",
            "source_output_index": 0,
            "target_node_path": "/fileout1",
            "target_input_index": 0
        }
    """
    source_node_path: str = Field(..., description="Source node path")
    source_output_index: int = Field(..., description="Output socket index (integer)")
    target_node_path: str = Field(..., description="Target node path")
    target_input_index: int = Field(..., description="Input socket index (integer)")


# ============================================================================
# Execution Models
# ============================================================================

class ExecutionResponse(BaseModel):
    """
    Result of executing/cooking a node.
    
    Example:
        {
            "success": true,
            "message": "Node cooked successfully",
            "output_data": [["Hello", "World"]],
            "execution_time": 23.5,
            "node_state": "COOKED",
            "errors": [],
            "warnings": []
        }
    """
    success: bool = Field(..., description="Whether execution succeeded")
    message: str = Field(..., description="Human-readable result message")
    output_data: Optional[List[List[str]]] = Field(None, description="Node output data (list of outputs for multi-output nodes)")
    execution_time: float = Field(..., description="Execution time in milliseconds")
    node_state: NodeStateEnum = Field(..., description="Node state after execution")
    errors: List[str] = Field(default_factory=list, description="Error messages from execution")
    warnings: List[str] = Field(default_factory=list, description="Warning messages from execution")


# ============================================================================
# Workspace Models
# ============================================================================

class WorkspaceState(BaseModel):
    """
    Complete workspace state including all nodes, connections, and globals.
    
    Example:
        {
            "nodes": [...],
            "connections": [...],
            "globals": {
                "LASTRUN": "2024-10-14",
                "PROJECT_NAME": "My Project"
            }
        }
    """
    nodes: List[NodeResponse] = Field(default_factory=list, description="All nodes in workspace")
    connections: List[ConnectionResponse] = Field(default_factory=list, description="All connections")
    globals: Dict[str, Any] = Field(default_factory=dict, description="Global variables")


# ============================================================================
# Helper Models
# ============================================================================

class ErrorResponse(BaseModel):
    """
    Standard error response.
    
    Example:
        {
            "error": "node_not_found",
            "message": "Node '/text1' does not exist",
            "details": {"path": "/text1"}
        }
    """
    error: str = Field(..., description="Error code/type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")


class SuccessResponse(BaseModel):
    """
    Generic success response.
    
    Example:
        {
            "success": true,
            "message": "Node deleted successfully"
        }
    """
    success: bool = Field(default=True, description="Operation success flag")
    message: str = Field(..., description="Success message")


# ============================================================================
# Conversion Utilities
# ============================================================================

"""
Refactored node_to_response() with helper functions
Replace the node_to_response() function in api/models.py with these functions.
"""

import logging
from typing import Dict, List

logger = logging.getLogger("api.models")


def _convert_parameters(node: 'Node', full_state) -> Dict[str, 'ParameterInfo']:
    """Convert node parameters to ParameterInfo DTOs."""
    from api.models import ParameterInfo

    parameters = {}
    for parm_name, parm_state in full_state.parms.items():
        # Determine if parameter is read_only (output parameters)
        is_read_only = parm_name in ['response', 'file_text', 'out_data', 'in_data', 'staging_data']

        # Get default value safely
        default_value = parm_state.value
        if hasattr(node, '_parms') and parm_name in node._parms:
            if hasattr(node._parms[parm_name], '_default'):
                default_value = node._parms[parm_name]._default

        parameters[parm_name] = ParameterInfo(
            type=parm_state.parm_type.replace("ParameterType.", ""),
            value=parm_state.value,
            default=default_value,
            read_only=is_read_only
        )

    return parameters


def _convert_inputs(node: 'Node') -> List['InputInfo']:
    """
    *** LOOPER NODE SPECIAL CONSIDERATION, DO NOT REMOVE THIS COMMENT ***
    Convert node input sockets to InputInfo DTOs.

    Special handling for InputNullNode: Since InputNullNode is an internal node
    within LooperNode that retrieves data from the parent LooperNode's inputs,
    we display the parent LooperNode's connections instead of the InputNullNode's
    (which has none).
    """
    from api.models import InputInfo
    from core.input_null_node import InputNullNode
    import os
    from core.base_classes import NodeEnvironment

    # For InputNullNode, show parent LooperNode's connections
    if isinstance(node, InputNullNode):
        parent_path = os.path.dirname(node.path())
        parent_node = NodeEnvironment.node_from_name(parent_path)
        if parent_node:
            input_names_dict = parent_node.input_names()
            input_data_types_dict = parent_node.input_data_types()
            connections_dict = parent_node._inputs
        else:
            # Fallback if parent not found
            input_names_dict = node.input_names()
            input_data_types_dict = node.input_data_types()
            connections_dict = node._inputs
    else:
        input_names_dict = node.input_names()
        input_data_types_dict = node.input_data_types()
        connections_dict = node._inputs

    inputs = []
    for socket_key, socket_name in input_names_dict.items():
        inputs.append(InputInfo(
            index=socket_key,
            name=socket_name,
            data_type=input_data_types_dict.get(socket_key, "Any"),
            connected=socket_key in connections_dict
        ))

    return inputs


def _convert_outputs(node: 'Node') -> List['OutputInfo']:
    """Convert node output sockets to OutputInfo DTOs."""
    from api.models import OutputInfo
    
    outputs = []
    output_names_dict = node.output_names()
    output_data_types_dict = node.output_data_types()
    
    for socket_key, socket_name in output_names_dict.items():
        connection_count = len(node._outputs.get(socket_key, []))
        outputs.append(OutputInfo(
            index=socket_key,
            name=socket_name,
            data_type=output_data_types_dict.get(socket_key, "Any"),
            connection_count=connection_count
        ))

    return outputs


def node_to_response(node: 'Node') -> 'NodeResponse':
    """
    Convert an internal Node object to a NodeResponse DTO.

    Args:
        node: Internal Node instance

    Returns:
        NodeResponse with all node data

    Raises:
        ValueError: If node state cannot be captured
    """
    from api.models import NodeResponse, NodeStateEnum
    from core.undo_manager import UndoManager

    try:
        # Capture node state
        undo_mgr = UndoManager()
        full_state = undo_mgr._capture_node_state(node)

        # Convert all node components
        parameters = _convert_parameters(node, full_state)
        inputs = _convert_inputs(node)
        outputs = _convert_outputs(node)

        # Build response
        group_enum = getattr(node.__class__, 'GROUP', None)
        group_color = group_enum.value.get('color', '') if group_enum else ''

        response = NodeResponse(
            session_id=node.session_id(),
            name=node.name(),
            path=node.path(),
            type=node.type().value,  # Use enum's value directly
            glyph=getattr(node.__class__, 'GLYPH', ''),  # Get GLYPH class attribute
            group=group_color,
            state=full_state.state.value,
            errors=full_state.errors,
            warnings=full_state.warnings,
            parameters=parameters,
            inputs=inputs,
            outputs=outputs,
            position=full_state.position,
            color=list(node._color) if hasattr(node, '_color') else [1.0, 1.0, 1.0],
            is_time_dependent=full_state.is_time_dependent if full_state.is_time_dependent is not None else False,
            cook_count=full_state.cook_count,
            last_cook_time=full_state.last_cook_time
        )

        return response
        
    except AttributeError as e:
        logger.error(f"AttributeError converting node {node.path()}: {e}")
        raise ValueError(f"Node state incomplete: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error converting node {node.path()}: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise





def connection_to_response(connection: 'NodeConnection') -> ConnectionResponse:
    """
    *** LOOPER NODE SPECIAL CONSIDERATION, DO NOT REMOVE THIS COMMENT ***
    Convert an internal NodeConnection to a ConnectionResponse DTO.

    Special handling for LooperNode: Connections to a LooperNode's input are displayed
    in the GUI as connections to the InputNullNode (looper_start). This function maps
    the actual backend connection (to LooperNode) to the GUI display path (InputNullNode).

    Args:
        connection: Internal NodeConnection instance

    Returns:
        ConnectionResponse with connection details
    """
    from core.looper_node import LooperNode
    from core.base_classes import NodeEnvironment

    target_node = connection.input_node()
    target_path = target_node.path()
    target_session_id = target_node.session_id()

    # If connection is to a LooperNode input, map to InputNullNode for GUI display
    if isinstance(target_node, LooperNode) and connection.input_index() == 0:
        input_null_path = f"{target_path}/inputNullNode"
        input_null_node = NodeEnvironment.node_from_name(input_null_path)
        if input_null_node:
            target_path = input_null_node.path()
            target_session_id = input_null_node.session_id()

    return ConnectionResponse(
        connection_id=connection.session_id(),
        source_node_session_id=connection.output_node().session_id(),
        source_node_path=connection.output_node().path(),
        source_output_index=connection.output_index(),
        source_output_name=connection.output_name(),
        target_node_session_id=target_session_id,
        target_node_path=target_path,
        target_input_index=connection.input_index(),
        target_input_name=connection.input_name()
    )