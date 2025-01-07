from enum import Enum
from pathlib import Path

_node_types = None

def generate_node_types():
    global _node_types
    if _node_types is None:
        node_types = {}
        # Look in the same directory as this file
        core_dir = Path(__file__).parent
        for file in core_dir.glob("*_node.py"):
            node_type_name = file.stem.replace("_node", "").upper()
            # Just store the base name, not the full path
            node_types[node_type_name] = file.stem.replace("_node", "")
        _node_types = node_types
    return _node_types

class NodeType(Enum):
    pass

NodeType = Enum("NodeType", generate_node_types(), type=NodeType)

class NetworkItemType(Enum):
    NODE = "node"
    CONNECTION = "connection"

class NodeState(Enum):
    COOKING = 'cooking'
    UNCHANGED = 'unchanged'
    UNCOOKED = 'uncooked'
    COOKED = 'cooked'
