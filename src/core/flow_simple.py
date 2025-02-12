from pathlib import Path
from typing import Dict, List, Any, Optional
from core.base_classes import NodeEnvironment, Node, NodeType
from core.global_store import GlobalStore
from core.parm import ParameterType

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

def _deserialize_value(value: str, parm_type: ParameterType) -> Any:
    if parm_type == ParameterType.STRING:
        return value.strip('"').replace('\\"', '"')
    elif parm_type == ParameterType.STRINGLIST:
        if value.startswith('[') and value.endswith(']'):
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
        return []
    elif parm_type == ParameterType.INT:
        return int(value)
    elif parm_type == ParameterType.FLOAT:
        return float(value)
    elif parm_type == ParameterType.TOGGLE:
        return value == 'T'
    return value

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
        
        with open(filepath, "w", encoding="utf-8", errors="surrogateescape") as f:
            f.write("\n".join(lines))
        return True
        
    except Exception as e:
        print(f"Error saving flow: {e}")
        return False


def _serialize_node(node: Node) -> str:
    parts = [f"{node.path()}:{node.type().name}"]
    
    non_default_parms = {}
    for name, parm in node._parms.items():
        if not parm.is_default and parm.type() != ParameterType.BUTTON:
            non_default_parms[name] = _serialize_value(parm.raw_value(), parm.type())
    
    if non_default_parms:
        parm_str = ",".join(f"{k}={v}" for k, v in non_default_parms.items())
        parts.append(f"{{{parm_str}}}")
    
    inputs = []
    outputs = []
    
    for idx, input_conn in node._inputs.items():
        if input_conn and input_conn.output_node():
            inputs.append(input_conn.output_node().path())
            
    for other_node in NodeEnvironment.get_instance().nodes.values():
        for input_conn in other_node._inputs.values():
            if input_conn and input_conn.output_node() == node:
                outputs.append(other_node.path())
    
    if inputs:
        parts.append("<" + ",".join(str(p) for p in inputs))
    if outputs:
        parts.append(">" + ",".join(str(p) for p in outputs))
    
    return "".join(parts)

def _parse_node_line(line: str) -> Dict:
    path_part, *rest = line.split("{", 1)
    path, node_type = path_part.split(":")
    
    result = {
        "path": path,
        "type": node_type,
        "parms": {},
        "inputs": [],
        "outputs": []
    }
    
    if rest:
        parm_conn = rest[0]
        if "}" in parm_conn:
            parm_part, *conn_part = parm_conn.split("}")
            if parm_part:
                pairs = parm_part.split(",")
                for pair in pairs:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        result["parms"][key.strip()] = value.strip()
            
            if conn_part:
                conn_str = conn_part[0]
                if "<" in conn_str:
                    inputs = conn_str.split("<")[1].split(">")[0]
                    if inputs:
                        result["inputs"] = inputs.split(",")
                if ">" in conn_str:
                    outputs = conn_str.split(">")[-1]
                    if outputs:
                        result["outputs"] = outputs.split(",")
    
    return result

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
        
        connections = []
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines or not lines[0].startswith("V:"):
            return False
        
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
            node = _create_node_from_data(node_data)
            
            if node:
                if node_data["inputs"]:
                    connections.append((node, node_data["inputs"], True))
                if node_data["outputs"]:
                    connections.append((node, node_data["outputs"], False))
        
        for node, paths, is_input in connections:
            for path in paths:
                other_node = env.node_from_name(path.strip())
                if other_node:
                    if is_input:
                        node.set_next_input(other_node)
                    else:
                        other_node.set_next_input(node)
        
        return True
        
    except Exception as e:
        print(f"Error loading flow: {e}")
        return False