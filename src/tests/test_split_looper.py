import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info

fruits = [
    "1_apple", "2_banana", "3_cherry", "4_date",
    "5_elderberry", "6_fig", "7_grape", "8_honeydew"
]

def setup_test_nodes(split_expr: str = "random(time)", connect_to_main: bool = True):
    text_nodes = []
    for fruit in fruits:
        node = Node.create_node(NodeType.TEXT, node_name=f"text_{fruit}")
        node._parms["text_string"].set(fruit)
        text_nodes.append(node)
    
    looper = Node.create_node(NodeType.LOOPER, node_name="looper1")
    merge = Node.create_node(NodeType.MERGE, node_name="merge1", parent_path="/looper1")
    split = Node.create_node(NodeType.SPLIT, node_name="split1", parent_path="/looper1")
    
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

def run_test(name: str, split_expr: str, connect_to_main: bool = True):
    print(f"\n=== Test: {name} ===")
    print(f"Split Expression: {split_expr}")
    print(f"Connected to: {'Main' if connect_to_main else 'Remainder'} output")
    
    looper, split = setup_test_nodes(split_expr, connect_to_main)
    
    print("\nInitial loop evaluation:")
    result = looper.eval()
    print(f"Result length: {len(result)}")
    
    for i, iteration_output in enumerate(result, 1):
        print(f"\nIteration {i} output: {iteration_output}")
        print_split_outputs(split)
    
    print("\nFinal loop result:", result)
    print("\nSplit node info:")
    print("Cook count:", split._cook_count)
    print("Last cook time:", f"{split._last_cook_time:.2f}ms")
    
    return result

print("\n=== Testing Time-based Random Splits ===")
results_main = run_test("Random Split - Main Output", "random(time,2)")

print("\n=== Testing Time-based Random Splits with Remainder ===")
results_remainder = run_test("Random Split - Remainder Output", "random(time,2)", False)

print("\n=== Testing Fixed Pattern Split ===")
results_fixed = run_test("Fixed Split [1:3]", "[1:3]")

print("\n=== Testing Single Item Split ===")
results_single = run_test("Single Item Split [0]", "[0]")

print("\n=== Verifying Different Results ===")
print("\nChecking if random splits were different across iterations:")
if len(results_main) > 1:
    all_same = all(r == results_main[0] for r in results_main)
    print(f"All iterations produced different results: {'No' if all_same else 'Yes'}")

print("\nChecking output accumulation:")
print(f"Total outputs collected: {len(results_main)}")
expected_iterations = 3  # Default loop count
print(f"Matches expected iteration count: {len(results_main) == expected_iterations}")