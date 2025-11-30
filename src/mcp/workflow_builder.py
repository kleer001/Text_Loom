"""
Workflow Builder for MCP Server

High-level interface for creating Text Loom workflows programmatically.
Simplifies node creation and connection for LLM agents.
"""

from typing import Dict, List, Any, Optional, Tuple
from core.base_classes import Node, NodeEnvironment, NodeType
from core.global_store import GlobalStore


class WorkflowBuilder:
    """Helper class for building Text Loom workflows programmatically."""

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.connections: List[Tuple[str, int, str, int]] = []

    def add_node(
        self,
        node_type: str,
        name: str,
        parameters: Optional[Dict[str, Any]] = None,
        position: Optional[Tuple[float, float]] = None
    ) -> str:
        node_type_enum = NodeType[node_type.upper()]

        node_class = NodeEnvironment.get_node_class(node_type_enum)
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")

        node = node_class()
        node.name = name

        if parameters:
            for key, value in parameters.items():
                if hasattr(node, key):
                    setattr(node, key, value)

        if position:
            node.position = list(position)

        NodeEnvironment.register_node(node)
        self.nodes[name] = node

        return node.session_id

    def connect(
        self,
        source_name: str,
        target_name: str,
        source_output: int = 0,
        target_input: int = 0
    ) -> bool:
        source = self.nodes.get(source_name)
        target = self.nodes.get(target_name)

        if not source or not target:
            raise ValueError(f"Node not found: {source_name if not source else target_name}")

        target.connect_input(target_input, source, source_output)
        self.connections.append((source_name, source_output, target_name, target_input))

        return True

    def execute_node(self, name: str) -> Dict[str, Any]:
        node = self.nodes.get(name)
        if not node:
            raise ValueError(f"Node not found: {name}")

        node.cook()

        return {
            "success": node.status.cooked,
            "output": [output.data if output else [] for output in node.outputs],
            "errors": node.status.errors,
            "warnings": node.status.warnings,
            "state": node.status.state.name
        }

    def execute_all(self) -> Dict[str, Any]:
        results = {}
        errors = []

        for name, node in self.nodes.items():
            try:
                result = self.execute_node(name)
                results[name] = result

                if not result["success"]:
                    errors.extend(result["errors"])
            except Exception as e:
                errors.append(f"Error executing {name}: {str(e)}")

        return {
            "success": len(errors) == 0,
            "results": results,
            "errors": errors
        }

    def get_output(self, name: str, output_index: int = 0) -> List[str]:
        node = self.nodes.get(name)
        if not node:
            raise ValueError(f"Node not found: {name}")

        if output_index >= len(node.outputs):
            raise ValueError(f"Output index {output_index} out of range")

        output = node.outputs[output_index]
        return output.data if output else []

    def set_global(self, key: str, value: List[str]) -> None:
        GlobalStore.set(key, value)

    def get_global(self, key: str) -> Optional[List[str]]:
        return GlobalStore.get(key)

    def clear(self) -> None:
        NodeEnvironment.clear()
        GlobalStore.clear()
        self.nodes.clear()
        self.connections.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {
                    "name": name,
                    "type": node.node_type.name,
                    "session_id": node.session_id,
                    "position": node.position
                }
                for name, node in self.nodes.items()
            ],
            "connections": [
                {
                    "source": src,
                    "source_output": src_out,
                    "target": tgt,
                    "target_input": tgt_in
                }
                for src, src_out, tgt, tgt_in in self.connections
            ]
        }


def get_available_node_types() -> List[Dict[str, str]]:
    return [
        {
            "type": node_type.name.lower(),
            "description": _get_node_description(node_type)
        }
        for node_type in NodeType
    ]


def _get_node_description(node_type: NodeType) -> str:
    descriptions = {
        NodeType.TEXT: "Static text input - stores text string",
        NodeType.FILE_OUT: "Write data to file",
        NodeType.FILE_IN: "Read data from file",
        NodeType.NULL: "Null output - discards input",
        NodeType.MERGE: "Merge multiple inputs into single output",
        NodeType.SPLIT: "Split input list into multiple outputs",
        NodeType.QUERY: "Send text to LLM and get response",
        NodeType.LOOPER: "Loop over list items and process each",
        NodeType.MAKE_LIST: "Create list from individual items",
        NodeType.SECTION: "Visual grouping container",
        NodeType.FOLDER: "Hierarchical organization",
        NodeType.JSON: "Parse/generate JSON data",
        NodeType.INPUT_NULL: "Null input - provides empty data",
        NodeType.OUTPUT_NULL: "Null output - receives but discards data"
    }
    return descriptions.get(node_type, "No description available")
