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

        # Import the node class dynamically
        try:
            module_name = f"core.{type_name}_node"
            class_name = ''.join(word.capitalize() for word in type_name.split('_')) + 'Node'

            # Try importing - some nodes have dependencies that may not be installed
            try:
                module = importlib.import_module(module_name)
                node_class = getattr(module, class_name)
            except ImportError:
                # If import fails, try to load just for docstring extraction
                import sys
                original_modules = sys.modules.copy()
                try:
                    # Stub out problematic imports
                    sys.modules['litellm'] = type('module', (), {})()
                    module = importlib.import_module(module_name)
                    node_class = getattr(module, class_name)
                finally:
                    # Restore original modules
                    sys.modules.clear()
                    sys.modules.update(original_modules)

            # Extract docstring (just first line for description)
            docstring = inspect.getdoc(node_class) or "No documentation available"
            description = docstring.split('\n')[0]

            # Extract just parameter names (lightweight)
            parameters = _extract_parameters(node_class)
            param_names = [p["name"] for p in parameters]

            # Get input/output info from class attributes
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
            # Fallback for nodes that can't be imported at all
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

    # Import the node class dynamically
    try:
        module_name = f"core.{type_name}_node"
        class_name = ''.join(word.capitalize() for word in type_name.split('_')) + 'Node'

        # Try importing - some nodes have dependencies that may not be installed
        try:
            module = importlib.import_module(module_name)
            node_class = getattr(module, class_name)
        except ImportError:
            # If import fails, try to load just for docstring extraction
            import sys
            original_modules = sys.modules.copy()
            try:
                # Stub out problematic imports
                sys.modules['litellm'] = type('module', (), {})()
                module = importlib.import_module(module_name)
                node_class = getattr(module, class_name)
            finally:
                # Restore original modules
                sys.modules.clear()
                sys.modules.update(original_modules)

        # Extract full docstring
        docstring = inspect.getdoc(node_class) or "No documentation available"

        # Extract detailed parameters
        parameters = _extract_parameters(node_class)

        # Get input/output info from class attributes
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
        # Fallback for nodes that can't be imported at all
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
