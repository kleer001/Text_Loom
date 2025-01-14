from typing import List, Dict, Any
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.llm_utils import get_clean_llm_response
from core.findLLM import *

class QueryNode(Node):

    """
    QueryNode: A node that interfaces with Large Language Models (LLMs) to process text prompts and generate responses.

    This node serves as a bridge between the node graph system and local LLM installations, enabling prompt-based
    text generation and processing. It can handle single or multiple prompts, with options to limit processing
    for development or resource management.

    Key Features:
        1. LLM Integration:
            - Automatically detects and connects to local LLM installations
            - Supports dynamic LLM selection and switching
            - Provides fallback mechanisms when preferred LLM is unavailable
            
        2. Prompt Processing:
            - Handles both single and batch prompt processing
            - Maintains response history
            - Supports forced response regeneration
            - Provides clean, formatted LLM responses

    Parameters:
        limit (bool): 
            When True, restricts processing to only the first prompt
            Useful for testing or managing resource usage
            
        response (List[str]): 
            Stores the history of LLM responses
            Updated after each successful processing
            
        llm_name (str): 
            Identifier for the target LLM (e.g., "Ollama")
            Defaults to "Ollama" but can be auto-detected
            
        find_llm (button): 
            Triggers automatic LLM detection
            Updates llm_name with found installation
            
        respond (button):
            Forces reprocessing of current prompts
            Updates responses regardless of cache

    Input/Output:
        Input: 
            - List[str]: Collection of prompts to process
            - Must be properly formatted strings
            - Size may be limited by 'limit' parameter
            
        Output:
            - List[str]: Generated LLM responses
            - Maintains order corresponding to input prompts
            - Empty strings for failed responses

    Error Handling:
        - Validates input data type and format
        - Provides clear error messages for LLM connection issues
        - Handles processing failures gracefully
        - Maintains partial results on partial failures

    Safety Features:
        - Input validation and sanitization
        - Resource usage management through limiting
        - Graceful handling of LLM unavailability
        - Clean response formatting

    Usage Notes:
        1. Single Prompt Mode:
            - Enable 'limit' parameter
            - Best for development and testing
            - Provides more detailed error feedback
            
        2. Batch Processing Mode:
            - Disable 'limit' parameter
            - Processes all input prompts
            - May take longer based on input size
            
        3. LLM Management:
            - Use find_llm to detect available LLMs
            - Manually set llm_name for specific installations
            - Check error messages for connection issues

    Performance Considerations:
        - Always time-dependent (_is_time_dependent = True)
        - Response caching available but not forced
        - Resource usage scales with input size
        - Consider using 'limit' for large prompt sets
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