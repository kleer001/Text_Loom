import ast
import bandit
from bandit.core import manager
from typing import Dict, Tuple, Union, Any
import re
import operator
import builtins
import math, datetime, random
from enum import Enum
from typing import Dict, Tuple, Union, Callable
from typing import List, Optional
from .base_classes import OperationFailed
from .loop_manager import *
from .global_store import GlobalStore


"""Defines parameter types and the Parm class for node-based operations.
Provides functionality for parameter management, evaluation, and script execution."""


class ParameterType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BUTTON = "button"
    TOGGLE = "toggle"  # Boolean
    MENU = "menu"
    STRINGLIST = "stringList"


class Parm:
    """
    Represents a parameter with various types and associated operations.
    Handles parameter value setting, evaluation, and script execution for node interactions.
    """

    __patterns = {
        # please pay special attention to the order of the patterns when used in a group as this
        # is how if and case control flow statements will filter them.
        # The default positions are noted below. 
        # Evenatually we will refactor them to be one offs and will no longer need to count them
        #     --------------
        # ~ Global variables in various contexts ~
        # All global varaible must be two or more caplital letters
        # Examples: `function($FOO)`, $$M+$FOO, ${$FOO * 5}, ${$FOO}, `$FOO`
        #
        # MATCH 1,2,3 (with the global variable $FOO
        # 1 = `$FOO` , 2 = $$M*3+$FOO , 3 = ${ $FOO }
        #
        'GLOBAL': r"`[^`]*\$[A-Z]{2,}[^`]*`|\$\$M\S*\$[A-Z]{2,}|\$\{[^}]*\$[A-Z]{2,}[^}]*\}",
        
        
        # ~ Simple loop number ~
        # Matches $$N - represents the current loop number
        #
        # MATCH 4
        #
        'NLOOP': r"\$\$N",
        
        # ~ Math loop number ~
        # Matches $$M followed by an optional arithmetic operation and a number
        # Examples: $$M+5, $$M-3, $$M*2, $$M/4, $$M%3
        #
        # MATCH 5
        #
        'MLOOP': r"\$\$M([-+*/%]?\d+)",
        
        # ~ Explicit Number for input list item ~
        # Matches $$ followed by one or more digits
        # Example: $$1, $$42, $$100
        #
        # MATCH 6
        #
        'NUMBER': r"\$\$(\d+)",
                
        # ~ Backticks for python code ~
        #
        # MATCH 7
        #
        'BACKTICK': r"`([^`]+)`",

        # ~ loop number its self~
        # Matches $$L - represents the current loop number
        #
        # MATCH 8
        #
        'NLOOP': r"\$\$L",
    }

    def __init__(self, name: str, parm_type: ParameterType, node: "Node"):
        self._name: str = name
        self._type: ParameterType = parm_type
        self._node: "Node" = node
        self._script_callback: str = ""
        self._value: Union[int, float, str, List[str], bool] = (
            ""  # Initial value, to be set later
        )

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

    def node(self) -> "Node":
        """Returns the node on which this parameter exists."""
        return self._node

    def set(self, value: Union[int, float, str, List[str], bool]) -> None:
        if self._type == ParameterType.STRINGLIST:
            if not isinstance(value, list):
                raise TypeError(f"Expected list for STRINGLIST, got {type(value)}")
            self._value = [str(item) for item in value]
        elif self._type == ParameterType.INT:
            self._value = int(value)
        elif self._type == ParameterType.FLOAT:
            self._value = float(value)
        elif self._type == ParameterType.STRING:
            self._value = str(value)
        elif self._type == ParameterType.TOGGLE:
            self._value = bool(value)
        else:
            raise TypeError(
                f"Cannot set value of type {type(value)} for parameter of type {self._type}"
            )

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

        expanded_script = self._expand_dollar_signs(self._script_callback) #This looks old and broken 
        if self._check_script_safety(expanded_script):
            try:
                result = eval(expanded_script, {"__builtins__": {}}, arguments)
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


    def _get_patterns(self, selected_patterns: Optional[Union[str, List[str]]] = None) -> str:
        patterns = self.__patterns
        if selected_patterns is None:
            return '|'.join(patterns.values())
        elif isinstance(selected_patterns, str):
            if selected_patterns not in patterns:
                raise ValueError(f"Invalid pattern key: {selected_patterns}")
            return patterns[selected_patterns]
        else:
            invalid_keys = set(selected_patterns) - set(patterns.keys())
            if invalid_keys:
                raise ValueError(f"Invalid pattern key(s): {', '.join(invalid_keys)}")
            pattern_return = '|'.join(patterns[key] for key in selected_patterns)
            #print("returning pattern ",pattern_return)
            return pattern_return

    def eval(self) -> Any:
        if self._type == ParameterType.STRINGLIST:
            return [self._expand_and_evaluate(str(item)) for item in self._value]
        elif self._type == ParameterType.INT:
            return int(self._value)
        elif self._type == ParameterType.FLOAT:
            return float(self._value)
        elif self._type == ParameterType.STRING:
            if self.is_expression():
                return self._expand_and_evaluate(str(self._value))
            else:
                return str(self._value)
        elif self._type == ParameterType.TOGGLE:
            return bool(self._value)
        elif self._type in [ParameterType.BUTTON, ParameterType.MENU]:
            return self._value
        else:
            raise OperationFailed(f"Unsupported parameter type: {self._type}")

    def _expand_and_evaluate(self, value: str) -> str:
        current_value = value
        current_value = self._expand_loop_number(current_value)
        current_value = self._expand_globals(current_value)
        current_value = self._expand_dollar_signs(current_value)
        current_value = self._eval_backticks(current_value)
        current_value = self._clean_globals(current_value)
        return current_value

    def _expand_globals(self, value: str) -> str:
        global_store = GlobalStore()
        def replace_global(match):
            global_var = match.group(0)
            global_var = global_var[1:] 
            #print(f"🌐 Processing global variable: {global_var}")
            
            if not global_store.has(global_var):
                #print(f"🌐 Warning: Global variable {global_var} not found")
                return global_var
            
            replacement_value = str(global_store.get(global_var))
            #print(f"🌐 Replacing {global_var} with: {replacement_value}")
            return replacement_value

        def replace_container(match):
            container = match.group(0)
            #base global far aka $FOO
            return re.sub(r'\$[A-Z]{2,}', replace_global, container)

        pattern = self._get_patterns('GLOBAL')
        result = re.sub(pattern, replace_container, value)
        return result

    def _clean_globals(self, value: str) -> str: 
        pattern = r'\$\{(.*?)\}'
        return re.sub(pattern, r'\1', value)


    def create_safe_globals(self):
        # List of allowed builtin function names
        allowed_builtins = [
            'len', 'abs', 'round', 'min', 'max', 'sum',
            'sorted', 'reversed', 'list', 'tuple', 'set', 'dict',
            'range', 'enumerate', 'zip',
            'isinstance', 'type', 'ascii',
            'int', 'float', 'str', 'bool',
            'print', 'True', 'False', 'None'
        ]

        # Create safe_builtins dictionary efficiently
        safe_builtins = {name: getattr(builtins, name) for name in allowed_builtins}

        # Create safe_modules dictionary
        safe_modules = {
            'math': math,
            'datetime': datetime,
            'random': random
        }

        # Combine safe_builtins and safe_modules
        return {'__builtins__': safe_builtins, **safe_modules}

    def _check_script_safety(self, script: str) -> bool:
        allowed_modules = {"math", "datetime", "random"}
        allowed_functions = set(self.create_safe_globals()['__builtins__'].keys()) | {"str.lower", "str.upper", "str.strip", "str.replace", "str.split", "str.join"}

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


    def _eval_backticks(self, value: str) -> str:
        """Evaluates expressions within backticks."""

        def evaluate_expression(match):
            script = match.group(1)
            if self._check_script_safety(script):
                safe_globals = self.create_safe_globals()
                safe_locals = {}
                exec_return = eval(script, safe_globals, safe_locals)
                #print("EVAL ", script," RETURNS ", exec_return)
                return exec_return
            else:
                raise ValueError("Script contains unsafe operations")

        return re.sub(r"`([^`]+)`", evaluate_expression, value)

    def raw_value(self) -> str:
        """Returns the parameter's raw text value without evaluation or expansion."""
        return self._value

    def expression(self) -> str:
        """
        Returns this parameter's expression.

        Raises:
            OperationFailed: If the parameter does not contain an expression.
        """
        matches = re.findall(r"`(.*?)`", self._value)
        if matches:
            return " ".join(matches)
        else:
            raise OperationFailed("Parameter does not contain an expression")

    def is_expression(self) -> bool:
        """Returns True if the parameter contains one or more valid functions accoring to self.__patterns ."""
        all_patterns = self._get_patterns()
        return bool(re.search(all_patterns, self._value))
        #return bool(re.search(r"`[^`]*`|\$\$N|\$\$M([-+*/%]?\d+)|\$\$(\d+)", self._value))

    def _expand_loop_number(self, value: str) -> str: 
        loop_number = loop_manager.get_current_loop(self.node().path()) - 1
        result = value.replace("$$L", str(loop_number))
        return result

    def _expand_dollar_signs(self, value: str) -> str:
        def evaluate_arithmetic(expression: str, loop_number: int) -> int:
            ops = {
                '+': operator.add,
                '-': operator.sub,
                '*': operator.mul,
                '/': operator.truediv,
                '%': operator.mod
            }
            
            tokens = re.findall(r'[-+*/%]|\d+', expression)
            result = loop_number if tokens[0] in ops else int(tokens[0])
            
            for i in range(0, len(tokens) - 1, 2):
                op, value = tokens[i], int(tokens[i + 1])
                if op in ops:
                    result = ops[op](result, value)
                else:
                    #print(f"$$ Warning: Invalid operator: {op}")
                    return loop_number
            
            return result

        def replace(match):
            expression = match.group(0)
            loop_number = loop_manager.get_current_loop(self.node().path()) - 1
            
            if not self.node().inputs():
                #print(f"$$ Warning: No valid input list found for {expression}")
                return expression
            
            input_list = self.node().inputs()[0].output_node().eval()
            list_length = len(input_list)
            
            if list_length == 0:
                #print(f"$$ Warning: Empty input list for {expression}")
                return expression
            
            if match.group(0):
                index = loop_number % list_length
                print(f"$$ Resolved index for $$N: {index}")
            elif match.group(1):  # $$M expression
                arithmetic_result = evaluate_arithmetic(match.group(1), loop_number)
                index = arithmetic_result % list_length
                #print(f"$$ Resolved index for {expression}: {index} (Arithmetic result: {arithmetic_result})")
            elif match.group(2):  # $$<number> expression
                index = (int(match.group(2)) - 1) % list_length
                #print(f"$$ Resolved index for {expression}: {index}")
            else:
                #print(f"$$ Warning: Malformed $$ expression: {expression}")
                return expression
            
            replacement_value = str(input_list[index])
            print(f"Replacing {expression} with: {replacement_value}")
            return replacement_value

        pattern = r"\$\$N|\$\$M([-+*/%\d]+)|\$\$(\d+)"
        result = re.sub(pattern, replace, value)
        return result

