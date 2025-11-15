from core.base_classes import Node, NodeEnvironment, NodeState, NodeType
from core.global_store import GlobalStore
from core.flowstate_manager import save_flowstate, load_flowstate
from core.node_connection import NodeConnection
from utils.node_loader import discover_node_types, get_node_class


def build_namespace():
    namespace = {
        'Node': Node,
        'NodeEnvironment': NodeEnvironment,
        'NodeState': NodeState,
        'NodeType': NodeType,
        'NodeConnection': NodeConnection,
        'GlobalStore': GlobalStore,
        'save_flowstate': save_flowstate,
        'load_flowstate': load_flowstate,
        'get_node_class': get_node_class,
        'env': NodeEnvironment,
    }

    node_types = discover_node_types()
    for node_type, node_class in node_types.items():
        class_name = node_class.__name__
        namespace[class_name] = node_class

    return namespace
