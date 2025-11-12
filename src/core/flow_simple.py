from pathlib import Path
from typing import Dict, List, Any, Optional
from core.base_classes import NodeEnvironment, Node, NodeType
from core.global_store import GlobalStore
from core.parm import ParameterType

'''Handles serialization and deserialization of node-based workflows in a compact single-line format

Each line represents one of:
- V:<version> - Version identifier
- G:<key=value,...> - Global variables
- path:type{param=value,...}>target1,target2 - Node definition with connections

Lines are ordered to reflect data flow from source to destination. Later nodes in the file 
receive data from earlier nodes. Multiple target connections are comma-separated.

Example file:
    V:0.01
    G:LASTRUN=2024-02-11
    /text2:TEXT{text_string="World"}>/text1,/text3
    /text1:TEXT{text_string="Hello",pass_through=F}
    /text3:TEXT{text_string="!"}

Functions:
    save_flowstate(filepath: str) -> bool: Saves current node environment to file
    load_flowstate(filepath: str) -> bool: Restores node environment using two-pass loading

Format preserves human readability while maintaining node relationships and parameter values.
Node parameters are optional - only non-default values are stored. Parameters with double quotes
or commas are escaped automatically.

Raises:
    Exception: On file IO errors or invalid node/parameter data
'''


VERSION = "0.01"

def _serialize_value(value: Any, parm_type: ParameterType) -> str:
    if parm_type == ParameterType.STRING:
        escaped = str(value).replace('"', '\\"')
        return f'"{escaped}"'
    elif parm_type == ParameterType.STRINGLIST:
        escaped = [s.replace('"', '\\"').replace(',', '\\,') for s in value]
        quoted = [f'"{s}"' for s in escaped]
        return f'[{",".join(quoted)}]'
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
    if line.startswith("V:") or line.startswith("G:"):
        return {}
        
    path_part, *rest = line.split("{", 1)
    path, node_type = path_part.split(":")
    
    result = {
        "path": path,
        "type": node_type,
        "parms": {},
        "feeds_into": []
    }
    
    remaining = rest[0] if rest else ""
    if "}" in remaining:
        parm_part, *conn_part = remaining.split("}")
        if parm_part:
            pairs = parm_part.split(",")
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    result["parms"][key.strip()] = value.strip()
        
        if conn_part and ">" in conn_part[0]:
            targets = conn_part[0].split(">")[1]
            if targets:
                result["feeds_into"] = [x.strip() for x in targets.split(",")]
    
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
    
    connected_inputs = []
    for other_node in NodeEnvironment.get_instance().nodes.values():
        for input_conn in other_node._inputs.values():
            if input_conn and input_conn.output_node() == node:
                connected_inputs.append(other_node.path())
    
    if connected_inputs:
        parts.append(">" + ",".join(str(p) for p in connected_inputs))
    
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
        node_lines = []
        
        for node_path, node in sorted_nodes:
            node_str = _serialize_node(node)
            if node_str:
                node_lines.append(node_str)
        
        lines.extend(reversed(node_lines))
        
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
        node_data_list = []
        
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
            
            node_data = _parse_node_line(line)
            if node_data:
                node = _create_node_from_data(node_data)
                if node:
                    node_data_list.append((node, node_data))
        
        # Second pass: Restore connections
        for source_node, data in node_data_list:
            for target_path in data["feeds_into"]:
                target_node = env.node_from_name(target_path)
                if target_node:
                    target_node.set_next_input(source_node)
        
        return True
        
    except Exception as e:
        print(f"Error loading flow: {e}")
        return False