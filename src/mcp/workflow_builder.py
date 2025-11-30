"""
Workflow Builder for MCP Server

High-level interface for creating Text Loom workflows programmatically.
Simplifies node creation and connection for LLM agents.
"""

import importlib
import inspect
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from core.base_classes import Node, NodeEnvironment, NodeType
from core.global_store import GlobalStore
from core.parm import ParameterType


class WorkflowBuilder:
    """Helper class for building Text Loom workflows programmatically."""

    def add_node(
        self,
        node_type: str,
        name: str,
        parameters: Optional[Dict[str, Any]] = None,
        position: Optional[Tuple[float, float]] = None
    ) -> str:
        from core.node import Node

        node_type_enum = NodeType[node_type.upper()]

        node = Node.create_node(node_type_enum, name, parent_path='/')

        if parameters:
            for key, value in parameters.items():
                if key in node._parms:
                    node._parms[key].set(value)
                else:
                    raise ValueError(f"Unknown parameter: {key}")

        if position:
            node.position = list(position)

        return node.session_id()

    def connect(
        self,
        source_name: str,
        target_name: str,
        source_output: int = 0,
        target_input: int = 0
    ) -> bool:
        source = NodeEnvironment.node_from_name(source_name)
        target = NodeEnvironment.node_from_name(target_name)

        if not source or not target:
            raise ValueError(f"Node not found: {source_name if not source else target_name}")

        target.set_input(target_input, source, source_output)

        return True

    def execute_node(self, name: str) -> Dict[str, Any]:
        from core.base_classes import NodeState

        node = NodeEnvironment.node_from_name(name)
        if not node:
            raise ValueError(f"Node not found: {name}")

        node.cook()

        return {
            "success": node.state() == NodeState.UNCHANGED,
            "output": node.get_output() if hasattr(node, 'get_output') else [],
            "errors": node.errors() if hasattr(node, 'errors') else [],
            "warnings": node.warnings() if hasattr(node, 'warnings') else [],
            "state": node.state().name
        }

    def execute_all(self) -> Dict[str, Any]:
        results = {}
        errors = []

        for path in NodeEnvironment.list_nodes():
            if path == '/':
                continue
            node = NodeEnvironment.nodes[path]
            name = node.name()
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
        node = NodeEnvironment.node_from_name(name)
        if not node:
            raise ValueError(f"Node not found: {name}")

        return node.get_output()

    def set_global(self, key: str, value: List[str]) -> None:
        GlobalStore.set(key, value)


def _import_node_class(type_name: str):
    """Import a node class with fallback stubbing for missing dependencies.

    Args:
        type_name: Node type name (lowercase, e.g., 'query', 'file_out')

    Returns:
        Tuple of (node_class, was_stubbed)
    """
    module_name = f"core.{type_name}_node"
    class_name = ''.join(word.capitalize() for word in type_name.split('_')) + 'Node'

    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name), False
    except ImportError:
        import sys
        original_modules = sys.modules.copy()
        try:
            sys.modules['litellm'] = type('module', (), {})()
            module = importlib.import_module(module_name)
            node_class = getattr(module, class_name)
            return node_class, True
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)


def get_available_node_types() -> List[Dict[str, Any]]:
    """Get lightweight list of all available node types.

    Returns minimal info for browsing - use get_node_details() for full docs.

    Returns:
        List of dicts containing:
        - type: Node type name (lowercase)
        - description: Short one-line description
        - parameter_names: List of parameter names (no types/defaults)
        - inputs: Number of inputs (or "multiple" for unlimited)
        - outputs: Number of outputs
    """
    node_types = []

    for node_type in NodeType:
        type_name = node_type.name.lower()

        try:
            node_class, _ = _import_node_class(type_name)

            docstring = inspect.getdoc(node_class) or "No documentation available"
            description = docstring.split('\n')[0]

            parameters = _extract_parameters(node_class)
            param_names = [p["name"] for p in parameters]

            single_input = getattr(node_class, 'SINGLE_INPUT', True)
            single_output = getattr(node_class, 'SINGLE_OUTPUT', True)

            node_types.append({
                "type": type_name,
                "description": description,
                "parameter_names": param_names,
                "inputs": 1 if single_input else "multiple",
                "outputs": 1 if single_output else "multiple"
            })

        except (ImportError, AttributeError) as e:
            node_types.append({
                "type": type_name,
                "description": _get_fallback_description(node_type),
                "parameter_names": [],
                "inputs": 1,
                "outputs": 1
            })

    return node_types


def get_node_details(node_type_name: str) -> Dict[str, Any]:
    """Get detailed documentation for a specific node type.

    Args:
        node_type_name: Node type (e.g., "query", "file_out")

    Returns:
        Dict containing:
        - type: Node type name
        - description: Short description
        - docstring: Full class docstring with examples and details
        - parameters: List of parameters with names, types, and defaults
        - inputs: Number of inputs
        - outputs: Number of outputs

    Raises:
        ValueError: If node type doesn't exist
    """
    # Find the NodeType enum value
    try:
        node_type = NodeType[node_type_name.upper()]
    except KeyError:
        raise ValueError(f"Unknown node type: {node_type_name}")

    type_name = node_type.name.lower()

    try:
        node_class, _ = _import_node_class(type_name)

        docstring = inspect.getdoc(node_class) or "No documentation available"
        parameters = _extract_parameters(node_class)

        single_input = getattr(node_class, 'SINGLE_INPUT', True)
        single_output = getattr(node_class, 'SINGLE_OUTPUT', True)

        return {
            "type": type_name,
            "description": docstring.split('\n')[0],
            "docstring": docstring,
            "parameters": parameters,
            "inputs": 1 if single_input else "multiple",
            "outputs": 1 if single_output else "multiple"
        }

    except (ImportError, AttributeError) as e:
        return {
            "type": type_name,
            "description": _get_fallback_description(node_type),
            "docstring": _get_fallback_docstring(node_type),
            "parameters": [],
            "inputs": 1,
            "outputs": 1
        }


def _extract_parameters(node_class) -> List[Dict[str, Any]]:
    """Extract parameter information from a node class by parsing __init__ source.

    Instead of instantiating (which may fail due to dependencies), we parse
    the source code to find Parm definitions.
    """
    parameters = []

    try:
        # Get the source code of __init__
        source = inspect.getsource(node_class.__init__)

        # Parse for Parm definitions
        # Pattern: "param_name": Parm("param_name", ParameterType.TYPE, ...)
        import re
        parm_pattern = r'"([^"]+)":\s*Parm\("([^"]+)",\s*ParameterType\.(\w+)'
        matches = re.findall(parm_pattern, source)

        for key, name, param_type in matches:
            parameters.append({
                "name": name,
                "type": param_type,
            })

        # Also look for .set() calls to find defaults
        # Pattern: self._parms["param_name"].set(value)
        set_pattern = r'self\._parms\["([^"]+)"\]\.set\(([^)]+)\)'
        set_matches = re.findall(set_pattern, source)

        # Create a dict of defaults
        defaults = {name: value for name, value in set_matches}

        # Add defaults to parameters
        for param in parameters:
            if param["name"] in defaults:
                param["default"] = defaults[param["name"]]

    except Exception as e:
        # If parsing fails, return empty list
        pass

    return parameters


def _get_fallback_description(node_type: NodeType) -> str:
    """Fallback descriptions for nodes that can't be dynamically loaded."""
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


def _get_fallback_docstring(node_type: NodeType) -> str:
    """Fallback docstrings with basic parameter info for common nodes."""
    docstrings = {
        NodeType.QUERY: """A node that interfaces with Large Language Models (LLMs) to process text prompts and generate responses.

Sends text to LLMs and returns responses. Supports multiple LLM providers.

Parameters:
    limit (bool): If True, restricts processing to only the first prompt
    llm_name (str): Identifier for the target LLM (e.g., "Ollama", "Claude", "GPT-4")
    response (List[str]): Stores the history of LLM responses
    track_tokens (bool): Enable token usage tracking

Input:
    List[str]: Collection of prompts to process

Output:
    List[str]: Generated LLM responses corresponding to input prompts
""",
    }
    return docstrings.get(node_type, f"Node type: {node_type.name.lower()}\n\nNo detailed documentation available.")
