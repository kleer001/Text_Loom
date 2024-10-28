import json
from typing import Any, Dict, List, Optional, Set
from pathlib import Path, PurePosixPath
import inspect
from datetime import datetime
from base_classes import NodeEnvironment, Node, NodeConnection, NodeType
from undo_manager import UndoManager
from global_store import GlobalStore
import traceback 
from parm import Parm, ParameterType

VERSION = 0.01

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
        return super().default(obj)

def _get_serializable_attrs(obj: Any) -> dict:
    attrs = {}
    for key, value in obj.__dict__.items():
        try:
            # Skip private attributes and known non-serializable types
            if key.startswith('__') or callable(value):
                continue
                
            if isinstance(value, (str, int, float, bool, type(None))):
                attrs[key] = value
            elif isinstance(value, (list, dict)):
                # Use the custom encoder for lists and dicts
                attrs[key] = json.loads(json.dumps(value, cls=NodeEncoder))
            elif isinstance(value, PurePosixPath):
                attrs[key] = str(value)
            elif isinstance(value, Node):
                attrs[key] = {
                    "_type": "Node",
                    "path": str(value.path()),
                    "name": value.name()
                }
            elif isinstance(value, NodeType):
                attrs[key] = value.value
            else:
                # For unknown types, store string representation
                attrs[key] = str(value)
        except Exception:
            continue
    return attrs

def _serialize_parm(parm: Parm) -> dict:
    return {
        "_name": parm._name,
        "_type": parm._type.value,
        "_script_callback": parm._script_callback,
        "_value": parm._value
    }

def _deserialize_parm(parm_data: dict, node: "Node") -> Parm:
    parm_type = ParameterType(parm_data["_type"])
    parm = Parm(parm_data["_name"], parm_type, node)
    parm._script_callback = parm_data["_script_callback"]
    parm._value = parm_data["_value"]
    return parm

def save_flowstate(filepath: str) -> bool:
    try:
        env = NodeEnvironment.get_instance()
        save_data = {
            "version": VERSION,
            "timestamp": datetime.now().isoformat(),
            "nodes": {},
            "globals": {},
            "undo_state": None
        }
        
        # Save nodes in topological order
        sorted_nodes = sorted(env.nodes.items(), key=lambda x: len(str(x[0]).split('/')))
        
        for node_path, node in sorted_nodes:
            try:
                # Get basic node data
                node_data = {
                    "_node_type": node.type().value,
                    "_path": str(node.path()),
                    "_name": node.name(),
                }
                
                # Add serializable attributes
                node_data.update(_get_serializable_attrs(node))
                
                # Handle parameters
                if hasattr(node, '_parms'):
                    node_data['_parms'] = {
                        name: _serialize_parm(parm)
                        for name, parm in node._parms.items()
                    }
                
                # Handle connections
                if hasattr(node, '_inputs'):
                    node_data['_connections'] = []
                    for input_idx, connection in node._inputs.items():
                        if connection and connection.output_node():
                            node_data['_connections'].append({
                                "input_index": input_idx,
                                "output_node_path": str(connection.output_node().path()),
                                "output_index": connection.output_index()
                            })
                
                save_data["nodes"][str(node_path)] = node_data
                
            except Exception as e:
                print(f"Warning: Failed to save node {node_path}: {str(e)}")
                traceback.print_exc()
                continue
        
        # Save globals
        try:
            global_store = GlobalStore()
            save_data["globals"] = global_store.list()
        except Exception as e:
            print(f"Warning: Failed to save globals: {str(e)}")
            
        # Save undo state
        try:
            undo_manager = UndoManager()
            save_data["undo_state"] = _get_serializable_attrs(undo_manager)
        except Exception as e:
            print(f"Warning: Failed to save undo state: {str(e)}")
        
        # Write to file using custom encoder
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, cls=NodeEncoder, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error saving flowstate: {str(e)}")
        traceback.print_exc()
        return False

def load_flowstate(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        file_version = save_data.get("version", 0)
        if file_version > VERSION:
            print(f"Warning: File version {file_version} is newer than current version {VERSION}")
        
        env = NodeEnvironment.get_instance()
        NodeEnvironment.nodes.clear()
        
        # First pass: Create nodes
        for node_path, node_data in sorted(save_data["nodes"].items(), key=lambda x: len(x[0].split('/'))):
            try:
                # Extract node type
                node_type = node_data.get("_node_type")
                if not node_type:
                    print(f"Warning: Missing node type for {node_path}")
                    continue
                
                # Create node
                node_name = Path(node_path).name
                parent_path = str(Path(node_path).parent)
                node_enum = getattr(NodeType, node_type.split('.')[-1].upper())
                
                new_node = Node.create_node(node_enum, node_name, parent_path)
                if not new_node:
                    print(f"Warning: Failed to create node {node_path}")
                    continue
                
                # Restore basic attributes
                for key, value in node_data.items():
                    if key not in ['_parms', '_connections', '_inputs', '_outputs']:
                        setattr(new_node, key, value)
                
                # Restore parameters
                if '_parms' in node_data and hasattr(new_node, '_parms'):
                    for parm_name, parm_data in node_data['_parms'].items():
                        new_node._parms[parm_name] = _deserialize_parm(parm_data, new_node)
                
            except Exception as e:
                print(f"Warning: Failed to load node {node_path}: {str(e)}")
                traceback.print_exc()
                continue
        
        # Second pass: Restore connections
        for node_path, node_data in save_data["nodes"].items():
            if '_connections' not in node_data:
                continue
                
            current_node = NodeEnvironment.node_from_name(node_path)
            if not current_node:
                continue
                
            for conn_data in node_data['_connections']:
                try:
                    output_node = NodeEnvironment.node_from_name(conn_data["output_node_path"])
                    if not output_node:
                        print(f"Warning: Could not find output node {conn_data['output_node_path']}")
                        continue
                    
                    input_idx = int(conn_data["input_index"])
                    output_idx = int(conn_data["output_index"])
                    current_node.set_input(input_idx, output_node, output_idx)
                    
                except Exception as e:
                    print(f"Warning: Failed to restore connection for {node_path}: {str(e)}")
                    traceback.print_exc()
        
        # Restore state
        try:
            if "globals" in save_data:
                global_store = GlobalStore()
                for key, value in save_data["globals"].items():
                    global_store.set(key, value)
                    
            if "undo_state" in save_data:
                undo_manager = UndoManager()
                for key, value in save_data["undo_state"].items():
                    setattr(undo_manager, key, value)
                    
        except Exception as e:
            print(f"Warning: Failed to restore state: {str(e)}")
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"Error loading flowstate: {str(e)}")
        traceback.print_exc()
        return False