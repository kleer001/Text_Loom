import time
from typing import List, Dict, Any
from base_classes import Node, NodeType, NodeState

class MergeNode(Node):
    """
    Represents a Merge Node in the workspace.
    
    The Merge Node combines multiple input string lists into a single string list
    with one item. It can have one or more input connections and produces a single
    output.

    Example usage:
    # Create a Merge node and three FILE_IN nodes
    merge_node = Node.create_node(NodeType.MERGE)
    file_in1 = Node.create_node(NodeType.FILE_IN)
    file_in2 = Node.create_node(NodeType.FILE_IN)
    file_in3 = Node.create_node(NodeType.FILE_IN)

    # Connect the FILE_IN nodes to the Merge node
    merge_node.set_input("input0", file_in1, "output")
    merge_node.set_input("input1", file_in2, "output")
    merge_node.set_input("input2", file_in3, "output")

    # To reorder the inputs arbitrarily, you can use Python's built-in functions
    # Get the current inputs
    current_inputs = merge_node.inputs()

    # Reorder the inputs (e.g., move the last input to the first position)
    reordered_inputs = current_inputs[-1:] + current_inputs[:-1]

    # Clear existing inputs
    for i in range(len(current_inputs)):
        merge_node.remove_input(f"input{i}")

    # Set the reordered inputs
    for i, input_node in enumerate(reordered_inputs):
        merge_node.set_input(f"input{i}", input_node, "output")

    # You can use any Python list operations to reorder the inputs as needed
    """


    SINGLE_INPUT = False

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.MERGE)
        self._is_time_dependent = False
        self._merged_output: List[str] = []

    def cook(self, force: bool = False) -> None:
        self.cook_dependencies()
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            input_data = []
            for input_connection in self.inputs():
                node_data = input_connection.output_node().eval()
                if not isinstance(node_data, list) or not all(isinstance(item, str) for item in node_data):
                    raise TypeError(f"Input from {input_connection.output_node().name()} must be a list of strings")
                input_data.extend(node_data)

            self._merged_output = ["".join(input_data)]
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error in MergeNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
    def input_names(self) -> Dict[str, str]:
        return {f"input{i}": f"Input {i}" for i in range(len(self.inputs()))}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Merged Output"}

    def input_data_types(self) -> Dict[str, str]:
        return {f"input{i}": "List[str]" for i in range(len(self.inputs()))}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def eval(self) -> List[str]:
        if self.state() != NodeState.UNCHANGED:
            self.cook()
        return self._merged_output

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        # Check if inputs have changed
        current_inputs = self.inputs()
        if len(current_inputs) != len(self._merged_output):
            return True

        for input_node in current_inputs:
            if input_node.needs_to_cook():
                return True

        return False