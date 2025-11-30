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
from mcp.workflow_builder import WorkflowBuilder, get_available_node_types


app = Server("text-loom")


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
            description="List all available node types and their descriptions",
            inputSchema={"type": "object", "properties": {}}
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


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls from LLM."""

    manager = get_session_manager()

    try:
        if name == "create_session":
            metadata = arguments.get("metadata", {})
            session_id = manager.create_session(metadata)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "session_id": session_id,
                    "message": "Session created. Use this session_id for all workflow operations."
                }, indent=2)
            )]

        elif name == "list_node_types":
            node_types = get_available_node_types()
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "node_types": node_types
                }, indent=2)
            )]

        elif name == "add_node":
            session_id = arguments["session_id"]

            with manager.use_session(session_id):
                builder = WorkflowBuilder()
                node_session_id = builder.add_node(
                    node_type=arguments["node_type"],
                    name=arguments["name"],
                    parameters=arguments.get("parameters"),
                    position=tuple(arguments["position"]) if "position" in arguments else None
                )

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "node_session_id": node_session_id,
                        "name": arguments["name"],
                        "type": arguments["node_type"]
                    }, indent=2)
                )]

        elif name == "connect_nodes":
            session_id = arguments["session_id"]

            with manager.use_session(session_id):
                builder = WorkflowBuilder()
                builder.connect(
                    source_name=arguments["source_name"],
                    target_name=arguments["target_name"],
                    source_output=arguments.get("source_output", 0),
                    target_input=arguments.get("target_input", 0)
                )

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "connection": {
                            "source": arguments["source_name"],
                            "target": arguments["target_name"]
                        }
                    }, indent=2)
                )]

        elif name == "execute_workflow":
            session_id = arguments["session_id"]

            with manager.use_session(session_id):
                builder = WorkflowBuilder()
                results = builder.execute_all()

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": results["success"],
                        "results": results["results"],
                        "errors": results.get("errors", [])
                    }, indent=2)
                )]

        elif name == "get_node_output":
            session_id = arguments["session_id"]
            node_name = arguments["node_name"]
            output_index = arguments.get("output_index", 0)

            with manager.use_session(session_id):
                builder = WorkflowBuilder()
                output = builder.get_output(node_name, output_index)

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "node": node_name,
                        "output": output
                    }, indent=2)
                )]

        elif name == "export_workflow":
            session_id = arguments["session_id"]
            flowstate = manager.export_session(session_id)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "flowstate": flowstate,
                    "message": "Workflow exported. User can save this JSON and load it in Text Loom GUI/TUI."
                }, indent=2)
            )]

        elif name == "set_global":
            session_id = arguments["session_id"]

            with manager.use_session(session_id):
                builder = WorkflowBuilder()
                builder.set_global(arguments["key"], arguments["value"])

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "global": {
                            "key": arguments["key"],
                            "value": arguments["value"]
                        }
                    }, indent=2)
                )]

        elif name == "delete_session":
            session_id = arguments["session_id"]
            success = manager.delete_session(session_id)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": success,
                    "message": "Session deleted" if success else "Session not found"
                }, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}"
                }, indent=2)
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "tool": name
            }, indent=2)
        )]


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
