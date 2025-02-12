from pathlib import Path
from typing import Dict, List, Any, Optional
from core.base_classes import NodeEnvironment, Node, NodeType
from core.global_store import GlobalStore
from core.parm import ParameterType

'''Handles serialization and deserialization of node-based workflows in a compact single-line format.

This module provides a lightweight text-based format for saving and loading node graphs. 
Each line represents one of:
- V:<version> - Version identifier
- G:<key=value,...> - Global variables
- path:type{param=value,...} - Node definition
- C:input_node>output_node - Node connection

Functions:
    save_flowstate(filepath: str) -> bool: 
        Saves current node environment to file.
    
    load_flowstate(filepath: str) -> bool:
        Restores node environment from file using two-pass loading.

The format prioritizes human readability and quick manual editing while maintaining
all necessary node relationships and parameter values.

Example file:
    V:0.01
    G:last_run=2024-02-11
    /text1:TEXT{text_string="Hello",pass_through=F}
    /text2:TEXT{text_string="World"}
    C:/text2>/text1

Raises:
    Exception: On file IO errors or invalid node/parameter data
'''


VERSION = "0.01"

def _serialize_value(value: Any, parm_type: ParameterType) -> str:
    if parm_type == ParameterType.STRING:
        return f'"{str(value).replace('"', '\\"')}"'
    elif parm_type == ParameterType.STRINGLIST:
        escaped = [s.replace('"', '\\"').replace(',', '\\,') for s in value]
        return f'[{",".join(f'"{s}"' for s in escaped)}]'
    elif parm_type == ParameterType.INT:
        return str(int(value))
    elif parm_type == ParameterType.FLOAT:
        return str(float(value))
    elif parm_type == ParameterType.TOGGLE:
        return 'T' if value else 'F'
    return str(value)

def _parse_stringlist(value: str) -> List[str]:
    if not (value.startswith('[') and value.endswith(']')):
        return []
        
    items = []
    current = []
    escaped = False
    
    for char in value[1:-1]:
        if escaped:
            current.append(char)
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == ',' and not escaped:
            if current:
                items.append(''.join(current).strip().strip('"').replace('\\"', '"'))
                current = []
        else:
            current.append(char)
            
    if current:
        items.append(''.join(current).strip().strip('"').replace('\\"', '"'))
    return items

def _deserialize_value(value: str, parm_type: ParameterType) -> Any:
    if parm_type == ParameterType.STRING:
        return value.strip('"').replace('\\"', '"')
    elif parm_type == ParameterType.STRINGLIST:
        return _parse_stringlist(value)
    elif parm_type == ParameterType.INT:
        return int(value)
    elif parm_type == ParameterType.FLOAT:
        return float(value)
    elif parm_type == ParameterType.TOGGLE:
        return value == 'T'
    return value

def _parse_node_line(line: str) -> Dict:
    if line.startswith(("V:", "G:", "C:")):
        return {}
        
    path_part, *rest = line.split("{", 1)
    path, node_type = path_part.split(":")
    
    result = {
        "path": path,
        "type": node_type,
        "parms": {}
    }
    
    if rest:
        parm_part = rest[0]
        if "}" in parm_part:
            parm_part = parm_part.split("}")[0]
            if parm_part:
                pairs = parm_part.split(",")
                for pair in pairs:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        result["parms"][key.strip()] = value.strip()
    
    return result

def _serialize_node(node: Node) -> str:
    parts = [f"{node.path()}:{node.type().name}"]
    
    non_default_parms = {}
    for name, parm in node._parms.items():
        if not parm.is_default and parm.type() != ParameterType.BUTTON:
            non_default_parms[name] = _serialize_value(parm.raw_value(), parm.type())
    
    if non_default_parms:
        parm_str = ",".join(f"{k}={v}" for k, v in non_default_parms.items())
        parts.append(f"{{{parm_str}}}")
    
    return "".join(parts)

def save_flowstate(filepath: str) -> bool:
    try:
        env = NodeEnvironment.get_instance()
        lines = [f"V:{VERSION}"]
        
        global_store = GlobalStore()
        globals_dict = global_store.list()
        if globals_dict:
            globals_str = ",".join(f"{k}={v}" for k, v in globals_dict.items())
            lines.append(f"G:{globals_str}")
        
        sorted_nodes = sorted(env.nodes.items(), key=lambda x: len(str(x[0]).split("/")))
        
        for node_path, node in sorted_nodes:
            node_str = _serialize_node(node)
            if node_str:
                lines.append(node_str)
        
        for node_path, node in sorted_nodes:
            for input_idx, conn in node._inputs.items():
                if conn and conn.output_node():
                    lines.append(f"C:{node.path()}>{conn.output_node().path()}")
        
        with open(filepath, "w", encoding="utf-8", errors="surrogateescape") as f:
            f.write("\n".join(lines))
        return True
        
    except Exception as e:
        print(f"Error saving flow: {e}")
        return False
def _create_node_from_data(node_data: Dict) -> Optional[Node]:
    try:
        node_type = getattr(NodeType, node_data["type"])
        node_name = Path(node_data["path"]).name
        parent_path = str(Path(node_data["path"]).parent)
        
        node = Node.create_node(node_type, node_name, parent_path)
        if not node:
            return None
            
        for parm_name, parm_value in node_data["parms"].items():
            if parm_name in node._parms:
                parm = node._parms[parm_name]
                value = _deserialize_value(parm_value, parm.type())
                parm.set(value)
                
        return node
    except Exception as e:
        print(f"Error creating node: {e}")
        return None

def load_flowstate(filepath: str) -> bool:
    try:
        env = NodeEnvironment.get_instance()
        env.nodes.clear()
        
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines or not lines[0].startswith("V:"):
            return False
            
        # First pass: Create nodes
        for line in lines[1:]:
            if line.startswith("G:"):
                global_store = GlobalStore()
                globals_str = line[2:]
                if globals_str:
                    for pair in globals_str.split(","):
                        key, value = pair.split("=", 1)
                        global_store.set(key, value)
                continue
                
            if line.startswith("C:"):
                continue  # Skip connections on first pass
                
            node_data = _parse_node_line(line)
            _create_node_from_data(node_data)
        
        # Second pass: Restore connections
        for line in lines[1:]:
            if line.startswith("C:"):
                input_path, output_path = line[2:].split(">")
                input_node = env.node_from_name(input_path.strip())
                output_node = env.node_from_name(output_path.strip())
                if input_node and output_node:
                    input_node.set_next_input(output_node)
        
        return True
        
    except Exception as e:
        print(f"Error loading flow: {e}")
        return False