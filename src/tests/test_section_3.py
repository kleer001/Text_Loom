import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType
from core.section_node import SectionNode

def test_shortcut_section():
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
        "INT. COFFEE SHOP - DAY",
        "DETECTIVE SMITH",
        "(looks around nervously)",
        "This is just regular dialogue",
        "FADE TO:",
        "EXT. STREET - NIGHT",
        "(checking phone)",
        "CUT TO:",
        "Random text here"
    ]

    print("\n=== Test Input ===")
    print("Setting input text:")
    for i, line in enumerate(test_input):
        print(f"Line {i}: '{line}'")
    input_node._parms["text_string"].set(str(test_input))

    print("\n=== Shortcut Section Test 1: Scene and Direction ===")
    section._parms["prefix1"].set("@scene")
    section._parms["prefix2"].set("@direction")
    section._parms["trim_prefix"].set(True)
    
    print("\nCurrent section node parameters:")
    print(f"Enabled: {section._parms['enabled'].eval()}")
    print(f"Prefix1: '{section._parms['prefix1'].eval()}'")
    print(f"Prefix2: '{section._parms['prefix2'].eval()}'")
    print(f"Trim prefix: {section._parms['trim_prefix'].eval()}")
    print(f"Regex file: '{section._parms['regex_file'].eval()}'")

    print("\nEvaluating outputs...")
    result1 = out1.eval()
    result2 = out2.eval()
    result3 = out3.eval()

    print(f"\nOutput 1 (Scenes): {result1}")
    print(f"Output 2 (Directions): {result2}")
    print(f"Output 3 (Unmatched): {result3}")

    expected1 = ["COFFEE SHOP - DAY", "STREET - NIGHT"]
    expected2 = ["(looks around nervously)", "(checking phone)"]
    expected3 = ["DETECTIVE SMITH", "This is just regular dialogue", "FADE TO:", "CUT TO:", "Random text here"]

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

    verify(result1, expected1, "Scene Output")
    verify(result2, expected2, "Direction Output")
    verify(result3, expected3, "Unmatched Output")

    print("\n=== Testing Invalid Shortcut ===")
    print(f"Debug: Current state before parameter change:")
    print(f"Enabled: {section._parms['enabled'].eval()}")
    print(f"Previous prefix1: {section._parms['prefix1'].eval()}")
    print(f"Previous prefix2: {section._parms['prefix2'].eval()}")
    
    section._parms["prefix1"].set("@nonexistent")
    section._parms["prefix2"].set("@character")
    
    print(f"\nDebug: State after parameter change:")
    print(f"New prefix1: {section._parms['prefix1'].eval()}")
    print(f"New prefix2: {section._parms['prefix2'].eval()}")
    
    #section.set_state(NodeState.UNCOOKED)  # Force a recook
    
    result1 = out1.eval()
    result2 = out2.eval()
    result3 = out3.eval()

if __name__ == "__main__":
    test_shortcut_section()