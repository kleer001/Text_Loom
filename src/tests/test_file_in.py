import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState
from core.print_node_info import print_node_info

test_cases = [
    ('basic.txt', '["a", "b", "c"]'),
    ('quotes.txt', '["double\\"quote", \'single\\\'quote\', "mixed\'quotes"]'),
    ('empty.txt', '["", "empty", "", "items"]'),
    ('escaped.txt', '["escaped\\\\backslash", "escaped\\,comma"]'),
    ('nested.txt', '["[nested]", "list"]'),
    ('invalid.txt', 'not a list at all'),
    ('malformed.txt', '["unclosed'),
]

file_in = Node.create_node(NodeType.FILE_IN, node_name="file_in_1")
null_node = Node.create_node(NodeType.NULL, node_name="null_1")
merge_node = Node.create_node(NodeType.MERGE, node_name="merge_1")

print("\nSetting up node connections...")
null_node.set_input("input", file_in, "output")
merge_node.set_input(0, null_node)

merge_node._parms["single_string"].set(False)

for filename, content in test_cases:
    test_path = os.path.abspath(filename)
    with open(test_path, "w") as f:
        f.write(content)
    
    print(f"\n=== Testing: {filename} ===")
    print(f"Input content: {content}")
    
    file_in._parms["file_name"].set(test_path)
    
    file_in.set_state(NodeState.UNCOOKED)
    null_node.set_state(NodeState.UNCOOKED)
    merge_node.set_state(NodeState.UNCOOKED)
    
    file_in_output = file_in.eval()
    print(f"FileIn output: {file_in_output}")
    
    null_output = null_node.eval()
    print(f"Null output: {null_output}")
    
    merge_output = merge_node.eval()
    print(f"Merge output: {merge_output}")
    
    os.remove(test_path)

print("\n=== Test Complete ===")