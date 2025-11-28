import time
from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.enums import FunctionalGroup

class MergeNode(Node):
    """Represents a Merge Node in the workspace.

    The Merge Node combines multiple input string lists into a single string list
    with one item. It can have one or more input connections and produces a single
    output.

    Attributes:
        single_string (bool): Merges input strings into a single string item list.
        insert_string (str): The string to be inserted ahead of each string list item.
                             'N' is replaced with the index number of the string list item (starting with 1).
                             This string is surrounded by a complementary (and hard coded) pair of newline escaped characters.
        use_insert (bool): Inserts the `insert_string` at the head of each item in the list as they're merged together.

    Example:
        >>> # Create a Merge node and three FILE_IN nodes
        >>> merge_node = Node.create_node(NodeType.MERGE)
        >>> file_in1 = Node.create_node(NodeType.FILE_IN)
        >>> file_in2 = Node.create_node(NodeType.FILE_IN)
        >>> file_in3 = Node.create_node(NodeType.FILE_IN)
        >>>
        >>> # Connect the FILE_IN nodes to the Merge node
        >>> merge_node.set_input("input0", file_in1, "output")
        >>> merge_node.set_input("input1", file_in2, "output")
        >>> merge_node.set_input("input2", file_in3, "output")
        >>>
        >>> # To reorder the inputs arbitrarily, you can use Python's built-in functions
        >>> # Get the current inputs
        >>> current_inputs = merge_node.inputs()
        >>>
        >>> # Reorder the inputs (e.g., move the last input to the first position)
        >>> reordered_inputs = current_inputs[-1:] + current_inputs[:-1]
        >>>
        >>> # Clear existing inputs
        >>> for i in range(len(current_inputs)):
        ...     merge_node.remove_input(f"input{i}")
        >>>
        >>> # Set the reordered inputs
        >>> for i, input_node in enumerate(reordered_inputs):
        ...     merge_node.set_input(f"input{i}", input_node, "output")
        >>>
        >>> # You can use any Python list operations to reorder the inputs as needed
    """

    GLYPH = '⋈'
    GROUP = FunctionalGroup.LIST
    SINGLE_INPUT = False
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, position: List[float]):
        super().__init__(name, path, position, NodeType.MERGE)
        self._is_time_dependent = False
        self._output: List[str] = []

        self._parms.update({
            "single_string": Parm("single_string", ParameterType.TOGGLE, self),
            "use_insert": Parm("use_insert", ParameterType.TOGGLE, self),
            "insert_string": Parm("insert_string", ParameterType.STRING, self)
        })

        self._parms["single_string"].set(True)
        self._parms["use_insert"].set(False)
        self._parms["insert_string"].set("##N")

    def _collect_input_data(self) -> List[str]:
        collected = []
        for connection in self.inputs():
            data = connection.output_node().eval(requesting_node=self)
            if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
                raise TypeError(f"Input from {connection.output_node().name()} must be a list of strings")
            collected.extend(data)
        return collected

    def _apply_insert_prefix(self, items: List[str]) -> List[str]:
        template = self._parms["insert_string"].eval()
        return [f"\n{template.replace('N', str(i + 1))}\n{item}" for i, item in enumerate(items)]

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        data = self._collect_input_data()

        if self._parms["use_insert"].eval():
            data = self._apply_insert_prefix(data)

        self._output = ["".join(data)] if self._parms["single_string"].eval() else data

        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000
        
    def input_names(self) -> Dict[int, str]:
        return {i: f"Input {i}" for i in range(len(self.inputs()) + 1)}

    def output_names(self) -> Dict[int, str]:
        return {0: "Merged Output"}

    def input_data_types(self) -> Dict[int, str]:
        return {i: "List[str]" for i in range(len(self.inputs()) + 1)}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        current_inputs = self.input_nodes()
        if len(current_inputs) != len(self._output):
            return True

        return any(node.needs_to_cook() for node in current_inputs)