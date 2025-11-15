from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from core.base_classes import Node, NodeEnvironment, NodeType
from core.flowstate_manager import save_flowstate, load_flowstate
from core.global_store import GlobalStore
from utils.node_loader import discover_node_types


def create(node_type: str, name: Optional[str] = None, parent: str = '/', **params) -> Node:
    node_type_upper = node_type.upper()

    try:
        node_type_enum = getattr(NodeType, node_type_upper)
    except AttributeError:
        available = [t.name.lower() for t in NodeType]
        raise ValueError(f"Unknown node type: {node_type}. Available: {available}")

    node = Node.create_node(
        node_type=node_type_enum,
        node_name=name,
        parent_path=parent
    )

    if params and hasattr(node, '_parms'):
        for param_name, value in params.items():
            if param_name in node._parms:
                node._parms[param_name].set(value)

    return node


def connect(source: Node, target: Node,
            source_output: int = 0, target_input: int = 0) -> None:
    target.set_input(target_input, source, source_output)


def connect_next(source: Node, target: Node, source_output: int = 0) -> None:
    target.set_next_input(source, source_output)


def disconnect(node: Node, input_index: int) -> None:
    node.remove_input(input_index)


def destroy(node: Node) -> None:
    node.destroy()


def run(node: Node, force: bool = False) -> Any:
    node.cook(force=force)
    return node.get_output()


def inspect(node: Node) -> Dict[str, Any]:
    info = {
        'name': node.name(),
        'path': node.path(),
        'type': node.__class__.__name__,
        'state': node.state().name,
        'inputs': len(node.inputs()),
        'outputs': len(node.outputs()),
        'parameters': {},
        'connections': {
            'inputs': [],
            'outputs': []
        }
    }

    if hasattr(node, '_parms'):
        for parm_name, parm in node._parms.items():
            info['parameters'][parm_name] = parm.eval()

    for i, inp in enumerate(node.inputs()):
        if inp:
            info['connections']['inputs'].append({
                'index': i,
                'from': inp.output_node().path()
            })

    for i, out in enumerate(node.outputs()):
        if out:
            info['connections']['outputs'].append({
                'to': out.path(),
                'input_index': i
            })

    return info


def tree(root: Optional[str] = None) -> None:
    nodes = NodeEnvironment.list_nodes()

    if root:
        nodes = [n for n in nodes if n.startswith(root)]

    nodes.sort()

    for node_path in nodes:
        depth = node_path.count('/') - 1
        indent = '  ' * depth
        name = node_path.split('/')[-1] or '/'

        node = NodeEnvironment.node_from_name(node_path)
        node_type = node.__class__.__name__ if node else 'Unknown'

        print(f"{indent}{name} ({node_type})")


def ls() -> List[str]:
    return NodeEnvironment.list_nodes()


def find(name: str) -> Optional[Node]:
    return NodeEnvironment.node_from_name(name)


def load(filepath: str) -> None:
    load_flowstate(Path(filepath))


def save(filepath: str) -> None:
    save_flowstate(Path(filepath))


def clear() -> None:
    NodeEnvironment.flush_all_nodes()


def types() -> List[str]:
    node_types = discover_node_types()
    return sorted(node_types.keys())


def get_global(key: str) -> str:
    return GlobalStore.get(key)


def set_global(key: str, value: str) -> None:
    GlobalStore.set(key, value)


def globals_dict() -> Dict[str, str]:
    return GlobalStore.get_all()


def parm(node: Node, name: str, value: Optional[Any] = None) -> Union[Any, Node]:
    if not hasattr(node, '_parms') or name not in node._parms:
        raise ValueError(f"Node {node.name()} has no parameter '{name}'")

    if value is None:
        return node._parms[name].eval()

    node._parms[name].set(value)
    return node


def children(node: Node) -> List[Node]:
    return list(node.children())


def set_parent(node: Node, parent_path: str) -> None:
    node.set_parent(parent_path)


def errors(node: Node) -> List[str]:
    return list(node.errors())


def clear_errors(node: Node) -> None:
    node.clear_errors()


def warnings(node: Node) -> List[str]:
    return list(node.warnings())


def clear_warnings(node: Node) -> None:
    node.clear_warnings()


def input_names(node: Node) -> Dict[int, str]:
    return node.input_names()


def output_names(node: Node) -> Dict[int, str]:
    return node.output_names()


def node_type(node: Node) -> str:
    return node.type().name


def input_nodes(node: Node) -> List[Node]:
    return node.input_nodes()


def cook_count(node: Node) -> int:
    return node.cook_count()


def last_cook_time(node: Node) -> float:
    return node.last_cook_time()


def needs_to_cook(node: Node) -> bool:
    return node.needs_to_cook()


def is_time_dependent(node: Node) -> bool:
    return node.isTimeDependent()


def cook_dependencies(node: Node) -> List[Node]:
    return node.cook_dependencies()


def inputs_with_indices(node: Node, use_names: bool = False) -> List[tuple]:
    return list(node.inputs_with_indices(use_names=use_names))


def outputs_with_indices(node: Node, use_names: bool = False) -> List[tuple]:
    return list(node.outputs_with_indices(use_names=use_names))


def node_exists(path: str) -> bool:
    return NodeEnvironment.node_exists(path)


def rename(old_path: str, new_parent_path: str) -> tuple:
    return NodeEnvironment.update_node_path(old_path, new_parent_path)

