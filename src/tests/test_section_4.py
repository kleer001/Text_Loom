import sys, os
import json
import tempfile
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState
from core.section_node import SectionNode


def test_section_node():
    print("\n=== Setting up nodes ===")
    input_node = Node.create_node(NodeType.TEXT, node_name="input_text")
    section = Node.create_node(NodeType.SECTION, node_name="section")
    out1 = Node.create_node(NodeType.TEXT, node_name="out1")
    out2 = Node.create_node(NodeType.TEXT, node_name="out2")
    out3 = Node.create_node(NodeType.TEXT, node_name="unmatched")

    section.set_input(0, input_node)
    out1.set_input(0, section, output_index=0)
    out2.set_input(0, section, output_index=1)
    out3.set_input(0, section, output_index=2)

    test_cases = [
        {
            "name": "Basic shortcuts",
            "prefix1": "@scene",
            "prefix2": "@character",
            "input": [
                "INT. COFFEE SHOP - DAY",
                "DETECTIVE SMITH",
                "Regular dialog",
                "EXT. STREET - NIGHT",
                "SARAH PARKER",
                "More dialog"
            ],
            "expected1": ["COFFEE SHOP - DAY", "STREET - NIGHT"],
            "expected2": ["DETECTIVE SMITH", "SARAH PARKER"],
            "expected3": ["Regular dialog", "More dialog"]
        },
        {
            "name": "Mixed shortcuts and wildcards",
            "prefix1": "@direction",
            "prefix2": "Q*",
            "input": [
                "(looks around)",
                "Q: First question",
                "(sighs deeply)",
                "Query: Another question",
                "Random text",
                "(checks phone)"
            ],
            "expected1": ["(looks around)", "(sighs deeply)", "(checks phone)"],
            "expected2": ["First question", "Another question"],
            "expected3": ["Random text"]
        },
        {
            "name": "Invalid shortcut",
            "prefix1": "@nonexistent",
            "prefix2": "@scene",
            "input": [
                "INT. ROOM - DAY",
                "Some text",
                "EXT. PARK - NIGHT"
            ],
            "expected1": [],
            "expected2": [],
            "expected3": ["INT. ROOM - DAY", "Some text", "EXT. PARK - NIGHT"]
        },
        {
            "name": "Basic * wildcard",
            "prefix1": "Q*",
            "prefix2": "A*",
            "input": [
                "Q: First question",
                "Query: Second question",
                "A: First answer",
                "Answer: Second answer",
                "Random line"
            ],
            "expected1": ["First question", "Second question"],
            "expected2": ["First answer", "Second answer"],
            "expected3": ["Random line"]
        }
    ]

    for test_case in test_cases:
        print(f"\n=== Running test: {test_case['name']} ===")
        
        section._parms["prefix1"].set(test_case["prefix1"])
        section._parms["prefix2"].set(test_case["prefix2"])
        input_node._parms["text_string"].set(str(test_case["input"]))
        section.set_state(NodeState.UNCOOKED)

        result1 = out1.eval()
        result2 = out2.eval()
        result3 = out3.eval()

        def verify(actual, expected, name):
            if actual == expected:
                print(f"✅ {name} PASSED")
                print(f"Expected: {expected}")
                print(f"Got: {actual}")
            else:
                print(f"❌ {name} FAILED")
                print(f"Expected: {expected}")
                print(f"Got: {actual}")
                if len(expected) != len(actual):
                    print(f"Length mismatch - Expected: {len(expected)}, Got: {len(actual)}")
                else:
                    for i, (exp, act) in enumerate(zip(expected, actual)):
                        if exp != act:
                            print(f"Mismatch at index {i}:")
                            print(f"Expected: '{exp}'")
                            print(f"Got: '{act}'")

        verify(result1, test_case["expected1"], f"{test_case['name']} - Output 1")
        verify(result2, test_case["expected2"], f"{test_case['name']} - Output 2")
        verify(result3, test_case["expected3"], f"{test_case['name']} - Output 3")

        if "@nonexistent" in [test_case["prefix1"], test_case["prefix2"]]:
            if len(section.warnings()) > 0:
                print(f"✅ Warning check PASSED")
                print(f"Got expected warnings: {section.warnings()}")
            else:
                print(f"❌ Warning check FAILED")
                print("No warnings found")

if __name__ == "__main__":
    test_section_node()