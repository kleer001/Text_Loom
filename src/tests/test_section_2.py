import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType
from core.section_node import SectionNode

def test_regex_section():
    print("\n=== Setting up nodes ===")
    input_node = Node.create_node(NodeType.TEXT, node_name="input_text")
    section = Node.create_node(NodeType.SECTION, node_name="section")
    out1 = Node.create_node(NodeType.TEXT, node_name="first_out")
    out2 = Node.create_node(NodeType.TEXT, node_name="second_out")
    out3 = Node.create_node(NodeType.TEXT, node_name="unmatched_out")

    print("\n=== Setting up connections ===")
    section.set_input(0, input_node)
    out1.set_input(0, section, output_index=0)
    out2.set_input(0, section, output_index=1)
    out3.set_input(0, section, output_index=2)

    test_input = [
        "Speaker1: Hello there",
        "speaker2: Hi back",
        "SPEAKER3: Greetings",
        "Speaker4 Hello",
        "Random line",
        "speaker5: Bye",
        "NotASpeaker: Something",
        "Speaker6:Farewell"
    ]

    print("\n=== Test Input ===")
    print("Setting input text:")
    for i, line in enumerate(test_input):
        print(f"Line {i}: '{line}'")
    input_node._parms["text_string"].set(str(test_input))

    print("\n=== Regex Section Test ===")
    # Using case-insensitive match for "speaker" followed by a number and colon
    section._parms["prefix1"].set("^(?i)speaker[0-9]+:")
    # Using case-insensitive match for "not" followed by any characters and colon
    section._parms["prefix2"].set("^(?i)not.*:")
    section._parms["trim_prefix"].set(True)
    
    print("Current section node parameters:")
    print(f"Enabled: {section._parms['enabled'].eval()}")
    print(f"Prefix1: '{section._parms['prefix1'].eval()}'")
    print(f"Prefix2: '{section._parms['prefix2'].eval()}'")
    print(f"Trim prefix: {section._parms['trim_prefix'].eval()}")

    print("\nEvaluating outputs...")
    result1 = out1.eval()
    print(f"Output 1 direct result: {result1}")
    result2 = out2.eval()
    print(f"Output 2 direct result: {result2}")
    result3 = out3.eval()
    print(f"Output 3 direct result: {result3}")

    # Expected results after prefix trimming
    expected1 = ["Hello there", "Hi back", "Greetings", "Bye", "Farewell"]
    expected2 = ["Something"]
    expected3 = ["Speaker4 Hello", "Random line"]

    def verify(actual, expected, name):
        if actual == expected:
            print(f"\n✅ {name} PASSED")
            print(f"Expected: {expected}")
            print(f"Got: {actual}")
        else:
            print(f"\n❌ {name} FAILED")
            print(f"Expected: {expected}")
            print(f"Got: {actual}")
            print("Differences:")
            print(f"Length expected: {len(expected)}, got: {len(actual)}")
            if len(expected) == len(actual):
                for i, (exp, act) in enumerate(zip(expected, actual)):
                    if exp != act:
                        print(f"Mismatch at index {i}:")
                        print(f"Expected: '{exp}'")
                        print(f"Got: '{act}'")

    verify(result1, expected1, "Speaker Output")
    verify(result2, expected2, "Not Output")
    verify(result3, expected3, "Unmatched Output")

if __name__ == "__main__":
    test_regex_section()