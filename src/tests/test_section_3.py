import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType

def test_wildcard_patterns():
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

        return all([
            verify(result1, expected1, "Output 1"),
            verify(result2, expected2, "Output 2"),
            verify(result3, expected3, "Output 3")
        ])

    tests = [
        {
            "description": "Simple wildcard matching",
            "input_list": [
                "Q: First question",
                "Query: Second question",
                "Question: Third question",
                "A: First answer",
                "Answer: Second answer"
            ],
            "prefix1": "Q*",
            "prefix2": "A*",
            "delimiter": ":",
            "expected1": ["First question", "Second question", "Third question"],
            "expected2": ["First answer", "Second answer"],
            "expected3": [""]
        },
        {
            "description": "Single character wildcard",
            "input_list": [
                "Bot1: Hello",
                "Bot2: Hi there",
                "Bot3: Greetings",
                "Human: Hey"
            ],
            "prefix1": "Bot?",
            "prefix2": "Human",
            "delimiter": ":",
            "expected1": ["Hello", "Hi there", "Greetings"],
            "expected2": ["Hey"],
            "expected3": [""]
        },
        {
            "description": "Mixed wildcards",
            "input_list": [
                "TestBot1: Message 1",
                "TestBot2: Message 2",
                "ChatBot: Message 3",
                "InfoBot: Message 4",
                "User: Response"
            ],
            "prefix1": "*Bot*",
            "prefix2": "User",
            "delimiter": ":",
            "expected1": ["Message 1", "Message 2", "Message 3", "Message 4"],
            "expected2": ["Response"],
            "expected3": [""]
        },
        {
            "description": "Wildcards with special characters",
            "input_list": [
                "Test.Bot: Data",
                "Test-Bot: Info",
                "Test_Bot: Status",
                "Other: Message"
            ],
            "prefix1": "Test?Bot",
            "prefix2": "Other",
            "delimiter": ":",
            "expected1": ["Data", "Info", "Status"],
            "expected2": ["Message"],
            "expected3": [""]
        },
        {
            "description": "Multiple consecutive wildcards",
            "input_list": [
                "ABC123XYZ: First",
                "ABCXYZ: Second",
                "ABC987XYZ: Third",
                "Other: Fourth"
            ],
            "prefix1": "ABC*XYZ",
            "prefix2": "Other",
            "delimiter": ":",
            "expected1": ["First", "Second", "Third"],
            "expected2": ["Fourth"],
            "expected3": [""]
        }
    ]

    success_count = 0
    for test in tests:
        if run_test(**test):
            success_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Passed {success_count} of {len(tests)} tests")

if __name__ == "__main__":
    test_wildcard_patterns()