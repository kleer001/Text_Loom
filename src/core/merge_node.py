import time
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType

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

    Parms: 

    single_string = boolian, merges input strings into a single string item list

    insert_string = string, the string to be inserted ahead of each string list item. N is replaced with the index number of the string list item (starting with 1). This string is surrounded by a complementary (and hard coded) pair of new line escaped characters
    
    use_insert = boolian, inserts the insert_string at the head of each item in the list as they're merged together
    """

    GLYPH = '⋈'
    SINGLE_INPUT = False
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.MERGE)
        self._is_time_dependent = False
        self._output: List[str] = []

        # Initialize parameters
        self._parms.update({
            "single_string": Parm("single_string", ParameterType.TOGGLE, self),
            "use_insert": Parm("use_insert", ParameterType.TOGGLE, self),
            "insert_string": Parm("insert_string", ParameterType.STRING, self)
        })
        # Set default value
        self._parms["single_string"].set(True)
        self._parms["use_insert"].set(False)
        self._parms["insert_string"].set("##N")

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        input_data = []

        for input_connection in self.inputs():
            #does this work with the split node correctly? 
            #TODO - Check. 
            node_data = input_connection.output_node().eval(requesting_node=self)
            if not isinstance(node_data, list) or not all(isinstance(item, str) for item in node_data):
                raise TypeError(f"Input from {input_connection.output_node().name()} must be a list of strings")
            input_data.extend(node_data)

        use_insert = self._parms["use_insert"].eval()
        if use_insert is True:
            insert_string_raw = self._parms["insert_string"].eval()
            temp_data = []
            for num_in, in_d in enumerate(input_data):
                insert_string = insert_string_raw.replace("N", str(num_in + 1))
                next_item = "\n" + insert_string + "\n" + in_d
                #print("NEXT ITEM ", next_item)
                temp_data.append(next_item)
            input_data = temp_data
        single_string = self._parms["single_string"].eval()
        if single_string:
            self._output = ["".join(input_data)]
        else:
            self._output = input_data

        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
    def input_names(self) -> Dict[str, str]:
        return {f"input{i}": f"Input {i}" for i in range(len(self.inputs()))}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Merged Output"}

    def input_data_types(self) -> Dict[str, str]:
        return {f"input{i}": "List[str]" for i in range(len(self.inputs()))}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        # Check if inputs have changed
        current_inputs = self.input_nodes()
        if len(current_inputs) != len(self._output):
            return True

        for input_node in current_inputs:
            if input_node.needs_to_cook():
                return True

        return False