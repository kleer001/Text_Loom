#!/usr/bin/env python3
"""
Simplified test to verify that node positions work with migration pattern.
"""
import sys
import os
sys.path.insert(0, '/home/user/Text_Loom/src')

from core.base_classes import NodeEnvironment, Node, NodeType
from core.flowstate_manager import save_flowstate, load_flowstate, NODE_ATTRIBUTES


def prepare_nodes_for_save():
    """Copy private attributes to public ones before saving."""
    skip_attrs = {'name', 'path', 'session_id', 'node_type'}
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if not node:
            continue
        for attr in NODE_ATTRIBUTES:
            if attr in skip_attrs:
                continue
            private_attr_name = f'_{attr}'
            if hasattr(node, private_attr_name):
                private_value = getattr(node, private_attr_name)
                if private_value is not None and not callable(private_value):
                    setattr(node, attr, private_value)


def cleanup_temp_attributes():
    """Remove temporary public attributes after saving."""
    skip_attrs = {'name', 'path', 'session_id', 'node_type'}
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if not node:
            continue
        for attr in NODE_ATTRIBUTES:
            if attr in skip_attrs:
                continue
            if hasattr(node, attr) and hasattr(node, f'_{attr}'):
                try:
                    delattr(node, attr)
                except AttributeError:
                    pass


def migrate_node_attributes():
    """Migrate public attributes to private ones after loading."""
    skip_attrs = {'name', 'path', 'session_id', 'node_type'}
    for path in NodeEnvironment.list_nodes():
        node = NodeEnvironment.node_from_name(path)
        if not node:
            continue
        for attr in NODE_ATTRIBUTES:
            if attr in skip_attrs:
                continue
            public_attr = getattr(node, attr, None)
            if public_attr is None or callable(public_attr):
                continue
            if hasattr(node, f'_{attr}'):
                if attr in ('position', 'color') and isinstance(public_attr, list):
                    public_attr = tuple(public_attr)
                setattr(node, f'_{attr}', public_attr)
                delattr(node, attr)
        if isinstance(node._node_type, str):
            node._node_type = getattr(NodeType, node._node_type.split('.')[-1].upper())


print("=" * 60)
print("Testing Position Persistence with Migration")
print("=" * 60)

env = NodeEnvironment.get_instance()
env.nodes.clear()

print("\n1. Creating nodes...")
text1 = Node.create_node(NodeType.TEXT, node_name="text1")
text1._position = (100.0, 200.0)
text1._color = (1.0, 0.0, 0.0)
text1._selected = True

print(f"   Position before save: {text1._position}")

print("\n2. Preparing for save...")
prepare_nodes_for_save()

print("\n3. Saving...")
save_flowstate("/tmp/test_migration.json")

cleanup_temp_attributes()
print("   Cleaned up temp attributes")

print("\n4. Verifying save data...")
import json
with open("/tmp/test_migration.json", 'r') as f:
    data = json.load(f)
    node_data = data["nodes"]["/text1"]
    print(f"   'position' in data: {'position' in node_data}")
    print(f"   'color' in data: {'color' in node_data}")
    print(f"   'selected' in data: {'selected' in node_data}")
    if 'position' in node_data:
        print(f"   Saved position: {node_data['position']}")

print("\n5. Clearing and reloading...")
env.nodes.clear()
load_flowstate("/tmp/test_migration.json")

print("\n6. Migrating attributes...")
migrate_node_attributes()

print("\n7. Verifying loaded data...")
text1_loaded = NodeEnvironment.node_from_name("/text1")
print(f"   Loaded position: {text1_loaded._position}")
print(f"   Loaded color: {text1_loaded._color}")
print(f"   Loaded selected: {text1_loaded._selected}")

assert text1_loaded._position == (100.0, 200.0), f"Position mismatch!"
assert text1_loaded._color == (1.0, 0.0, 0.0), f"Color mismatch!"
assert text1_loaded._selected == True, f"Selected mismatch!"

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
