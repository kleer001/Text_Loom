import hashlib
import time
import os
from typing import List, Dict, Any, Optional
from core.base_classes import Node, NodeType, NodeState, NodeEnvironment
from core.parm import Parm, ParameterType
from core.loop_manager import LoopManager, loop_manager

class InputNullNode(Node):
    """A node that retrieves input from another specified node.

    This node is typically used inside a Looper Node, but can function independently.
    It retrieves the input value of another node specified by the in_node parameter.

    Attributes:
        in_node (str): Path to the target node to retrieve input from.
        in_data (List[str]): Data retrieved from the target node's input.
        feedback_mode (bool): When True, retrieves output from parent looper's
            output node instead of the target node's input (for iterative processing).

    Example:
        >>> input_null = Node.create_node(NodeType.INPUT_NULL)
        >>> input_null.parms()["in_node"].set("/root/my_node")
        >>> input_null.cook()
        >>> # Output: data from the input of /root/my_node

    Note:
        The node retrieves data from the input connection of the target node,
        not the target node's output. This allows looper constructs to access
        data flowing into the loop boundary.
    """

    GLYPH = '▷'

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._last_input_size = 0
        self._output = None
        self._parent_looper = True
        # Initialize parameters
        self._parms.update({
            "in_node": Parm("in_node", ParameterType.STRING, self),
            "in_data": Parm("in_data", ParameterType.STRINGLIST, self),
            "feedback_mode": Parm("feedback_mode", ParameterType.TOGGLE, self),
        })

        # Set default values
        self._parms["in_node"].set("")
        self._parms["in_data"].set([])
        self._parms["feedback_mode"].set(False)

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            in_node_path = self._parms["in_node"].eval()

            if not in_node_path:
                raise ValueError("Input node path is empty")

            in_node = NodeEnvironment.nodes.get(in_node_path)

            if not in_node:
                raise ValueError(f"Invalid node path: {in_node_path}")

            if not in_node.inputs():
                self.add_warning(f"Node at {in_node_path} has no inputs")
                self._parms["in_data"].set([])
                self._output = []
                self.set_state(NodeState.COOKED)
                return

            input_connection = in_node.inputs()[0]

            output_node = input_connection.output_node()

            input_data = output_node.get_output(requesting_node=in_node)  # CHANGED: use get_output() with requesting_node

            if input_data is None:
                self.add_warning("Input data is None, setting empty list as output")
                self._parms["in_data"].set([])
                self._output = []
            elif not isinstance(input_data, list):
                raise TypeError(f"Input data must be a list, got {type(input_data)}")
            elif not all(isinstance(item, str) for item in input_data):
                raise TypeError("All items in input data must be strings")
            else:
                loopnumber = loop_manager.get_current_loop(self.path())

                if(self._parms["feedback_mode"].eval() is True and loopnumber > 1):
                    parent_looper_name = os.path.dirname(self.path())
                    parent_looper = NodeEnvironment.node_from_name(parent_looper_name)
                    input_data = parent_looper._output_node._parms["out_data"].eval()

                self._parms["in_data"].set(input_data)
                self._output = input_data

            self.set_state(NodeState.COOKED)

        except Exception as e:
            self.add_error(f"Error in InputNullNode cook: {str(e)}")
            self.set_state(NodeState.UNCOOKED)
            self._output = []
            self._parms["in_data"].set([])

        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            in_node_path = self._parms["in_node"].eval()
            in_node = NodeEnvironment.nodes.get(in_node_path)

            if not in_node or not in_node.inputs():
                return True

            current_input = in_node.inputs()[0].output_node().eval()
            current_size = sum(len(s.encode('utf-8')) for s in current_input)

            if current_size != self._last_input_size:
                return True

            if current_size < 10 * 1024 * 1024:  # 10MB
                return True

            current_hash = self._calculate_hash(str(current_input))
            if current_hash != self._input_hash:
                return True

            return False

        except Exception:
            return True

    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def input_names(self) -> Dict[int, str]:
        return {}  # This node has no inputs

    def output_names(self) -> Dict[int, str]:
        return {0: "Output Data"}

    def input_data_types(self) -> Dict[int, str]:
        return {}  # This node has no inputs

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}