import ast
from typing import Dict, Tuple, Union, Any
import re
import operator
import builtins
import math, datetime, random
from enum import Enum
from typing import Dict, Tuple, Union, Callable
from typing import List, Optional
from core.base_classes import OperationFailed
from core.loop_manager import *
from core.global_store import GlobalStore
from core.base_classes import OperationFailed, NodeState

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
        # Stage 1: Global Variables with optional math
        'GLOBAL': r"\$[A-Z]{2,}([-+*/%]\d+)?",     # $FOO, $FOO+4
        
        # Stage 2: Loop Number
        'LOOP_NUMBER': r"\$\$L",                    # $$L
        
        # Stage 3: Combined List Access
        'LIST_ACCESS': r"\$\$(?:N([-+*/%]\d+)?|(\d+))",  # $$N, $$N*8, $$1
        
        # Stage 4: Python Code
        'PYTHON_CODE': r"`([^`]+)`"                # `len("test")`
    }

    def __init__(self, name: str, parm_type: ParameterType, node: "Node"):
        self._name: str = name
        self._type: ParameterType = parm_type
        self._node: "Node" = node
        self._script_callback: str = ""
        self._value: Union[int, float, str, List[str], bool] = ""
        self._default_value: Union[int, float, str, List[str], bool] = ""
        self._is_default: bool = True


    def name(self) -> str:
        """Returns this parameter's name."""
        return self._name

    def set_name(self, name: str) -> None:
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

    @property
    def is_default(self) -> bool:
        return self._is_default
        
    @property 
    def default_value(self):
        return self._default_value

    def set(self, value: Union[int, float, str, List[str], bool, Dict[str, str]]) -> None:
        from core.undo_manager import UndoManager

        if self._type == ParameterType.STRINGLIST:
            if not isinstance(value, list):
                raise TypeError(f"Expected list for STRINGLIST, got {type(value)}")
            new_value = [str(item) for item in value]
        elif self._type == ParameterType.INT:
            new_value = int(value)
        elif self._type == ParameterType.FLOAT:
            new_value = float(value)
        elif self._type == ParameterType.STRING:
            new_value = str(value)
        elif self._type == ParameterType.TOGGLE:
            new_value = bool(value)
        elif self._type == ParameterType.MENU:
            # MENU accepts either a dict (to set menu options) or a string (to select an option)
            if isinstance(value, dict):
                new_value = str(value)
            else:
                new_value = str(value)
        else:
            raise TypeError(f"Cannot set value type {type(value)} for parameter type {self._type}")

        if new_value != self._value:
            UndoManager().push_state(f"Set {self.node().name()} parm: {self.name()} to {value}")
            if self._default_value == "":
                self._default_value = new_value
            self._value = new_value
            self._is_default = (self._value == self._default_value)
            self._node.set_state(NodeState.UNCOOKED)

    def script_callback(self) -> str:
        """Return the contents of the script that gets runs when this parameter changes."""
        return self._script_callback

    def set_script_callback(self, script_callback: str) -> None:
        """Set the callback script to the given string."""
        self._script_callback = script_callback

    def press_button(self, arguments: Optional[Dict[str, Any]] = None) -> None:
        """
        Executes a button parameter's callback script with proper safety checks.
        
        Args:
            arguments: Optional dictionary of arguments to pass to the script

        Raises:
            OperationFailed: If parameter is not a button or script execution fails
            ValueError: If script contains unsafe operations
        """
        if self._type != ParameterType.BUTTON:
            raise OperationFailed("Parameter is not a button.")
            
        if not self._script_callback:
            raise OperationFailed("No callback script defined for button.")
            
        if arguments is None:
            arguments = {}
            
        try:
            processed_script = self._expand_and_evaluate(self._script_callback)
                
            if not self._check_script_safety(processed_script):
                raise ValueError("Script contains unsafe operations")
                
            safe_globals = self.create_safe_globals()
            
            safe_locals = arguments.copy()
            
            result = eval(processed_script, safe_globals, safe_locals)
        
            if result is not None:
                if isinstance(result, (int, float, bool, str, list)):
                    self.set(result)
                else:
                    self.set(str(result))
            return result
        except Exception as e:
            raise OperationFailed(f"Failed to execute button script: {str(e)}")

    def _get_menu_dict(self) -> dict:
        """Returns parsed menu dictionary or raises OperationFailed with helpful message."""
        if self._type != ParameterType.MENU:
            raise OperationFailed(f"Cannot access menu data on parameter of type {self._type}")
        
        try:
            return ast.literal_eval(self._value)
        except (ValueError, SyntaxError):
            raise OperationFailed(f"Invalid menu format in parameter {self.name()}")

    def menu_keys(self) -> Tuple[str, ...]:
        """Returns tuple of menu option keys."""
        return tuple(self._get_menu_dict().keys())

    def menu_values(self) -> Tuple[str, ...]:
        """Returns tuple of menu option values."""
        return tuple(self._get_menu_dict().values())

    def menu_items(self) -> Tuple[Tuple[str, str], ...]:
        """Returns tuple of (key, value) pairs for menu options."""
        return tuple(self._get_menu_dict().items())


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
            print("returning pattern ",pattern_return)
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
                #print(f"CONTAINS EXPRESSION {self.raw_value()}")
                return self._expand_and_evaluate(str(self._value))
            else:
                #print(f"DOES NOT CONTAIN EXPRESSION  {self.raw_value()}")
                return str(self._value)
        elif self._type == ParameterType.TOGGLE:
            return bool(self._value)
        elif self._type in [ParameterType.BUTTON, ParameterType.MENU]:
            return self._value
        else:
            raise OperationFailed(f"Unsupported parameter type: {self._type}")

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
        matches = re.finditer(all_patterns, self._value)
        
        # Store result before printing since we need to use matches twice
        has_matches = False
        matching_strings = []
        
        for match in matches:
            has_matches = True
            matching_strings.append(match.group(0))
        
        if matching_strings:
            print(f"Expression matches in {self.name()}: {matching_strings}")
            
        return has_matches

    def _process_global(self, match) -> str:
        var_part = match.group(0)
        var_name = var_part[1:]  # Remove $
        math_part = None
        
        # Split variable and math if exists
        for op in ['+', '-', '*', '/', '%']:
            if op in var_name:
                var_name, math_part = var_name.split(op)
                math_part = op + math_part
                break
        
        global_store = GlobalStore()
        if not global_store.has(var_name):
            print(f"🌐 Warning: Global variable {var_name} not found")
            return match.group(0)
            
        value = global_store.get(var_name)
        
        if math_part:
            try:
                op = math_part[0]
                num = int(math_part[1:])
                ops = {'+': operator.add, '-': operator.sub, 
                      '*': operator.mul, '/': operator.truediv, 
                      '%': operator.mod}
                value = ops[op](float(value), num)
                print(f"🌐 Global {var_name} with {math_part} = {value}")
            except (ValueError, TypeError) as e:
                print(f"🌐 Error processing math for {var_name}: {e}")
                return match.group(0)
        else:
            print(f"🌐 Global {var_name} = {value}")
            
        return str(value)

    def _process_list_access(self, match) -> str:
        expression = match.group(0)
        
        if not self.node().inputs():
            print(f"📝 Warning: No input list found for {expression}")
            return expression
            
        input_list = self.node().inputs()[0].output_node().eval()
        if not input_list:
            print(f"📝 Warning: Empty input list for {expression}")
            return expression
            
        list_length = len(input_list)
        loop_number = loop_manager.get_current_loop(self.node().path()) - 1

        try:
            # Handle $$N cases (with or without math)
            if expression.startswith("$$N"):
                if match.group(1):  # Has math
                    op = match.group(1)[0]
                    num = int(match.group(1)[1:])
                    ops = {'+': operator.add, '-': operator.sub, 
                          '*': operator.mul, '/': operator.truediv, 
                          '%': operator.mod}
                    index = int(ops[op](loop_number, num)) % list_length
                    print(f"📝 List access with {match.group(1)} = index {index}")
                else:  # Simple $$N
                    index = loop_number % list_length
                    print(f"📝 Simple list access = index {index}")
            # Handle $$1 style cases
            else:
                index = (int(match.group(2)) - 1) % list_length
                print(f"📝 Direct index access = index {index}")
                
            result = str(input_list[index])
            print(f"📝 Retrieved: {result}")
            return result
            
        except (ValueError, TypeError) as e:
            print(f"📝 Error processing list access: {e}")
            return expression

    def _process_list_index(self, match) -> str:
        expression = match.group(0)
        
        if not self.node().inputs():
            print(f"📑 Warning: No input list found for {expression}")
            return expression
            
        input_list = self.node().inputs()[0].output_node().eval()
        if not input_list:
            print(f"📑 Warning: Empty input list for {expression}")
            return expression
            
        list_length = len(input_list)
        try:
            index = (int(match.group(1)) - 1) % list_length
            result = str(input_list[index])
            print(f"📑 Direct index {match.group(1)} = {result} (index {index})")
            return result
        except (ValueError, TypeError) as e:
            print(f"📑 Error processing index: {e}")
            return expression

    def _process_python_code(self, match) -> str:
        script = match.group(1)
        print(f"🐍 Evaluating: {script}")
        
        if not self._check_script_safety(script):
            print("🐍 Error: Unsafe script detected")
            raise ValueError("Script contains unsafe operations")
            
        try:
            safe_globals = self.create_safe_globals()
            result = str(eval(script, safe_globals, {}))
            print(f"🐍 Result: {result}")
            return result
        except Exception as e:
            print(f"🐍 Error evaluating script: {e}")
            return match.group(0)

    def _expand_and_evaluate(self, value: str) -> str:
        result = value
        #print(f"\n🔄 Processing: {value}")

        # Stage 1: Global Variables
        result = re.sub(self._get_patterns('GLOBAL'), 
                       self._process_global, result)

        # Stage 2: Loop Number
        loop_number = loop_manager.get_current_loop(self.node().path()) - 1
        result = result.replace("$$L", str(loop_number))
        if "$$L" in value:
            print(f"🔢 Loop number {loop_number}")

        # Stage 3: List Access (combined)
        result = re.sub(self._get_patterns('LIST_ACCESS'), 
                       self._process_list_access, result)

        # Stage 4: Python Code
        result = re.sub(self._get_patterns('PYTHON_CODE'), 
                       self._process_python_code, result)

        #print(f"🔄 Final result: {result}\n")
        return result


    def create_safe_globals(self):
        allowed_builtins = [
            'len', 'abs', 'round', 'min', 'max', 'sum',
            'sorted', 'reversed', 'list', 'tuple', 'set', 'dict',
            'range', 'enumerate', 'zip',
            'isinstance', 'type', 'ascii',
            'int', 'float', 'str', 'bool',
            'print', 'True', 'False', 'None'
        ]
        safe_builtins = {name: getattr(builtins, name) for name in allowed_builtins}
        safe_modules = {
            'math': math,
            'datetime': datetime,
            'random': random
        }

        # Combine safe_builtins and safe_modules
        return {'__builtins__': safe_builtins, **safe_modules}

    def _check_script_safety(self, script: str) -> bool:
        """
        Check if a Python script contains only allowed operations.
        
        Args:
            script: The Python script to check
            
        Returns:
            bool: True if the script only uses allowed operations, False otherwise
        """
        try:
            tree = ast.parse(script)
            return self._check_ast_node_safety(tree)
        except SyntaxError:
            return False
            
    def _check_ast_node_safety(self, tree: ast.AST) -> bool:
        """
        Recursively check if all nodes in the AST are safe.
        """
        for node in ast.walk(tree):
            if not self._is_node_safe(node):
                return False
        return True
        
    def _is_node_safe(self, node: ast.AST) -> bool:
        """
        Check if a single AST node is safe based on its type.
        """
        # Define allowed operations
        allowed_modules = {"math", "datetime", "random"}
        allowed_functions = (set(self.create_safe_globals()['__builtins__'].keys()) | 
                            {"str.lower", "str.upper", "str.strip", 
                            "str.replace", "str.split", "str.join"})
        
        # Check different node types
        if isinstance(node, ast.Import):
            return all(alias.name in allowed_modules 
                    for alias in node.names)
                    
        elif isinstance(node, ast.ImportFrom):
            return node.module in allowed_modules
            
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id in allowed_functions
                
        elif isinstance(node, ast.Attribute):
            return node.attr in allowed_functions
            
        # All other node types are considered safe
        return True

    def _expand_loop_number(self, value: str) -> str: 
        loop_number = loop_manager.get_current_loop(self.node().path()) - 1
        result = value.replace("$$L", str(loop_number))
        return result


