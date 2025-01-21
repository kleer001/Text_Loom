import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType
from core.section_node import SectionNode

def test_section_node():
    print("\n=== Setting up nodes ===")
    input_node = Node.create_node(NodeType.TEXT, node_name="input_text")
    section = Node.create_node(NodeType.SECTION, node_name="section")
    out1 = Node.create_node(NodeType.TEXT, node_name="interviewer_out")
    out2 = Node.create_node(NodeType.TEXT, node_name="participant_out")
    out3 = Node.create_node(NodeType.TEXT, node_name="unmatched_out")

    print("\n=== Setting up connections ===")
    section.set_input(0, input_node)
    out1.set_input(0, section, output_index=0)
    out2.set_input(0, section, output_index=1)
    out3.set_input(0, section, output_index=2)

    print("\nVerifying connections:")
    print(f"Section node input count: {len(section.inputs())}")
    print(f"Section node output count: {len(section._outputs)}")
    for idx, outputs in section._outputs.items():
        print(f"Output {idx} has {len(outputs)} connections")

    test_input = [
        "Interviewer: First question",
        "  Interviewer:Second question",
        "Participant: First answer",
        "Random line",
        "Interviewer:   Third question",
        "Participant: Second answer",
        "  Some other text  ",
        "Participant:Third answer"
    ]

    print("\n=== Test Input ===")
    print("Setting input text:")
    for i, line in enumerate(test_input):
        print(f"Line {i}: '{line}'")
    input_node._parms["text_string"].set(str(test_input))

    print("\n=== Basic Section Test ===")
    section._parms["prefix1"].set("Interviewer:")
    section._parms["prefix2"].set("Participant:")
    section._parms["trim_prefix"].set(True)
    #section._parms["regex_file"].set("regex.dat.json")
    
    print("Current section node parameters:")
    print(f"Enabled: {section._parms['enabled'].eval()}")
    print(f"Prefix1: '{section._parms['prefix1'].eval()}'")
    print(f"Prefix2: '{section._parms['prefix2'].eval()}'")
    print(f"Trim prefix: {section._parms['trim_prefix'].eval()}")
    #print(f"Regex file: '{section._parms['regex_file'].eval()}'")


    print("\nEvaluating outputs...")
    result1 = out1.eval()
    print(f"Output 1 direct result: {result1}")
    result2 = out2.eval()
    print(f"Output 2 direct result: {result2}")
    result3 = out3.eval()
    print(f"Output 3 direct result: {result3}")

    print("\nChecking section node internal state:")
    print(f"Section node state: {section.state()}")
    print(f"Section node cook count: {section._cook_count}")
    print(f"Section node output lists: {section._output}")

    # Expected results after prefix trimming
    expected1 = ["First question", "Second question", "Third question"]
    expected2 = ["First answer", "Second answer", "Third answer"]
    expected3 = ["Random line", "Some other text"]

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

    verify(result1, expected1, "Interviewer Output")
    verify(result2, expected2, "Participant Output")
    verify(result3, expected3, "Unmatched Output")

if __name__ == "__main__":
    test_section_node()