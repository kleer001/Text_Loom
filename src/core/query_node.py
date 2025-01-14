from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.llm_utils import get_clean_llm_response
from core.findLLM import *

class QueryNode(Node):
    """
    A node that sends prompts to an LLM and stores the responses.

    This node takes a list of strings as input, optionally limits it to one item,
    sends each prompt to the specified LLM, and stores the responses.

    Attributes:
        _is_time_dependent (bool): Always True for this node.
    """

    SINGLE_INPUT = True
    SINGLE_OUTPUT = True
    
    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = True #I'm on the fence, but False seems too boring

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "limit": Parm("limit", ParameterType.TOGGLE, self),
            "response": Parm("response", ParameterType.STRINGLIST, self),
            "llm_name": Parm("llm_name", ParameterType.STRING, self),
            "find_llm": Parm("find_llm", ParameterType.BUTTON, self),
            "respond": Parm("respond", ParameterType.BUTTON, self)
        }

        # Set default values
        self._parms["limit"].set("True")
        self._parms["response"].set([])
        self._parms["llm_name"].set("Ollama")

        # Set button callbacks
        self._parms["find_llm"].set_script_callback(self._find_llm_callback)
        self._parms["respond"].set_script_callback(self._respond_callback)

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1

        input_data = self.inputs()[0].output_node().eval(requesting_node=self) if self.inputs() else []
        if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
            self.add_error("Input data must be a list of strings")
            return

        limit = self._parms["limit"].eval()
        if limit and len(input_data) > 1:
            input_data = input_data[:1]
            self.add_error("Input limited to one item due to 'limit' parameter being True")

        llm_name = self._parms["llm_name"].eval()
        if llm_name == "None":
            self.add_error("No LLM specified. Running find_local_llm().")
            llm_name = find_local_LLM()
            self._parms["llm_name"].set(llm_name)

        responses = []
        for prompt in input_data:
            try:
                response = get_clean_llm_response(prompt)
                responses.append(response)
            except Exception as e:
                self.add_error(f"Error processing prompt: {str(e)}")
                responses.append("")  # Add an empty string for failed responses

        self._parms["response"].set(responses)
        self._output = responses
        self.set_state(NodeState.UNCHANGED)

    def _find_llm_callback(self) -> None:
        llm_name = find_local_LLM()
        self._parms["llm_name"].set(llm_name)

    def _respond_callback(self) -> None:
        self.cook(force=True)

    def input_names(self) -> Dict[str, str]:
        return {"input": "Input Prompts"}

    def output_names(self) -> Dict[str, str]:
        return {"output": "LLM Responses"}

    def input_data_types(self) -> Dict[str, str]:
        return {"input": "List[str]"}

    def output_data_types(self) -> Dict[str, str]:
        return {"output": "List[str]"}

    # def eval(self, force: bool = False) -> List[str]:
    #     if self.state() != NodeState.UNCHANGED or force is True:
    #         self.cook()
    #     return self._output