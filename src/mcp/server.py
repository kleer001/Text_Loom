"""
Text Loom MCP Server

Exposes Text Loom functionality via Model Context Protocol (MCP).
Enables LLMs to create and execute text processing workflows.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

from mcp.session_manager import get_session_manager
from mcp.workflow_builder import WorkflowBuilder, get_available_node_types, get_node_details


app = Server("text-loom")


def _json_response(data: Dict[str, Any]) -> List[TextContent]:
    """Create standardized JSON response for MCP tool calls."""
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _success_response(data: Dict[str, Any]) -> List[TextContent]:
    """Create success response with data."""
    return _json_response({"success": True, **data})


def _error_response(error: str, **kwargs) -> List[TextContent]:
    """Create error response."""
    return _json_response({"success": False, "error": error, **kwargs})


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools for Text Loom."""
    return [
        Tool(
            name="create_session",
            description="Create a new isolated workflow session. Each session has its own workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata for the session"
                    }
                }
            }
        ),
        Tool(
            name="list_node_types",
            description="List all available node types with brief descriptions (lightweight - ~500 tokens). Use get_node_details for full documentation.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_node_details",
            description="Get detailed documentation for a specific node type including full docstring, parameters, types, and defaults. Use after list_node_types to get specifics.",
            inputSchema={
                "type": "object",
                "required": ["node_type"],
                "properties": {
                    "node_type": {
                        "type": "string",
                        "description": "Node type name (e.g., 'query', 'file_out', 'looper')"
                    }
                }
            }
        ),
        Tool(
            name="add_node",
            description="Add a node to the workflow. Returns the session_id of the created node.",
            inputSchema={
                "type": "object",
                "required": ["session_id", "node_type", "name"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to add node to"
                    },
                    "node_type": {
                        "type": "string",
                        "description": "Type of node (e.g., 'text', 'query', 'file_out')"
                    },
                    "name": {
                        "type": "string",
                        "description": "Unique name for the node"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Node-specific parameters (e.g., text_string for text nodes)"
                    },
                    "position": {
                        "type": "array",
                        "description": "Visual position [x, y]",
                        "items": {"type": "number"}
                    }
                }
            }
        ),
        Tool(
            name="connect_nodes",
            description="Connect two nodes together. Data flows from source to target.",
            inputSchema={
                "type": "object",
                "required": ["session_id", "source_name", "target_name"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID"
                    },
                    "source_name": {
                        "type": "string",
                        "description": "Name of source node"
                    },
                    "target_name": {
                        "type": "string",
                        "description": "Name of target node"
                    },
                    "source_output": {
                        "type": "integer",
                        "description": "Source output index (default 0)",
                        "default": 0
                    },
                    "target_input": {
                        "type": "integer",
                        "description": "Target input index (default 0)",
                        "default": 0
                    }
                }
            }
        ),
        Tool(
            name="execute_workflow",
            description="Execute all nodes in the workflow and return results",
            inputSchema={
                "type": "object",
                "required": ["session_id"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to execute"
                    }
                }
            }
        ),
        Tool(
            name="get_node_output",
            description="Get the output data from a specific node after execution",
            inputSchema={
                "type": "object",
                "required": ["session_id", "node_name"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID"
                    },
                    "node_name": {
                        "type": "string",
                        "description": "Name of the node"
                    },
                    "output_index": {
                        "type": "integer",
                        "description": "Output index (default 0)",
                        "default": 0
                    }
                }
            }
        ),
        Tool(
            name="export_workflow",
            description="Export workflow as JSON for user to save/edit. Returns flowstate format.",
            inputSchema={
                "type": "object",
                "required": ["session_id"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to export"
                    }
                }
            }
        ),
        Tool(
            name="set_global",
            description="Set a global variable accessible to all nodes",
            inputSchema={
                "type": "object",
                "required": ["session_id", "key", "value"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID"
                    },
                    "key": {
                        "type": "string",
                        "description": "Global variable name"
                    },
                    "value": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of strings"
                    }
                }
            }
        ),
        Tool(
            name="delete_session",
            description="Delete a session and clean up resources",
            inputSchema={
                "type": "object",
                "required": ["session_id"],
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to delete"
                    }
                }
            }
        )
    ]


def _handle_create_session(manager, arguments: Dict) -> List[TextContent]:
    metadata = arguments.get("metadata", {})
    session_id = manager.create_session(metadata)
    return _success_response({
        "session_id": session_id,
        "message": "Session created. Use this session_id for all workflow operations."
    })


def _handle_list_node_types(manager, arguments: Dict) -> List[TextContent]:
    node_types = get_available_node_types()
    return _success_response({
        "node_types": node_types,
        "note": "Use get_node_details(node_type) for full documentation of a specific node"
    })


def _handle_get_node_details(manager, arguments: Dict) -> List[TextContent]:
    try:
        details = get_node_details(arguments["node_type"])
        return _success_response({"node_details": details})
    except ValueError as e:
        return _error_response(str(e), hint="Use list_node_types to see available types")


def _handle_add_node(manager, arguments: Dict) -> List[TextContent]:
    session_id = arguments["session_id"]
    with manager.use_session(session_id):
        builder = WorkflowBuilder()
        node_session_id = builder.add_node(
            node_type=arguments["node_type"],
            name=arguments["name"],
            parameters=arguments.get("parameters"),
            position=tuple(arguments["position"]) if "position" in arguments else None
        )
        return _success_response({
            "node_session_id": node_session_id,
            "name": arguments["name"],
            "type": arguments["node_type"]
        })


def _handle_connect_nodes(manager, arguments: Dict) -> List[TextContent]:
    session_id = arguments["session_id"]
    with manager.use_session(session_id):
        builder = WorkflowBuilder()
        builder.connect(
            source_name=arguments["source_name"],
            target_name=arguments["target_name"],
            source_output=arguments.get("source_output", 0),
            target_input=arguments.get("target_input", 0)
        )
        return _success_response({
            "connection": {
                "source": arguments["source_name"],
                "target": arguments["target_name"]
            }
        })


def _handle_execute_workflow(manager, arguments: Dict) -> List[TextContent]:
    session_id = arguments["session_id"]
    with manager.use_session(session_id):
        builder = WorkflowBuilder()
        results = builder.execute_all()
        return _json_response({
            "success": results["success"],
            "results": results["results"],
            "errors": results.get("errors", [])
        })


def _handle_get_node_output(manager, arguments: Dict) -> List[TextContent]:
    session_id = arguments["session_id"]
    with manager.use_session(session_id):
        builder = WorkflowBuilder()
        output = builder.get_output(arguments["node_name"], arguments.get("output_index", 0))
        return _success_response({
            "node": arguments["node_name"],
            "output": output
        })


def _handle_export_workflow(manager, arguments: Dict) -> List[TextContent]:
    flowstate = manager.export_session(arguments["session_id"])
    return _success_response({
        "flowstate": flowstate,
        "message": "Workflow exported. User can save this JSON and load it in Text Loom GUI/TUI."
    })


def _handle_set_global(manager, arguments: Dict) -> List[TextContent]:
    session_id = arguments["session_id"]
    with manager.use_session(session_id):
        builder = WorkflowBuilder()
        builder.set_global(arguments["key"], arguments["value"])
        return _success_response({
            "global": {
                "key": arguments["key"],
                "value": arguments["value"]
            }
        })


def _handle_delete_session(manager, arguments: Dict) -> List[TextContent]:
    success = manager.delete_session(arguments["session_id"])
    return _success_response({
        "message": "Session deleted" if success else "Session not found"
    }) if success else _error_response("Session not found")


TOOL_HANDLERS = {
    "create_session": _handle_create_session,
    "list_node_types": _handle_list_node_types,
    "get_node_details": _handle_get_node_details,
    "add_node": _handle_add_node,
    "connect_nodes": _handle_connect_nodes,
    "execute_workflow": _handle_execute_workflow,
    "get_node_output": _handle_get_node_output,
    "export_workflow": _handle_export_workflow,
    "set_global": _handle_set_global,
    "delete_session": _handle_delete_session
}


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls from LLM."""
    manager = get_session_manager()

    try:
        handler = TOOL_HANDLERS.get(name)
        if handler:
            return handler(manager, arguments)
        return _error_response(f"Unknown tool: {name}")
    except Exception as e:
        return _error_response(str(e), tool=name)


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
