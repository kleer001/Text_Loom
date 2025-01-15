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

def test_format(use_format_output):
    file_in = Node.create_node(NodeType.FILE_IN, node_name="file_in_1")
    file_out = Node.create_node(NodeType.FILE_OUT, node_name="file_out_1")
    
    print(f"\nTesting with format_output={use_format_output}")
    file_out.set_input("input", file_in)
    file_out._parms["format_output"].set(use_format_output)

    for filename, content in test_cases:
        input_path = os.path.abspath(f"input_{filename}")
        output_path = os.path.abspath(f"output_{filename}")
        
        with open(input_path, "w") as f:
            f.write(content)
        
        print(f"\n=== Testing: {filename} ===")
        print(f"Original content: {content}")
        
        file_in._parms["file_name"].set(input_path)
        file_out._parms["file_name"].set(output_path)
        
        file_in.set_state(NodeState.UNCOOKED)
        file_out.set_state(NodeState.UNCOOKED)
        
        file_in_output = file_in.eval()
        print(f"FileIn parsed: {file_in_output}")
        
        file_out.eval()
        
        with open(output_path, 'r') as f:
            written_content = f.read()
        print(f"Written content: {written_content}")
        
        if not use_format_output:
            # Read it back in to verify roundtrip
            file_in._parms["file_name"].set(output_path)
            file_in.set_state(NodeState.UNCOOKED)
            roundtrip = file_in.eval()
            print(f"Roundtrip parse: {roundtrip}")
        
        os.remove(input_path)
        os.remove(output_path)

print("\n=== Testing with format_output=True ===")
test_format(True)

print("\n=== Testing with format_output=False ===")
test_format(False)