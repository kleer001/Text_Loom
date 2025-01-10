import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info

fruits = [
    "1_apple", "2_banana", "3_cherry", "4_date",
    "5_elderberry", "6_fig", "7_pine", "8_lemon", "9_peace", "0_art"
]

def setup_test_nodes(split_expr: str = "random($$M*211)", connect_to_main: bool = True, cook_loops: bool = False):
    text_nodes = []
    for fruit in fruits:
        node = Node.create_node(NodeType.TEXT, node_name=f"text_{fruit}")
        node._parms["text_string"].set(fruit)
        text_nodes.append(node)
    
    looper = Node.create_node(NodeType.LOOPER, node_name="looper1")
    merge = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")
    split = Node.create_node(NodeType.SPLIT, node_name="split1", parent_path="/looper1")
    
    looper._parms["cook_loops"].set(cook_loops)
    split._parms["split_expr"].set(split_expr)
    
    for i, node in enumerate(text_nodes):
        merge.set_input(i, node)
    merge._parms["single_string"].set(False)
    
    split.set_input(0, merge)
    
    output_connection = 0 if connect_to_main else 1
    looper._output_node.set_input(0, split, output_connection)
    
    return looper, split

def print_split_outputs(split_node):
    print("\n=== Split Node Current Output State ===")
    full_output = split_node._output
    if isinstance(full_output, list) and len(full_output) >= 2:
        print("MAIN Output (index 0):", full_output[0])
        print("REMAINDER Output (index 1):", full_output[1])
    else:
        print("Unexpected split output format:", full_output)
    print("=====================================")

def run_test(name: str, split_expr: str, connect_to_main: bool = True, cook_loops: bool = False):
    print(f"\n=== Test: {name} ===")
    print(f"Split Expression: {split_expr}")
    print(f"Connected to: {'Main' if connect_to_main else 'Remainder'} output")
    print(f"Cook Loops: {cook_loops}")
    
    looper, split = setup_test_nodes(split_expr, connect_to_main, cook_loops)
    
    print("\nInitial loop evaluation:")
    result = looper.eval()
    print(f"Loop Result length: {len(result)}")
    print(f"Final Result: {result}")
    print_split_outputs(split)
    
    print("\nCook counts:")
    print(f"Split node: {split._cook_count}")
    print(f"Looper output node: {looper._output_node._cook_count}")
    
    return result

print("\n=== Testing with cook_loops=False ===")
results_no_cook = run_test(
    "Random Split - Main Output", 
    "random(42,5)", 
    connect_to_main=True, 
    cook_loops=False
)

print("\n=== Testing with cook_loops=True ===")
results_with_cook = run_test(
    "Random Split - Main Output", 
    "random(time,5)", 
    connect_to_main=True, 
    cook_loops=True
)

print("\n=== Testing Remainder with cook_loops=True ===")
results_remainder = run_test(
    "Random Split - Remainder Output", 
    "random(time,5)", 
    connect_to_main=False, 
    cook_loops=True
)

print("\n=== Verifying Cook Counts ===")
print("\nResults Summary:")
print(f"No Cook Results: {len(results_no_cook)} outputs")
print(f"With Cook Results: {len(results_with_cook)} outputs")
print(f"Remainder Results: {len(results_remainder)} outputs")