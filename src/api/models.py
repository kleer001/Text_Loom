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
    """Node processing state"""
    COOKING = "COOKING"
    UNCHANGED = "UNCHANGE"
    UNCOOKED = "UNCOOKED"
    COOKED = "COOKED"


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
            "index": 0,  # Can be int or string
            "name": "input",
            "data_type": "List[str]",
            "connected": true
        }
    """
    index: Union[int, str] = Field(..., description="Input index (can be integer or string key)")
    name: str = Field(..., description="Display name of this input")
    data_type: str = Field(..., description="Expected data type")
    connected: bool = Field(..., description="Whether this input has a connection")


class OutputInfo(BaseModel):
    """
    Information about a node's output socket.
    
    Example:
        {
            "index": 0,  # Can be int or string
            "name": "output",
            "data_type": "List[str]",
            "connection_count": 2
        }
    """
    index: Union[int, str] = Field(..., description="Output index (can be integer or string key)")
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
            "selected": false,
            "is_time_dependent": false,
            "cook_count": 5,
            "last_cook_time": 0.023
        }
    """
    # Core identification
    session_id: int = Field(..., description="Unique session identifier")
    name: str = Field(..., description="Node name (may not be unique)")
    path: str = Field(..., description="Full path (unique identifier)")
    type: str = Field(..., description="Node type (e.g., 'text', 'fileout', 'query')")
    
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
    selected: bool = Field(default=False, description="Whether node is selected in UI")
    
    # Performance metrics
    is_time_dependent: bool = Field(default=False, description="Whether node recooks on every eval")
    cook_count: int = Field(default=0, description="Number of times node has cooked")
    last_cook_time: float = Field(default=0.0, description="Last cook duration in milliseconds")


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
            "parameters": {
                "text_string": "Updated text",
                "pass_through": true
            },
            "position": [150.0, 250.0],
            "selected": true
        }
    """
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameter updates (key: value pairs)")
    position: Optional[List[float]] = Field(None, description="New [x, y] position")
    color: Optional[List[float]] = Field(None, description="New [r, g, b] color")
    selected: Optional[bool] = Field(None, description="Selection state")


# ============================================================================
# Connection Models
# ============================================================================

class ConnectionResponse(BaseModel):
    """
    A connection between two nodes.
    
    Example:
        {
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
    # Source (output) side
    source_node_session_id: int = Field(..., description="Source node's session ID")
    source_node_path: str = Field(..., description="Source node's path")
    source_output_index: int = Field(..., description="Output socket index")
    source_output_name: str = Field(..., description="Output socket name")
    
    # Target (input) side
    target_node_session_id: int = Field(..., description="Target node's session ID")
    target_node_path: str = Field(..., description="Target node's path")
    target_input_index: int = Field(..., description="Input socket index")
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
    source_output_index: int = Field(default=0, description="Output socket index")
    target_node_path: str = Field(..., description="Target node path")
    target_input_index: int = Field(default=0, description="Input socket index")


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
    source_output_index: int = Field(..., description="Output socket index")
    target_node_path: str = Field(..., description="Target node path")
    target_input_index: int = Field(..., description="Input socket index")


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



def node_to_response(node: 'Node') -> 'NodeResponse':
    """
    Convert an internal Node object to a NodeResponse DTO.
    FIXED: Properly handles dictionary keys (strings or integers) for sockets.
    
    Args:
        node: Internal Node instance
        
    Returns:
        NodeResponse with all node data
        
    Raises:
        ValueError: If node state cannot be captured
    """
    from api.models import NodeResponse, ParameterInfo, InputInfo, OutputInfo, NodeStateEnum
    
    logger.debug(f"Converting node to response: {node.path()}, type={node.type()}")
    
    try:
        from core.undo_manager import UndoManager
        
        # Capture node state
        undo_mgr = UndoManager()
        logger.debug(f"  Capturing node state via UndoManager")
        full_state = undo_mgr._capture_node_state(node)
        logger.debug(f"  State captured successfully")
        
        # Convert parameters
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
        
        logger.debug(f"  Converted {len(parameters)} parameters")
        
        # Convert inputs - FIXED: Use actual dictionary keys, not enumerate
        inputs = []
        input_names_dict = node.input_names()
        input_data_types_dict = node.input_data_types()
        
        logger.debug(f"  Input names dict: {input_names_dict}")
        logger.debug(f"  Input data types dict: {input_data_types_dict}")
        
        for socket_key, socket_name in input_names_dict.items():
            # Use the actual socket_key from the dictionary
            inputs.append(InputInfo(
                index=socket_key,  # Use actual key (could be int or string)
                name=socket_name,
                data_type=input_data_types_dict.get(socket_key, "Any"),
                connected=socket_key in node._inputs
            ))
        
        logger.debug(f"  Converted {len(inputs)} inputs")
        
        # Convert outputs - FIXED: Use actual dictionary keys, not enumerate
        outputs = []
        output_names_dict = node.output_names()
        output_data_types_dict = node.output_data_types()
        
        logger.debug(f"  Output names dict: {output_names_dict}")
        logger.debug(f"  Output data types dict: {output_data_types_dict}")
        
        for socket_key, socket_name in output_names_dict.items():
            # Use the actual socket_key from the dictionary
            connection_count = len(node._outputs.get(socket_key, []))
            outputs.append(OutputInfo(
                index=socket_key,  # Use actual key (could be int or string)
                name=socket_name,
                data_type=output_data_types_dict.get(socket_key, "Any"),
                connection_count=connection_count
            ))
        
        logger.debug(f"  Converted {len(outputs)} outputs")
        
        # Build response
        response = NodeResponse(
            session_id=node.session_id(),
            name=node.name(),
            path=node.path(),
            type=full_state.node_type.replace("NodeType.", "").lower(),
            state=NodeStateEnum(full_state.state),
            errors=full_state.errors,
            warnings=full_state.warnings,
            parameters=parameters,
            inputs=inputs,
            outputs=outputs,
            position=full_state.position,
            color=list(node._color) if hasattr(node, '_color') else [1.0, 1.0, 1.0],
            selected=node._selected if hasattr(node, '_selected') else False,
            is_time_dependent=full_state.is_time_dependent,
            cook_count=full_state.cook_count,
            last_cook_time=full_state.last_cook_time
        )
        
        logger.debug(f"  Response created successfully for {node.path()}")
        return response
        
    except AttributeError as e:
        logger.error(f"AttributeError converting node {node.path()}: {e}")
        logger.error(f"  Node has _parms: {hasattr(node, '_parms')}")
        logger.error(f"  Node has _inputs: {hasattr(node, '_inputs')}")
        logger.error(f"  Node has _outputs: {hasattr(node, '_outputs')}")
        raise ValueError(f"Node state incomplete: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error converting node {node.path()}: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise





def connection_to_response(connection: 'NodeConnection') -> ConnectionResponse:
    """
    Convert an internal NodeConnection to a ConnectionResponse DTO.
    
    Args:
        connection: Internal NodeConnection instance
        
    Returns:
        ConnectionResponse with connection details
    """
    return ConnectionResponse(
        source_node_session_id=connection.output_node().session_id(),
        source_node_path=connection.output_node().path(),
        source_output_index=connection.output_index(),
        source_output_name=connection.output_name(),
        target_node_session_id=connection.input_node().session_id(),
        target_node_path=connection.input_node().path(),
        target_input_index=connection.input_index(),
        target_input_name=connection.input_name()
    )