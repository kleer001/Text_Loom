from typing import Any, Dict, List, Optional, Set
from pathlib import Path, PurePosixPath
from datetime import datetime
import json
from core.base_classes import NodeEnvironment, Node, NodeConnection, NodeType
from core.global_store import GlobalStore
from core.parm import Parm, ParameterType
import traceback
import inspect


"""
Manages the serialization and deserialization of node-based workflows in Text Loom.

This module provides functionality to save and load the complete state of a node graph,
including node attributes, parameters, connections, and global variables. It handles
the conversion of complex node objects and their relationships into JSON-serializable
format and back.

Key components:
- NodeEncoder: Custom JSON encoder for Node objects and related types
- save_flowstate(): Saves the current node environment to a JSON file
- load_flowstate(): Restores a node environment from a JSON file
- Helper functions for serializing/deserializing individual nodes, parameters, and connections

The module ensures data integrity through careful error handling and maintains
backwards compatibility through version tracking. Internal nodes (e.g., those created
by Looper nodes) are handled specially during the save/load process.

Version: 0.01
"""

SOFTWARE_NAME = "Text Loom"
VERSION = 0.01

NODE_ATTRIBUTES = [
    '_name', '_path', '_selected', '_color', '_position', '_session_id', '_node_type',
    '_children', '_depth', '_inputs', '_outputs', '_state', '_errors', '_warnings',
    '_is_time_dependent', '_last_cook_time', '_cook_count', '_file_hash',
    '_param_hash', '_last_input_size', '_input_node', '_output_node',
    '_internal_nodes_created', '_parent_looper'
]

PARM_ATTRIBUTES = ['name', 'type', 'node', 'script_callback', 'value']


class NodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            return {
                "_type": "Node",
                "path": str(obj.path()),
                "name": obj.name()
            }
        if isinstance(obj, PurePosixPath):
            return str(obj)
        if isinstance(obj, NodeType):
            return obj.value
        if _is_method_or_callable(obj):
            return None
        return super().default(obj)

def _is_method_or_callable(obj: Any) -> bool:
    return (inspect.ismethod(obj) or 
        inspect.isfunction(obj) or 
        callable(obj) or 
        isinstance(obj, (type, property)))

def _clean_for_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _clean_for_json(v) for k, v in obj.items() 
                if not _is_method_or_callable(v)}
    elif isinstance(obj, list):
        return [_clean_for_json(item) for item in obj 
                if not _is_method_or_callable(item)]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif _is_method_or_callable(obj):
        return None
    else:
        try:
            return json.loads(json.dumps(obj, cls=NodeEncoder))
        except:
            return str(obj)

def _apply_node_data(node: Node, node_data: dict) -> None:
    try:
        print(f"[DEBUG] _apply_node_data for {node.path()}")
        print(f"[DEBUG] BEFORE attr loop - node._node_type type: {type(node._node_type)}, value: {node._node_type}")

        for attr in NODE_ATTRIBUTES:
            if attr in node_data:
                value = node_data[attr]
                if not inspect.ismethod(getattr(node, attr, None)):
                    if attr == '_node_type':
                        print(f"[DEBUG] About to set _node_type to: {value} (type: {type(value)})")
                    setattr(node, attr, value)
                    if attr == '_node_type':
                        print(f"[DEBUG] After setattr - node._node_type type: {type(node._node_type)}, value: {node._node_type}")

        print(f"[DEBUG] AFTER attr loop - node._node_type type: {type(node._node_type)}, value: {node._node_type}")

        # Fix _node_type if the attribute loop overwrote the enum with a string
        # The node was created with the correct enum, but JSON has it as a string
        if isinstance(node._node_type, str):
            print(f"[DEBUG] FIXING _node_type from string to enum")
            node_type_str = node._node_type
            node_enum = getattr(NodeType, node_type_str.split('.')[-1].upper())
            print(f"[DEBUG] Setting node._node_type = {node_enum} (type: {type(node_enum)})")
            node._node_type = node_enum
            print(f"[DEBUG] AFTER FIX - node._node_type type: {type(node._node_type)}, value: {node._node_type}")
        else:
            print(f"[DEBUG] No fix needed, _node_type is already correct type: {type(node._node_type)}")

        if '_parms' in node_data and hasattr(node, '_parms'):
            for parm_name, parm_data in node_data['_parms'].items():
                try:
                    node._parms[parm_name] = _deserialize_parm(parm_data, node)
                except Exception as e:
                    print(f"Error deserializing parm {parm_name}")
                    traceback.print_exc()
                    continue
    except Exception as e:
        print(f"Error applying node data to {node.path()}")
        traceback.print_exc()

def _serialize_parm(parm: Parm) -> dict:
    try:
        return {
            "_name": parm._name,
            "_type": parm._type.value,
            "_node": str(parm._node.path()) if parm._node else None,
            "_script_callback": parm._script_callback,
            "_value": parm._value
        }
    except Exception as e:
        print(f"Error in _serialize_parm")
        traceback.print_exc()
        return {}

def _deserialize_parm(parm_data: dict, node: Node) -> Parm:
    try:
        parm_type = ParameterType(parm_data["_type"])
        parm = Parm(parm_data["_name"], parm_type, node)
        parm._script_callback = parm_data["_script_callback"]
        parm._value = parm_data["_value"]
        return parm
    except Exception as e:
        print(f"Error in _deserialize_parm")
        traceback.print_exc()
        raise


def _serialize_node(node: Node) -> dict:
    try:
        node_data = {
            "_node_type": node.type().value,
            "_path": str(node.path()),
            "_name": node.name(),
            "_is_internal": hasattr(node, '_parent_looper') and bool(node._parent_looper)
        }
        
        for attr in NODE_ATTRIBUTES:
            try:
                if hasattr(node, attr):
                    value = getattr(node, attr)
                    if not _is_method_or_callable(value):
                        node_data[attr] = _clean_for_json(value)
            except Exception as e:
                print(f"Error serializing attribute {attr} for node {node.path()}")
                traceback.print_exc()
                continue
        
        if hasattr(node, '_parms'):
            node_data['_parms'] = {}
            for name, parm in node._parms.items():
                try:
                    if not _is_method_or_callable(parm):
                        node_data['_parms'][name] = _serialize_parm(parm)
                except Exception as e:
                    print(f"Error serializing parm {name} for node {node.path()}")
                    traceback.print_exc()
                    continue
        
        if hasattr(node, '_inputs'):
            node_data['_connections'] = []
            for input_idx, connection in node._inputs.items():
                try:
                    if connection and connection.output_node():
                        conn_data = {
                            "input_index": input_idx,
                            "output_node_path": str(connection.output_node().path()),
                            "input_node_path": str(node.path()),
                            "output_index": connection.output_index()
                        }
                        node_data['_connections'].append(_clean_for_json(conn_data))
                except Exception as e:
                    print(f"Error serializing connection {input_idx} for node {node.path()}")
                    traceback.print_exc()
                    continue
        
        return node_data
        
    except Exception as e:
        print(f"Error in _serialize_node for {node.path()}")
        traceback.print_exc()
        return {}

def _deserialize_node(node_data: dict, env: NodeEnvironment) -> Optional[Node]:
    try:
        node_type = node_data.get("_node_type")
        if not node_type:
            return None

        node_name = Path(node_data["_path"]).name
        parent_path = str(Path(node_data["_path"]).parent)
        node_enum = getattr(NodeType, node_type.split('.')[-1].upper())

        node = Node.create_node(node_enum, node_name, parent_path)
        print("CREATED NODE : ", node)
        if not node:
            return None

        # DEBUG: Check type BEFORE attribute restoration
        print(f"[DEBUG] BEFORE attr loop - node._node_type type: {type(node._node_type)}, value: {node._node_type}")
        print(f"[DEBUG] node_enum type: {type(node_enum)}, value: {node_enum}")

        for attr in NODE_ATTRIBUTES:
            try:
                if attr in node_data:
                    value = node_data[attr]
                    if not inspect.ismethod(getattr(node, attr, None)):
                        if attr == '_node_type':
                            print(f"[DEBUG] About to set _node_type to: {value} (type: {type(value)})")
                        setattr(node, attr, value)
                        if attr == '_node_type':
                            print(f"[DEBUG] After setattr - node._node_type type: {type(node._node_type)}, value: {node._node_type}")
            except Exception as e:
                print(f"Error deserializing attribute {attr}")
                traceback.print_exc()
                continue

        # DEBUG: Check type AFTER attribute restoration
        print(f"[DEBUG] AFTER attr loop - node._node_type type: {type(node._node_type)}, value: {node._node_type}")

        # Fix _node_type if the attribute loop overwrote the enum with a string
        # Node.create_node() correctly sets it as NodeType enum, but the JSON has it as a string
        if isinstance(node._node_type, str):
            print(f"[DEBUG] FIXING _node_type from string to enum")
            print(f"[DEBUG] Setting node._node_type = {node_enum} (type: {type(node_enum)})")
            node._node_type = node_enum
            print(f"[DEBUG] AFTER FIX - node._node_type type: {type(node._node_type)}, value: {node._node_type}")
        else:
            print(f"[DEBUG] No fix needed, _node_type is already correct type: {type(node._node_type)}")

        if '_parms' in node_data and hasattr(node, '_parms'):
            for parm_name, parm_data in node_data['_parms'].items():
                try:
                    node._parms[parm_name] = _deserialize_parm(parm_data, node)
                except Exception as e:
                    print(f"Error deserializing parm {parm_name}")
                    traceback.print_exc()
                    continue

        # FINAL VERIFICATION
        print(f"[DEBUG] === FINAL STATE for {node.path()} ===")
        print(f"[DEBUG] node._node_type type: {type(node._node_type)}, value: {node._node_type}")
        print(f"[DEBUG] node.type() returns: {node.type()} (type: {type(node.type())})")
        print(f"[DEBUG] === END FINAL STATE ===")

        return node

    except Exception as e:
        print(f"Error in _deserialize_node {e}")
        traceback.print_exc()
        return None



def _restore_connections(node: Node, connections_data: List[dict]) -> None:
    for conn_data in connections_data:
        try:
            output_node = NodeEnvironment.node_from_name(conn_data["output_node_path"])
            if not output_node:
                continue
            
            input_idx = int(conn_data["input_index"])
            output_idx = int(conn_data["output_index"])
            node.set_input(input_idx, output_node, output_idx)
            
        except Exception as e:
            print(f"Error restoring connection {e}")
            traceback.print_exc()


def save_flowstate(filepath: str) -> bool:
    try:
        env = NodeEnvironment.get_instance()
        save_data = {
            "software": SOFTWARE_NAME,
            "version": VERSION,
            "timestamp": datetime.now().isoformat(),
            "nodes": {},
            "globals": {}
        }
        
        sorted_nodes = sorted(env.nodes.items(), key=lambda x: len(str(x[0]).split('/')))
        
        for node_path, node in sorted_nodes:
            try:
                save_data["nodes"][str(node_path)] = _serialize_node(node)
            except Exception as e:
                print(f"Error saving node {node_path}")
                traceback.print_exc()
                continue
        
        try:
            global_store = GlobalStore()
            save_data["globals"] = _clean_for_json(global_store.list())
        except Exception as e:
            print(f"Error saving state {e}")
            traceback.print_exc()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, cls=NodeEncoder, indent=2)
        
        print("💾 Flowstate saved 💾 ")
        return True
        
    except Exception as e:
        print(f"Error saving flowstate {e}")
        traceback.print_exc()
        return False
    
def load_flowstate(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        env = NodeEnvironment.get_instance()
        NodeEnvironment.nodes.clear()
        
        sorted_nodes = sorted(save_data["nodes"].items(), key=lambda x: len(x[0].split('/')))
        for node_path, node_data in sorted_nodes:
            if node_data.get("_is_internal", False):
                continue
                
            try:
                node = _deserialize_node(node_data, env)
                if not node:
                    print(f"Failed to create node {node_path}")
                    continue
                
                if node.type() == NodeType.LOOPER and node._internal_nodes_created:
                    input_path = str(node.input_node.path())
                    output_path = str(node.output_node.path())
                    
                    if input_path in save_data["nodes"]:
                        _apply_node_data(node.input_node, save_data["nodes"][input_path])
                    if output_path in save_data["nodes"]:
                        _apply_node_data(node.output_node, save_data["nodes"][output_path])
                    
            except Exception as e:
                print(f"Error creating node {node_path}")
                traceback.print_exc()
                continue
        
        for node_path, node_data in save_data["nodes"].items():
            try:
                if '_connections' not in node_data:
                    continue
                    
                current_node = NodeEnvironment.node_from_name(node_path)
                if current_node:
                    _restore_connections(current_node, node_data['_connections'])
            except Exception as e:
                print(f"Error restoring connections for node {node_path}")
                traceback.print_exc()
                continue
        
        try:
            if "globals" in save_data:
                global_store = GlobalStore()
                for key, value in save_data["globals"].items():
                    global_store.set(key, value)
            
        except Exception as e:
            print(f"Error restoring state {e}")
            traceback.print_exc()
        
        print("💾 Flowstate Loaded 💾 ")
        return True
        
    except Exception as e:
        print(f"Error loading flowstate {e}")
        traceback.print_exc()
        return False