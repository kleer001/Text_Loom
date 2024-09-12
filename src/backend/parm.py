import ast
import bandit
from bandit.core import manager
from typing import Dict, Tuple, Union, Any
import re
from enum import Enum
from typing import Dict, Tuple, Union, Callable 
from typing import List, Optional
from base_classes import OperationFailed

"""Defines parameter types and the Parm class for node-based operations.
Provides functionality for parameter management, evaluation, and script execution."""

class ParameterType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BUTTON = "button"
    TOGGLE = "toggle"
    MENU = "menu"

class Parm:

    """
    Represents a parameter with various types and associated operations.
    Handles parameter value setting, evaluation, and script execution for node interactions.
    """

    def __init__(self, name: str, parm_type: ParameterType, node: 'Node'):
        self._name: str = name
        self._type: ParameterType = parm_type
        self._node: 'Node' = node
        self._script_callback: str = ""
        self._value: Union[int, float, str] = "" # Initial value, to be set later

    def name(self) -> str:
        """Returns this parameter's name."""
        return self._name

    def setName(self, name: str) -> None:
        """Change the name of this parm."""
        self._name = name

    def type(self) -> ParameterType:
        """Returns the parameter type."""
        return self._type

    def path(self) -> str:
        """Returns the full path to this parameter."""
        return f"{self._node.node_path()}/{self.name()}"

    def node(self) -> 'Node':
        """Returns the node on which this parameter exists."""
        return self._node

    def set(self, value: Union[int, float, str]) -> None:
        """Sets the parameter value."""
        if self._type == ParameterType.INT:
            self._value = int(value)
        elif self._type == ParameterType.FLOAT:
            self._value = float(value)
        elif self._type == ParameterType.STRING:
            self._value = str(value)
        else:
            raise TypeError(f"Cannot set value of type {type(value)} for parameter of type {self._type}")

    def script_callback(self) -> str:
        """Return the contents of the script that gets runs when this parameter changes."""
        return self._script_callback

    def set_script_callback(self, script_callback: str) -> None:
        """Set the callback script to the given string."""
        self._script_callback = script_callback

    def press_button(self, arguments: Dict[str, Any] = {}) -> None:
        """
        Emulates clicking a button parameter to trigger its callback script.
        
        Raises:
            OperationFailed: If the callback script could not be run.
            TypeError: If an argument value type is unsupported.
        """
        if self._type != ParameterType.BUTTON:
            raise OperationFailed("Parameter is not a button.")
        
        expanded_script = self._expand_dollar_signs(self._script_callback)
        if self._check_script_safety(expanded_script):
            try:
                result = eval(expanded_script, {'__builtins__': {}}, arguments)
                self.set(str(result))
            except Exception as e:
                raise OperationFailed(f"Failed to execute button script: {str(e)}")
        else:
            raise OperationFailed("Script failed safety check")

    def menu_keys(self) -> Tuple[str, ...]:
        """Returns a tuple of keys for the menu items."""
        if self._type != ParameterType.MENU:
            raise OperationFailed("Parameter is not a menu.")
        try:
            menu_dict = ast.literal_eval(self._value)
            return tuple(menu_dict.keys())
        except:
            raise OperationFailed("Invalid menu format")

    def menu_values(self) -> Tuple[str, ...]:
        """Returns a tuple of values for the menu items."""
        if self._type != ParameterType.MENU:
            raise OperationFailed("Parameter is not a menu.")
        try:
            menu_dict = ast.literal_eval(self._value)
            return tuple(menu_dict.values())
        except:
            raise OperationFailed("Invalid menu format")

    def menu_items(self) -> Tuple[Tuple[str, str], ...]:
        """Returns a tuple of (key, value) pairs for the menu items."""
        if self._type != ParameterType.MENU:
            raise OperationFailed("Parameter is not a menu.")
        try:
            menu_dict = ast.literal_eval(self._value)
            return tuple(menu_dict.items())
        except:
            raise OperationFailed("Invalid menu format")

    def eval(self) -> Any:
        """Evaluates this parameter and returns the result."""
        print(f"Debug: Evaluating parameter {self._name}, raw value: {self._value}")

        if self._type == ParameterType.INT:
            return int(self._value)
        elif self._type == ParameterType.FLOAT:
            return float(self._value)
        elif self._type == ParameterType.STRING:
            return self._expand_and_evaluate(str(self._value))
        elif self._type in [ParameterType.BUTTON, ParameterType.TOGGLE, ParameterType.MENU]:
            return self._value
        else:
            raise OperationFailed(f"Unsupported parameter type: {self._type}")

    def _expand_and_evaluate(self, value: str) -> str:
        """Expands dollar signs and evaluates backticks until no more changes occur."""
        previous_value = None
        current_value = value

        while current_value != previous_value:
            previous_value = current_value
            current_value = self._expand_dollar_signs(current_value)
            current_value = self._eval_backticks(current_value)

        return current_value

    def _eval_backticks(self, value: str) -> str:
        """Evaluates expressions within backticks."""
        def evaluate_expression(match):
            expr = match.group(1)
            try:
                if self._check_script_safety(expr):
                    result = eval(expr, {'__builtins__': {}}, {})
                    return str(result)
                else:
                    raise OperationFailed(f"Expression failed safety check: {expr}")
            except Exception as e:
                print(f"Error evaluating expression '{expr}': {str(e)}")
                return match.group(0)

        return re.sub(r'`([^`]+)`', evaluate_expression, value)

    def raw_value(self) -> str:
        """Returns the parameter's raw text value without evaluation or expansion."""
        return self._value

    def expression(self) -> str:
        """
        Returns this parameter's expression.
        
        Raises:
            OperationFailed: If the parameter does not contain an expression.
        """
        matches = re.findall(r'`(.*?)`', self._value)
        if matches:
            return ' '.join(matches)
        else:
            raise OperationFailed("Parameter does not contain an expression")

    def is_expression(self) -> bool:
        """Returns True if the parameter contains one or more valid functions in backticks."""
        return bool(re.search(r'`.*?`', self._value))

    def _expand_dollar_signs(self, value: str, loop_number: Optional[int] = None) -> str:
        """
        Expands $$ expressions in the given value.
        
        Args:
            value (str): The input string containing $$ expressions.
            loop_number (Optional[int]): The optional loop number for $$N replacement.
        
        Returns:
            str: The expanded string with $$ expressions replaced.
        """
        def replace(match):
            expression = match.group(0)
            
            # Handle $$N replacement
            if expression == "$$N":
                if loop_number is None:
                    print(f"Warning: Found $$N but no loop_number provided.")
                    return expression
                return str(loop_number)
            
            # Handle $$<number> replacement
            if match.group(1).isdigit():
                index = int(match.group(1)) - 1
                if self.node.inputs and self.node.inputs[0].list:
                    input_list = self.node.inputs[0].list
                    modulo_index = index % len(input_list)
                    if modulo_index != index:
                        print(f"Modulo replacement: {expression} -> $${modulo_index + 1}")
                    return str(input_list[modulo_index])
                return expression
            
            # Handle malformed $$ expressions
            print(f"Warning: Malformed $$ expression found: {expression}")
            return expression

        # Updated regex pattern to catch malformed $$ expressions
        pattern = r'\$\$N|\$\$(\d+)|\$\$\S*'
        return re.sub(pattern, replace, value)


    def _check_script_safety(self, script: str) -> bool:
        allowed_modules = {'os', 'math', 'time'}  # Add more as needed
        allowed_functions = {'open', 'read', 'write', 'join', 'split'}  # Add more as needed

        try:
            tree = ast.parse(script)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in allowed_modules:
                            return False
                elif isinstance(node, ast.ImportFrom):
                    if node.module not in allowed_modules:
                        return False
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id not in allowed_functions:
                            return False
                elif isinstance(node, ast.Attribute):
                    if node.attr not in allowed_functions:
                        return False
            return True
        except SyntaxError:
            return False

