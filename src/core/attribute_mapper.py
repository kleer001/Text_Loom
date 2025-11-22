"""
Attribute Mapper for Node Serialization

This module provides transformation functions between public attribute names
(used in flowstate_manager.py's NODE_ATTRIBUTES) and internal attribute names
(used in Node class with underscore prefix).

The flowstate_manager.py is a sacred file that cannot be modified, so this
helper module bridges the gap between the non-underscored names in
NODE_ATTRIBUTES and the underscored names in the Node class.

Example:
    'is_time_dependent' (public) <-> '_is_time_dependent' (internal)
    'name' (public) <-> '_name' (internal)
"""

from typing import Any, Dict
from core.base_classes import Node


def to_internal_name(public_name: str) -> str:
    """
    Convert a public attribute name to its internal (underscored) form.

    Args:
        public_name: Public attribute name (e.g., 'is_time_dependent')

    Returns:
        Internal attribute name (e.g., '_is_time_dependent')
    """
    return f'_{public_name}'


def to_public_name(internal_name: str) -> str:
    """
    Convert an internal attribute name to its public (non-underscored) form.

    Args:
        internal_name: Internal attribute name (e.g., '_is_time_dependent')

    Returns:
        Public attribute name (e.g., 'is_time_dependent')
    """
    if internal_name.startswith('_'):
        return internal_name[1:]
    return internal_name


def get_node_attribute(node: Node, public_name: str, default: Any = None) -> Any:
    """
    Get a node attribute using a public (non-underscored) name.

    Args:
        node: The node to get the attribute from
        public_name: Public attribute name (e.g., 'is_time_dependent')
        default: Default value if attribute doesn't exist

    Returns:
        The attribute value or default if not found
    """
    internal_name = to_internal_name(public_name)
    return getattr(node, internal_name, default)


def set_node_attribute(node: Node, public_name: str, value: Any) -> None:
    """
    Set a node attribute using a public (non-underscored) name.

    Args:
        node: The node to set the attribute on
        public_name: Public attribute name (e.g., 'is_time_dependent')
        value: The value to set
    """
    internal_name = to_internal_name(public_name)
    setattr(node, internal_name, value)


def has_node_attribute(node: Node, public_name: str) -> bool:
    """
    Check if a node has an attribute using a public (non-underscored) name.

    Args:
        node: The node to check
        public_name: Public attribute name (e.g., 'is_time_dependent')

    Returns:
        True if the attribute exists, False otherwise
    """
    internal_name = to_internal_name(public_name)
    return hasattr(node, internal_name)


def map_attributes_from_node(node: Node, public_names: list) -> Dict[str, Any]:
    """
    Extract multiple attributes from a node using public names.
    Returns a dictionary with public names as keys.

    Args:
        node: The node to extract attributes from
        public_names: List of public attribute names

    Returns:
        Dictionary mapping public names to their values
    """
    result = {}
    for public_name in public_names:
        internal_name = to_internal_name(public_name)
        if hasattr(node, internal_name):
            result[public_name] = getattr(node, internal_name)
    return result


def apply_attributes_to_node(node: Node, attributes: Dict[str, Any]) -> None:
    """
    Apply multiple attributes to a node using a dictionary with public names.

    Args:
        node: The node to apply attributes to
        attributes: Dictionary with public names as keys
    """
    for public_name, value in attributes.items():
        set_node_attribute(node, public_name, value)
