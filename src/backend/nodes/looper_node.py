import time
import sys
import re
from typing import List, Dict, Any, Optional
from base_classes import Node, NodeType, NodeState, NodeEnvironment
from parm import Parm, ParameterType#, set_loop, clean_stale_loops
from .input_null_node import InputNullNode
from .output_null_node import OutputNullNode
from dataclasses import dataclass
from loop_manager import LoopManager, loop_manager


"""
Looping functions for looper node type and what it does
Called in looper_node.py too
"""


# def get_loop_var_name(path: str, depth: int) -> str:
#     """
#     Generate a loop variable name based on the looper node's path and depth.
#     """
#     safe_path = re.sub(r"[^a-zA-Z0-9_]", "_", path)
#     return f"loop_{safe_path}_{depth}"


# def get_current_loop(path: str, depth: int) -> Optional[int]:
#     """
#     Get the current loop number for a given path and depth.
#     """
#     var_name = get_loop_var_name(path, depth)
#     return globals().get(var_name)


# def set_loop(path: str, depth: int, value: int) -> None:
#     """
#     Set the loop number for a given path and depth.
#     """
#     var_name = get_loop_var_name(path, depth)
#     globals()[var_name] = value


# def clean_stale_loops() -> None:
#     """
#     Remove all stale loop variables from globals.
#     This should be called at the beginning of each cook operation.
#     """
#     for var in list(globals().keys()):
#         if var.startswith("loop_"):
#             del globals()[var]



class LooperNode(Node):
    """
    A node that performs loop iterations, managing internal input and output nodes.
    
    This node creates internal inputNull and outputNull nodes, and iterates through
    a range of values, collecting output data from each iteration.
    """

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_node = None
        self._output_node = None
        self._internal_nodes_created = False
        
        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "min": Parm("min", ParameterType.INT, self),
            "max": Parm("max", ParameterType.INT, self),
            "step": Parm("step", ParameterType.INT, self),
            "use_test": Parm("use_test", ParameterType.TOGGLE, self),
            "test_number": Parm("test_number", ParameterType.INT, self),
            "input_hook": Parm("input_hook", ParameterType.STRING, self),
            "output_hook": Parm("output_hook", ParameterType.STRING, self),
            "staging_data": Parm("staging_data", ParameterType.STRINGLIST, self),
            "timeout_limit": Parm("timeout_limit", ParameterType.FLOAT, self),
            "data_limit": Parm("data_limit", ParameterType.INT, self),
        }

        # Set default values
        self._parms["min"].set(1)
        self._parms["max"].set(3)
        self._parms["step"].set(1)
        self._parms["use_test"].set(False)
        self._parms["test_number"].set(1)
        self._parms["input_hook"].set("")
        self._parms["output_hook"].set("")
        self._parms["staging_data"].set([])
        self._parms["timeout_limit"].set(180.0)  # 3 minutes in seconds
        self._parms["data_limit"].set(200 * 1024 * 1024)  # 200MB in bytes

    @classmethod
    def post_registration_init(cls, node):
        if isinstance(node, LooperNode) and not node._internal_nodes_created:
            node._create_internal_nodes()

    def validate_parameters(self):
        min_val = self._parms["min"].eval()
        max_val = self._parms["max"].eval()
        step = self._parms["step"].eval()
        use_test = self._parms["use_test"].eval()
        test_number = self._parms["test_number"].eval()

        if not isinstance(min_val, int) or min_val < 0:
            self.add_error("'min' must be a non-negative integer.")
        if not isinstance(max_val, int) or max_val < 0:
            self.add_error("'max' must be a non-negative integer.")
        if not isinstance(step, int):
            self.add_error("'step' must be an integer.")
        if step == 0:
            self.add_error("'step' cannot be zero.")
        if step > 0 and min_val > max_val:
            self.add_error("'min' must be less than or equal to 'max' when step is positive.")
        if step < 0 and min_val < max_val:
            self.add_error("'min' must be greater than or equal to 'max' when step is negative.")
        if use_test and (test_number < min_val or test_number > max_val):
            self.add_error("'test_number' must be between 'min' and 'max' when 'use_test' is True.")
        
        if (max_val - min_val) // step == 0:
            self.add_warning("The current parameter values will result in no iterations.")

    def cook(self, force: bool = False) -> None:
        self.cook_dependencies()
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        # self.clear_errors()
        # self.clear_warnings()
        # self.validate_parameters()

        if self.errors():
            self.set_state(NodeState.UNCOOKED)
            return

        # Clear staging_data at the beginning of a major cook
        self._parms["staging_data"].set([])

        # Check if we need to cook
        if not self.inputs() and not self._output_node.inputs():
            self.set_state(NodeState.UNCHANGED)
            return

        try:
            self._perform_iterations()
        except Exception as e:
            self.add_error(f"Error during iteration: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if self.state() == NodeState.COOKING:
            self.set_state(NodeState.UNCHANGED)


    def _perform_iterations(self):
        print("∞ loop: starting loop, cleaning up")
        loop_manager.clean_stale_loops()  # Clean up stale loop variables at the start of cooking

        min_val = self._parms["min"].eval()
        max_val = self._parms["max"].eval()
        step = self._parms["step"].eval()
        use_test = self._parms["use_test"].eval()
        test_number = self._parms["test_number"].eval()
        timeout_limit = self._parms["timeout_limit"].eval()

        if use_test:
            iteration_range = [test_number]
        else:
            iteration_range = range(min_val, max_val + 1, step) if step > 0 else range(max_val, min_val - 1, step)

        start_time = time.time()
        staging_data = []

        for i in iteration_range:
            if time.time() - start_time > timeout_limit:
                self.add_warning(f"Iteration timeout reached after {timeout_limit} seconds.")
                break

            # Set loop number for this iteration
            loop_manager.set_loop(self.path(), i)

            # Get output from internal outputNode
            output_value = self._output_node.eval()
            
            if output_value in (None, "", "  "):
                self.add_warning(f"Iteration {i} created a blank value.")
            
            staging_data.append(str(output_value))
            
            # Check data size limit
            data_size = sum(sys.getsizeof(item) for item in staging_data)
            if data_size > self._parms["data_limit"].eval():
                self.add_warning(f"Data size limit reached: {data_size} bytes.")
                break
            elif data_size > 100 * 1024 * 1024:  # 100MB
                self.add_warning(f"Data size exceeds 100MB: {data_size} bytes.")

        self._parms["staging_data"].set(staging_data)
        self._parms["output_hook"].set("\n".join(staging_data))
        # Clean up this loop's variable after iterations are complete
        print("∞ loop: end of loop reached, cleaning up")
        loop_manager.set_loop(self.path(), None)


    def eval(self) -> List[str]:
        if self.state() != NodeState.UNCHANGED:
            self.cook()
        return self._parms["staging_data"].eval()

    def input_names(self) -> Dict[str, str]:
        return {"input": "Input Data"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Output Data"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    def _create_internal_nodes(self):
        if self._internal_nodes_created:
            return
        try:
            # Create InputNull node
            input_node_name = "inputNullNode"
            input_node_path = f"{self.path()}/{input_node_name}"
            self._input_node = Node.create_node(NodeType.INPUT_NULL, node_name=input_node_name, parent_path=self.path())

            # Create OutputNull node
            output_node_name = "outputNullNode"
            output_node_path = f"{self.path()}/{output_node_name}"
            self._output_node = Node.create_node(NodeType.OUTPUT_NULL, node_name=output_node_name, parent_path=self.path())
            
            # Set input_node's in_node parameter to this looper node's path
            input_node_parms = self._input_node._parms
            if "in_node" in input_node_parms:
                input_node_parms["in_node"].set(self.path())
            
            # Set parent-child relationships
            self._children.append(self._input_node)
            self._children.append(self._output_node)
            
        except Exception as e:
            self.add_error(f"Failed to create internal nodes: {str(e)}")


    def __del__(self):
        # Ensure the callback is unregistered when the LooperNode is deleted
        if self._on_created_callback:
            self._on_created_callback()
        super().__del__()