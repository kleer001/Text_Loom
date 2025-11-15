import importlib
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict
from core.base_classes import Node

logger = logging.getLogger(__name__)


def find_node_class(module):
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and
            issubclass(attr, Node) and
            attr != Node and
            hasattr(attr, 'GLYPH')):
            return attr
    return None


def load_node_module(file_stem: str):
    module_name = f"core.{file_stem}"
    if module_name in sys.modules:
        return sys.modules[module_name]
    return importlib.import_module(module_name)


def get_node_class(node_type: str):
    file_stem = f"{node_type}_node"
    module = load_node_module(file_stem)
    return find_node_class(module)


def discover_node_types(exclude: Optional[List[str]] = None) -> Dict[str, type]:
    if exclude is None:
        exclude = ['input_null', 'output_null']

    core_dir = Path(__file__).parent.parent / "core"
    node_types = {}

    for file in core_dir.glob("*_node.py"):
        node_type = file.stem.replace("_node", "")

        if node_type in exclude:
            continue

        try:
            node_class = get_node_class(node_type)
            if node_class:
                node_types[node_type] = node_class
        except (ImportError, AttributeError) as e:
            logger.debug(f"Could not load node type {node_type}: {e}")

    return node_types

