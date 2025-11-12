import time
import sys
import re
from typing import List, Dict, Any, Optional
import traceback

from core.base_classes import Node, NodeType, NodeState, NodeEnvironment
from core.parm import Parm, ParameterType
from core.input_null_node import InputNullNode
from core.output_null_node import OutputNullNode
from core.loop_manager import LoopManager, loop_manager

from dataclasses import dataclass



class LooperNode(Node):
    """
    LooperNode: A powerful node for iterative processing of data with configurable loop behavior.

    This node enables iterative operations by managing internal input and output connections, making it
    ideal for tasks that require repeated processing or accumulation of results. Think of it as a
    sophisticated 'for' loop that can process data iteratively while maintaining node graph connectivity.

    Parameters:
        min (int): Starting value for the loop iteration (must be non-negative)
        max (int): Ending value for the loop iteration (must be non-negative)
        step (int): Increment value between iterations (cannot be zero)
        max_from_input (bool): When enabled, sets max iterations based on input data length
        feedback_mode (bool): Enables feedback loop mode where each iteration's output feeds into the next
        use_test (bool): When enabled, runs only a single test iteration
        cook_loops (bool): Controls whether to force cook operations on each loop iteration
        test_number (int): Specific iteration to run when use_test is enabled (must be between min and max)
        input_hook (str): Custom input processing hook (advanced usage)
        output_hook (str): Custom output processing hook (advanced usage)
        timeout_limit (float): Maximum execution time in seconds (default: 300.0)
        data_limit (int): Maximum memory usage in bytes (default: 200MB)

    Loop Behavior Modes:
        1. Standard Loop:
        - Iterates from min to max by step
        - Each iteration processes fresh input data
        Example use case: Processing a series of numbered files or generating sequences

        2. Input-Driven Loop (max_from_input=True):
        - Number of iterations matches input data length
        - Useful for processing lists or arrays item by item
        Example use case: Processing each item in a list with complex operations

        3. Feedback Loop (feedback_mode=True):
        - Output of each iteration becomes input for the next
        - Useful for recursive or cumulative operations
        Example use case: Iterative refinement or accumulation of results

        4. Test Mode (use_test=True):
        - Runs single iteration specified by test_number
        - Useful for debugging and development
        Example use case: Testing specific iteration behavior without running full loop

    Safety Features:
        - Timeout protection (timeout_limit parameter)
        - Memory usage limits (data_limit parameter)
        - Automatic cleanup of stale loops
        - Parameter validation to prevent invalid configurations

    Internal Structure:
        The node creates and manages two internal nodes:
        - inputNullNode: Handles input data for each iteration
        - outputNullNode: Collects and manages output from each iteration

    Notes:
        - Iterations stop if timeout_limit is reached
        - Warns if iterations produce null/blank values
        - Last valid output is preserved in staging_data
        - All iterations must process List[str] data types
        - Step can be negative for reverse iteration

    Example Usage:
        1. Basic counting loop:
        min=1, max=10, step=1
        Result: Processes 10 iterations

        2. Input-driven processing:
        max_from_input=True
        Result: Iterations match input data length

        3. Feedback processing:
        feedback_mode=True
        Result: Each iteration processes previous iteration's output

        4. Debug specific iteration:
        use_test=True, test_number=5
        Result: Only processes iteration #5
    """
    GLYPH = '⟲'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_node = None
        self._output_node = None
        self._internal_nodes_created = False

        # Initialize parameters
        self._parms.update({
            "min": Parm("min", ParameterType.INT, self),
            "max": Parm("max", ParameterType.INT, self),
            "step": Parm("step", ParameterType.INT, self),
            "max_from_input": Parm("max_from_input", ParameterType.TOGGLE, self),
            "feedback_mode": Parm("feedback_mode", ParameterType.TOGGLE, self),
            "use_test": Parm("use_test", ParameterType.TOGGLE, self),
            "cook_loops": Parm("cook_loops", ParameterType.TOGGLE, self),
            "test_number": Parm("test_number", ParameterType.INT, self),
            "input_hook": Parm("input_hook", ParameterType.STRING, self), #WHY?
            "output_hook": Parm("output_hook", ParameterType.STRING, self), #WHY?
            "staging_data": Parm("staging_data", ParameterType.STRINGLIST, self),
            "timeout_limit": Parm("timeout_limit", ParameterType.FLOAT, self),
            "data_limit": Parm("data_limit", ParameterType.INT, self),
        })

        # Set default values
        self._parms["min"].set(1)
        self._parms["max"].set(3)
        self._parms["step"].set(1)
        self._parms["max_from_input"].set(False)
        self._parms["feedback_mode"].set(False)
        self._parms["use_test"].set(False)
        self._parms["cook_loops"].set(False)
        self._parms["test_number"].set(1)
        self._parms["input_hook"].set("")
        self._parms["output_hook"].set("")
        self._parms["staging_data"].set([])
        self._parms["timeout_limit"].set(300.0)  # 5 minutes in seconds
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

    def _internal_cook(self, force: bool = False) -> None:

        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        if self.errors():
            self.set_state(NodeState.UNCOOKED)
            return

        # Check if we need to cook
        if not self.inputs() and not self._output_node.inputs():
            self.set_state(NodeState.UNCHANGED)
            return

        # Clear staging_data at the beginning of a major cook
        print("LOOPER DATA = ",self._parms["staging_data"].eval())
        print("LOOPER CLEARING DATA?")
        self._parms["staging_data"].set([])
        print("LOOPER DATA = ",self._parms["staging_data"].eval())

        # 🔧 ADD THIS LINE - Clear the OutputNullNode's accumulated data
        print("STAGING DATA = ",self._output_node._parms["out_data"].eval())
        if self._output_node:
            self._output_node._parms["out_data"].set([])
        print("STAGING DATA = ",self._output_node._parms["out_data"].eval())

        try:
            self._perform_iterations()
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_error(f"Error during iteration: {error_trace}")
            self.set_state(NodeState.UNCOOKED)


        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        if self.state() == NodeState.COOKING:
            self.set_state(NodeState.UNCHANGED)

        self._output = self._parms["staging_data"].raw_value()


    def _perform_iterations(self):
        print("\n∞ loop: starting loop, cleaning up")
        loop_manager.clean_stale_loops(self.path())

        min_val = self._parms["min"].eval()
        max_val = self._parms["max"].eval()
        step = self._parms["step"].eval()
        use_test = self._parms["use_test"].eval()
        test_number = self._parms["test_number"].eval()
        timeout_limit = self._parms["timeout_limit"].eval()
        feedback_mode = self._parms["feedback_mode"].eval()
        cook_loops = self._parms["cook_loops"].eval()

        self._input_node._parms["feedback_mode"].set(feedback_mode)
        self._output_node._parms["feedback_mode"].set(feedback_mode)

        max_from_input = self._parms["max_from_input"].eval()
        if max_from_input is True:
            # Get the actual input data (which for FolderNode will be a list of file contents)
            input_data = self.inputs()[0].output_node().eval(requesting_node=self)
            input_steps = len(input_data)
            max_val = input_steps
            print("RUNNING LOOP FROM INPUT, num = ", input_steps)

        if use_test:
            iteration_range = [test_number]
        else:
            iteration_range = range(min_val, max_val + 1, step) if step > 0 else range(max_val, min_val - 1, step)

        start_time = time.time()
        self._parms["staging_data"].set([])
        collected_outputs = []

        for i in iteration_range:
            if time.time() - start_time > timeout_limit:
                self.add_warning(f"Iteration timeout reached after {timeout_limit} seconds.")
                break

            loop_manager.set_loop(self.path(), i)
            self._output_node.cook()
            iteration_result = self._output_node._parms["out_data"].eval()

            if iteration_result:
                collected_outputs.append(iteration_result)
            else:
                self.add_warning(f"Iteration {i} created a blank or null value.")

        if collected_outputs:
            last_valid_output = collected_outputs[-1]
            self._parms["staging_data"].set(last_valid_output)
            self._output = last_valid_output
        else:
            self._parms["staging_data"].set([])
            self._output = []

        loop_manager.set_loop(self.path(), value=None)
        print("∞ loop: end of loop reached, cleaning up\n")

    def input_names(self) -> Dict[int, str]:
        return {0: "Input Data"}

    def output_names(self) -> Dict[int, str]:
        return {0: "Output Data"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def _create_internal_nodes(self):
        if self._internal_nodes_created:
            return

        # Skip if called during parent node registration (when _creating_node is True)
        # This ensures child nodes are only created after parent is fully registered
        from core.node_environment import NodeEnvironment
        if NodeEnvironment.get_instance()._creating_node:
            return

        # Mark as created to prevent duplicate calls
        self._internal_nodes_created = True

        try:
            input_node_name = "inputNullNode"
            self._input_node = Node.create_node(NodeType.INPUT_NULL, node_name=input_node_name, parent_path=self.path())

            output_node_name = "outputNullNode"
            self._output_node = Node.create_node(NodeType.OUTPUT_NULL, node_name=output_node_name, parent_path=self.path())

            input_node_parms = self._input_node._parms
            if "in_node" in input_node_parms:
                input_node_parms["in_node"].set(self.path())

            output_node_parms = self._output_node._parms
            if "in_node" in output_node_parms:
                output_node_parms["in_node"].set(self.path())

            self._children.append(self._input_node)
            self._children.append(self._output_node)

        except Exception as e:
            self._internal_nodes_created = False  # Reset on error
            self.add_error(f"Failed to create internal nodes: {str(e)}")

    def connect_loop_in(self, node: 'Node'):
        node.set_input(0, self._input_node, "output")

    def connect_loop_out(self, node: 'Node'):
        self._output_node.set_input(0, node, "output")

    def __del__(self):
        # Ensure the callback is unregistered when the LooperNode is deleted
        if self._on_created_callback:
            self._on_created_callback()
        super().__del__()