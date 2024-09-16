import time
from typing import List, Dict, Any, Optional
from base_classes import Node, NodeType, NodeState
from parm import Parm, ParameterType
from out_null_node import OutputNullNode
import sys

class LooperNode(Node):
    """
    A node that performs loop operations on its input data.
    
    This node contains two internal nodes (inputNull and outputNull) and performs
    iterations based on specified parameters. It accumulates output from each
    iteration into a staging area before producing the final output.
    """

    SINGLE_INPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "min": Parm("min", ParameterType.INT, self),
            "max": Parm("max", ParameterType.INT, self),
            "step": Parm("step", ParameterType.INT, self),
            "use_test": Parm("use_test", ParameterType.TOGGLE, self),
            "test_number": Parm("test_number", ParameterType.INT, self),
            "input_hook": Parm("input_hook", ParameterType.STRINGLIST, self),
            "output_hook": Parm("output_hook", ParameterType.STRINGLIST, self),
            "staging_data": Parm("staging_data", ParameterType.STRINGLIST, self),
            "timeout_limit": Parm("timeout_limit", ParameterType.FLOAT, self),
            "data_limit": Parm("data_limit", ParameterType.INT, self)
        }

        # Set default values
        self._parms["min"].set(1)
        self._parms["max"].set(3)
        self._parms["step"].set(1)
        self._parms["use_test"].set(False)
        self._parms["test_number"].set(1)
        self._parms["input_hook"].set([])
        self._parms["output_hook"].set([])
        self._parms["staging_data"].set([])
        self._parms["timeout_limit"].set(180.0)  # 3 minutes in seconds
        self._parms["data_limit"].set(200 * 1024 * 1024)  # 200MB in bytes

        # Create internal nodes
        self._create_internal_nodes()

    def _create_internal_nodes(self):
        try:
            self._input_node = Node.create_node(NodeType.OUTPUT_NULL, "inputNode")
            self._output_node = Node.create_node(NodeType.OUTPUT_NULL, "outputNode")
            
            # Set inputNode's in_node parameter to this looper's path
            input_node_parms = self._input_node._parms
            if "in_node" in input_node_parms:
                input_node_parms["in_node"].set(self.path())
            
            # Connect outputNode to this looper
            self.set_input("output_hook", self._output_node, "output")
        except Exception as e:
            self.add_error(f"Failed to create internal nodes: {str(e)}")

    def _validate_parameters(self):
        min_val = self._parms["min"].eval()
        max_val = self._parms["max"].eval()
        step = self._parms["step"].eval()
        use_test = self._parms["use_test"].eval()
        test_number = self._parms["test_number"].eval()

        if not isinstance(min_val, int) or min_val < 0:
            self.add_error("'min' must be a non-negative integer")
        if not isinstance(max_val, int) or max_val < 0:
            self.add_error("'max' must be a non-negative integer")
        if not isinstance(step, int):
            self.add_error("'step' must be an integer")
        if step == 0:
            self.add_error("'step' cannot be zero")
        if step > 0 and min_val > max_val:
            self.add_error("'min' must be less than or equal to 'max' when step is positive")
        if step < 0 and min_val < max_val:
            self.add_error("'min' must be greater than or equal to 'max' when step is negative")
        if use_test and (test_number < min_val or test_number > max_val):
            self.add_error("'test_number' must be within the range of 'min' and 'max' when 'use_test' is True")
        
        if (step > 0 and step > max_val - min_val) or (step < 0 and abs(step) > max_val - min_val):
            self.add_warning("The current step size will result in no iterations")

    def cook(self, force: bool = False) -> None:
        self.cook_dependencies()
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        try:
            self._validate_parameters()
            if self.errors():
                raise ValueError("Parameter validation failed")

            self._parms["staging_data"].set([])  # Clear staging data

            input_data = self.inputs()[0].output_node().eval() if self.inputs() else []
            self._parms["input_hook"].set(input_data)

            if not input_data and not self._output_node.inputs():
                self.add_warning("No input connected and no input to internal outputNull node. Skipping cook.")
                self.set_state(NodeState.UNCHANGED)
                return

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

            for i in iteration_range:
                if time.time() - start_time > timeout_limit:
                    self.add_warning(f"Timeout reached after {timeout_limit} seconds. Stopping iterations.")
                    break

                # Set the current iteration number for the internal nodes
                self._input_node._parms["in_node"].set(str(i))
                
                # Cook the output node
                self._output_node.cook(force)
                
                # Get the output from the internal output node
                output = self._output_node.eval()
                self._parms["output_hook"].set(output)

                if not output or all(not item.strip() for item in output):
                    self.add_warning(f"Iteration {i} produced a blank or empty value.")

                # Append to staging data
                current_staging = self._parms["staging_data"].eval()
                current_staging.extend(output)
                self._parms["staging_data"].set(current_staging)

                # Check data size
                data_size = sys.getsizeof(current_staging)
                if data_size > self._parms["data_limit"].eval():
                    self.add_error(f"Data size exceeded limit of {self._parms['data_limit'].eval()} bytes. Stopping iterations.")
                    break
                elif data_size > 100 * 1024 * 1024:  # 100MB
                    self.add_warning(f"Data size has exceeded 100MB. Current size: {data_size / (1024 * 1024):.2f}MB")

            self._output = self._parms["staging_data"].eval()
            self.set_state(NodeState.UNCHANGED)

        except Exception as e:
            self.add_error(f"Error during cooking: {str(e)}")
            self.set_state(NodeState.UNCOOKED)

        self._last_cook_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    def eval(self) -> List[str]:
        if self.state() != NodeState.UNCHANGED:
            self.cook()
        return self._output

    def input_names(self) -> Dict[str, str]:
        return {"input": "Input Data"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "Output Data"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}