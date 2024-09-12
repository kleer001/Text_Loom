import pytest
from src.backend.base_classes import Node, NodeType

@pytest.fixture
def create_node():
    def _create_node(node_type):
        return Node.create_node(node_type)
    return _create_node

@pytest.fixture
def print_node_info(capsys):
    def _print_node_info(node, node_name):
        print(f"\n--- {node_name} Node Information ---")
        print(f"Node: {node}")
        print(f"Node Type: {node.type()}")
        print(f"Node Path: {node.path()}")
        print(f"Node State: {node.state()}")
        print("Parameters:")
        if hasattr(node, '_parms'):
            for parm_name, parm in node._parms.items():
                print(f"  {parm_name}: {parm.raw_value()}")
        else:
            print("No parameters found.")
        print(f"Inputs: {node.inputs_with_indices()}")
        print(f"Outputs: {node.outputs_with_indices()}")
        print(f"Errors: {node.errors()}")
        print(f"Warnings: {node.warnings()}")
        print(f"Last Cook Time: {node.last_cook_time()}")
        print(f"Cook Count: {node.cook_count()}")

        # Capture and return the printed output
        captured = capsys.readouterr()
        return captured.out

    return _print_node_info
