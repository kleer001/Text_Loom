# Re-export all symbols from new modular structure
from core.enums import NetworkItemType, NodeState, NodeType
from core.network_entity import NetworkEntity
from core.internal_path import InternalPath
from core.mobile_item import MobileItem
from core.node_connection import NodeConnection
from core.node_environment import (
    NodeEnvironment, 
    generate_node_types,
    OperationFailed
)
from core.node import Node, NodeState

# Re-export everything to maintain backward compatibility
__all__ = [
    'NetworkEntity',
    'NetworkItemType',
    'InternalPath',
    'MobileItem',
    'NodeConnection',
    'NodeEnvironment',
    'generate_node_types',
    'OperationFailed',
    'Node',
    'NodeState'
]

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "Importing directly from base_classes is deprecated. "
#     "Please import from the specific modules instead.",
#     DeprecationWarning,
#     stacklevel=2
# )