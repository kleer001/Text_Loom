import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType

def test_edge_cases():
    def setup_nodes():
        input_node = Node.create_node(NodeType.TEXT, node_name="input_text")
        section = Node.create_node(NodeType.SECTION, node_name="section")
        out1 = Node.create_node(NodeType.TEXT, node_name="out1")
        out2 = Node.create_node(NodeType.TEXT, node_name="out2")
        out3 = Node.create_node(NodeType.TEXT, node_name="out3")

        section.set_input(0, input_node)
        out1.set_input(0, section, output_index=0)
        out2.set_input(0, section, output_index=1)
        out3.set_input(0, section, output_index=2)
        
        return input_node, section, out1, out2, out3

    def run_test(description: str, input_list: list, prefix1: str, prefix2: str, 
                delimiter: str, expected1: list, expected2: list, expected3: list):
        
        print(f"\n=== Test: {description} ===")
        print(f"Prefix1: '{prefix1}'")
        print(f"Prefix2: '{prefix2}'")
        print(f"Delimiter: '{delimiter}'")
        print("Input:")
        for line in input_list:
            print(f"  '{line}'")

        input_node, section, out1, out2, out3 = setup_nodes()
        
        section._parms["prefix1"].set(prefix1)
        section._parms["prefix2"].set(prefix2)
        section._parms["delimiter"].set(delimiter)
        input_node._parms["text_string"].set(str(input_list))

        print("\nEvaluating outputs...")
        print(f"Section node state before eval: {section.state()}")
        
        result1 = out1.eval()
        print(f"Output1 raw result: {result1}")
        
        result2 = out2.eval()
        print(f"Output2 raw result: {result2}")
        
        result3 = out3.eval()
        print(f"Output3 raw result: {result3}")
        
        print(f"\nSection node internal output lists: {section._output}")
        
        def verify(actual, expected, name):
            success = actual == expected
            print(f"\n{'✅' if success else '❌'} {name}")
            print(f"Expected: {expected}")
            print(f"Got: {actual}")
            if not success:
                print("Differences:")
                print(f"Length expected: {len(expected)}, got: {len(actual)}")
                for i, (exp, act) in enumerate(zip(expected, actual)):
                    if exp != act:
                        print(f"Mismatch at {i}:")
                        print(f"Expected: '{exp}'")
                        print(f"Got: '{act}'")
            return success

        success = (
            verify(result1, expected1, "Output 1") and
            verify(result2, expected2, "Output 2") and
            verify(result3, expected3, "Output 3")
        )
        return success

    tests = [
        {
            "description": "Empty input list",
            "input_list": [""],
            "prefix1": "A",
            "prefix2": "B",
            "delimiter": ":",
            "expected1": [""],
            "expected2": [""],
            "expected3": [""]
        },
        {
            "description": "Different delimiter (>)",
            "input_list": [
                "Speaker1> Hello",
                "Speaker2> Hi",
                "Random text"
            ],
            "prefix1": "Speaker1",
            "prefix2": "Speaker2",
            "delimiter": ">",
            "expected1": ["Hello"],
            "expected2": ["Hi"],
            "expected3": ["Random text"]
        },
        {
            "description": "Multiple spaces in prefix",
            "input_list": [
                "First    Speaker : Message",
                "Second   Speaker : Reply"
            ],
            "prefix1": "First Speaker",
            "prefix2": "Second Speaker",
            "delimiter": ":",
            "expected1": ["Message"],
            "expected2": ["Reply"],
            "expected3": [""]
        },
        {
            "description": "Prefix containing delimiter",
            "input_list": [
                "Mr:Smith: Hello",
                "Ms:Jones: Hi"
            ],
            "prefix1": "Mr:Smith",
            "prefix2": "Ms:Jones",
            "delimiter": ":",
            "expected1": ["Smith: Hello"],
            "expected2": ["Jones: Hi"],
            "expected3": [""]
        },
        {
            "description": "Multiple delimiters in line",
            "input_list": [
                "A: B: C: D",
                "X: Y: Z"
            ],
            "prefix1": "A",
            "prefix2": "X",
            "delimiter": ":",
            "expected1": ["B: C: D"],
            "expected2": ["Y: Z"],
            "expected3": [""]
        },
        {
            "description": "Just prefixes, no content",
            "input_list": [
                "A:",
                "B:",
                "C"
            ],
            "prefix1": "A",
            "prefix2": "B",
            "delimiter": ":",
            "expected1": [""],
            "expected2": [""],
            "expected3": ["C"]
        }
    ]

    success_count = 0
    for test in tests:
        if run_test(**test):
            success_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Passed {success_count} of {len(tests)} tests")

if __name__ == "__main__":
    test_edge_cases()