import sys, os
import time
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType, NodeState
from core.print_node_info import print_node_info

fruits = [
   "1_apple", "2_banana", "3_cherry", "4_date", 
   "5_elderberry", "6_fig", "7_grape", "8_honeydew",
   "9_imbe", "10_jackfruit", "11_kiwi", "12_lemon"
]

text_nodes = []
for fruit in fruits:
   node = Node.create_node(NodeType.TEXT, node_name=f"text_{fruit}")
   node._parms["text_string"].set(fruit)
   text_nodes.append(node)

merge = Node.create_node(NodeType.MERGE, node_name="merge")
split = Node.create_node(NodeType.SPLIT, node_name="split")
main_output = Node.create_node(NodeType.TEXT, node_name="main_output")
remainder_output = Node.create_node(NodeType.TEXT, node_name="remainder_output")

for i, node in enumerate(text_nodes):
   merge.set_input(i, node)
merge._parms["single_string"].set(False)

split.set_input(0, merge)

main_output.set_input(0, split)
remainder_output.set_input(1, split)

print("Connection indices:")
print(f"main_output input index: {main_output.inputs()[0].input_index()}")
print(f"remainder_output input index: {remainder_output.inputs()[0].input_index()}")

def verify_outputs(main_result, remainder_result, expected_main=None, expected_remainder=None):
    if expected_main is not None:
        assert main_result == expected_main, f"Main output mismatch. Expected {expected_main}, got {main_result}"
    if expected_remainder is not None:
        assert remainder_result == expected_remainder, f"Remainder output mismatch. Expected {expected_remainder}, got {remainder_result}"
    return True

def run_split_test(expr: str, description: str, expected_main=None, expected_remainder=None):
    print(f"\n#Test: {description}")
    print(f"Expression: {expr}")
    
    split._parms["split_expr"].set(expr)
    
    # Force evaluate the split node first
    split_result = split.eval()
    print(f"Split direct eval result: {split_result}")
    
    main_result = main_output.eval()
    remainder_result = remainder_output.eval()
    
    try:
        verify_outputs(main_result, remainder_result, expected_main, expected_remainder)
        print("🆗 Test PASSED!")
    except AssertionError as e:
        print(f"❌ Test FAILED!: {str(e)}")
    
    print(f"$Main Output: {main_result}")
    print(f"$Remainder Output: {remainder_result}")
    print(f"$Cook Count: {split._cook_count}")
    print(f"$Cook Time: {split._last_cook_time:.2f}ms\n")

if __name__ == "__main__":
    print("\n=== Basic List Operations ===")
    run_split_test("[0]", "Single item (first)",
               expected_main=["1_apple"],
               expected_remainder=fruits[1:])

    run_split_test("[-1]", "Single item (last)",
               expected_main=["12_lemon"],
               expected_remainder=fruits[:-1])

    run_split_test("[1:5]", "Slice (items 2-5)",
               expected_main=fruits[1:5],
               expected_remainder=fruits[:1] + fruits[5:])

    run_split_test("[::2]", "Every other item",
               expected_main=fruits[::2],
               expected_remainder=fruits[1::2])

    run_split_test("[1::3]", "Every third item starting at second",
               expected_main=fruits[1::3],
               expected_remainder=[f for i, f in enumerate(fruits) if (i-1) % 3 != 0])

    print("\n=== Random Operations ===")
    run_split_test("random(42)", "One random item (fixed seed)")
    run_split_test("random(42,3)", "Three random items (fixed seed)")
    run_split_test("random(time)", "Random item (time seed)")
    run_split_test("random(42,20)", "Random with count > list length")

    print("\n=== Edge Cases ===")
    run_split_test("", "Empty expression (should pass through)",
               expected_main=fruits,
               expected_remainder=[''])

    run_split_test("invalid_expr", "Invalid expression (should pass through)",
               expected_main=fruits,
               expected_remainder=[''])

    run_split_test("[999]", "Out of bounds index",
               expected_main=[''],
               expected_remainder=fruits)

    run_split_test("[5:2]", "Empty slice selection",
               expected_main=[''],
               expected_remainder=fruits)

    run_split_test("random(42)[1:3]", "Mixed format expression",
               expected_main=fruits,
               expected_remainder=[''])

    print("\n=== Dependency Chain Tests ===")
    merge._parms["single_string"].set(True)
    run_split_test("[0]", "Testing merge parameter change propagation")
    merge._parms["single_string"].set(False)

    print("\n=== Error Conditions ===")
    print("Testing disabled state")
    split._parms["enabled"].set(False)
    error_result = main_output.eval()
    print(f"$Disabled Output: {error_result}")
    split._parms["enabled"].set(True)

    print("\nTesting input modification")
    text_nodes[0]._parms["text_string"].set("modified_1_apple")
    run_split_test("[0:3]", "Testing dependency chain update",
               expected_main=["modified_1_apple", "2_banana", "3_cherry"],
               expected_remainder=fruits[3:])

    print("\nTesting state transitions")
    initial_state = split.state()
    split._parms["split_expr"].set("[0:2]")
    cooking_state = split.state()
    main_output.eval()
    final_state = split.state()

    print(f"$Initial State: {initial_state}")
    print(f"$Cooking State: {cooking_state}")
    print(f"$Final State: {final_state}")

    print("\n#Node Information:")
    print_node_info(split)