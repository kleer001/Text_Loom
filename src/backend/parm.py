import ast
import bandit
from bandit.core import manager
from typing import Dict, Tuple, Union, Any
import re
from enum import Enum
from typing import Dict, Tuple, Union, Callable

class ParameterType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BUTTON = "button"
    TOGGLE = "toggle"
    MENU = "menu"

class Parm:
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
        expanded_value = self._expand_dollar_signs(self._value)
        if self._check_script_safety(expanded_value):
            try:
                return eval(expanded_value, {'__builtins__': {}}, {})
            except Exception as e:
                raise OperationFailed(f"Failed to evaluate parameter: {str(e)}")
        else:
            raise OperationFailed("Expression failed safety check")

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

    def _expand_dollar_signs(self, value: str) -> str:
        """Expands $$ expressions in the given value."""
        def replace(match):
            index = int(match.group(1)) - 1
            inputs = self.node().inputs()
            if inputs:
                return str(inputs[index % len(inputs)])
            return ''
        return re.sub(r'\$\$(\d+)', replace, value)

    def _check_script_safety(self, script: str) -> bool:
        """Checks if the given script is safe to run using bandit."""
        b_mgr = manager.BanditManager(bandit.config.BanditConfig(), bandit.config.BanditConfig().get_option('profile'))
        b_mgr.discover_files([script])
        b_mgr.run_tests()
        return b_mgr.scores[0] == 0  # Return True if no issues found

    def set(self, value: str) -> None:
        """Sets the parameter value."""
        self._value = value