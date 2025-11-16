from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING, Sequence, Union
import re
import importlib
from core.enums import NetworkItemType
from core.enums import NodeState
from core.enums import NodeType
from core.mobile_item import MobileItem
from core.node_connection import NodeConnection
from core.node_environment import NodeEnvironment

if TYPE_CHECKING:
    from core.parm import Parm, ParameterType

class Node(MobileItem):
    """
    Node: The foundational building block of a node-based graph processing system.

    This abstract base class implements a composable, connectable processing unit that forms the 
    backbone of a node graph architecture. Each Node can receive inputs, process data, and provide 
    outputs while maintaining its state and position within a hierarchical structure.

    Core Capabilities:
        1. Graph Structure:
            - Maintains input/output connections to other nodes
            - Supports hierarchical parent-child relationships
            - Handles both single and multi-input/output configurations
            - Prevents circular dependencies and self-connections

        2. Data Processing:
            - Manages data flow between connected nodes
            - Supports dependency-aware processing (cooking)
            - Handles state management and cache invalidation
            - Provides type-safe data connections

        3. State Management:
            - Tracks processing state (UNCOOKED, COOKING, UNCHANGED)
            - Maintains error and warning messages
            - Records performance metrics (cook time, cook count)
            - Handles time-dependent behavior

    Key Components:
        Connections:
            - Input connections: Dict[int, NodeConnection]
            - Output connections: Dict[int, List[NodeConnection]]
            - Supports multiple connection types and data validation
            - Manages connection creation, removal, and updates

        State Tracking:
            - Processing state management
            - Error and warning collection
            - Cook time and count metrics
            - Hash-based change detection

        Hierarchical Structure:
            - Parent-child relationships
            - Path-based node location
            - Child management and traversal
            - Position management in workspace

    Safety Features:
        - Prevents circular dependencies
        - Validates connection types
        - Handles connection cleanup on node removal
        - Maintains graph integrity during operations
        - Supports undo/redo operations

    Processing Behavior:
        1. Evaluation (eval):
            - Checks if cooking is needed
            - Manages dependency cooking
            - Returns processed output
            - Handles force evaluation

        2. Cooking Process:
            - Dependency resolution
            - Ordered processing
            - State management
            - Error handling

    Common Usage:
        >>> node = Node.create_node(NodeType.SPLIT, "my_splitter")  # Create new node
        >>> node.set_input(0, input_node)  # Connect input
        >>> result = node.eval()  # Process and get result
        >>> node.cook()  # Force reprocessing
        >>> node.set_parent("/new/path")  # Move in hierarchy

    Subclassing Notes:
        Required Implementations:
            - _internal_cook(): Define node's processing logic
            - input_names(): Define input connection names
            - output_names(): Define output connection names
            - input_data_types(): Define accepted input types
            - output_data_types(): Define provided output types

        Optional Overrides:
            - needs_to_cook(): Custom processing triggers
            - get_output(): Custom output handling
            - post_registration_init(): Setup after creation

    Key Properties:
        SINGLE_INPUT: bool
            If True, node accepts only one input connection
        SINGLE_OUTPUT: bool
            If True, node provides only one output connection
        _is_time_dependent: bool
            If True, node recooks on every evaluation

    Error Handling:
        - Maintains lists of errors and warnings
        - Provides clear error messages
        - Supports error state propagation
        - Handles connection validation

    Performance Features:
        - Caches processed results
        - Tracks processing time
        - Implements smart reprocessing
        - Supports forced evaluation
    """

    def __init__(self, name: str, path: str, position: List[float],
        node_type: NodeType):
        super().__init__(name, path, position)
        self._node_type: NodeType = node_type
        self._children: List['Node'] = []
        self._depth = self._calculate_depth()
        self._inputs: Dict[int, NodeConnection] = {}
        self._outputs: Dict[int, List[NodeConnection]] = {}
        self._output = None
        self._state: NodeState = NodeState.UNCOOKED
        self._errors: List[str] = []
        self._warnings: List[str] = []
        self._is_time_dependent = False
        self._last_cook_time = 0.0
        self._cook_count = 0
        self._file_hash = None
        self._param_hash = None
        self._last_input_size = 0
        self._input_node = None
        self._output_node = None
        self._internal_nodes_created = False
        self._parent_looper = False

        # Universal enabled toggle - initialized in base class before child classes init their _parms
        # Import at runtime to avoid circular dependency
        from core.parm import Parm, ParameterType
        self._parms: Dict[str, 'Parm'] = {
            "enabled": Parm("enabled", ParameterType.TOGGLE, self),
            "bypass": Parm("bypass", ParameterType.TOGGLE, self),
            "display": Parm("display", ParameterType.TOGGLE, self)
        }
        self._parms["enabled"].set(True)
        self._parms["bypass"].set(False)
        self._parms["display"].set(False)

    def node_path(self) ->str:
        """Returns the current location in the hierarchy of the workspace."""
        return self.path()

    def _calculate_depth(self) ->int:
        """Calculate the depth of this looper node based on its path."""
        return self.path().count('/') + 1

    def children(self) ->Tuple['Node', ...]:
        """Returns a tuple of the list of nodes it's connected to on its output."""
        return tuple(self._children)

    @classmethod
    def sanitize_node_name(cls, name: Optional[str]) ->Optional[str]:
        if not name:
            return None
        sanitized = re.sub('[^a-zA-Z0-9_]', '', name)
        return sanitized if sanitized else None

    @classmethod
    def create_node(cls, node_type: NodeType, node_name: Optional[str]=None,
        parent_path: str='/') ->'Node':
        from core.undo_manager import UndoManager

        sanitized_name = cls.sanitize_node_name(node_name)
        base_name = (f'{node_type.value}_1' if sanitized_name is None else
            sanitized_name)
        new_path = f"{parent_path.rstrip('/')}/{base_name}"
        if new_path not in NodeEnvironment.nodes:
            new_name = base_name
        else:
            number_match = re.search('_(\\d+)$', base_name)
            if number_match:
                prefix = base_name[:number_match.start()]
                counter = int(number_match.group(1)) + 1
            else:
                prefix = base_name
                counter = 1
            while True:
                new_name = f'{prefix}_{counter}'
                new_path = f"{parent_path.rstrip('/')}/{new_name}"
                if new_path not in NodeEnvironment.nodes:
                    break
                counter += 1
        new_path = f"{parent_path.rstrip('/')}/{new_name}"

        UndoManager().push_state(f'Create node: {new_path}')

        if parent_path != '/' and not NodeEnvironment.node_exists(parent_path):
            raise ValueError(f"Parent path '{parent_path}' does not exist.")
        try:
            module_name = f'core.{node_type.value}_node'
            module = importlib.import_module(module_name)
            class_name = ''.join(word.capitalize() for word in node_type.
                value.split('_'))
            node_class = getattr(module, f'{class_name}Node')

            new_node = node_class(new_name, new_path, node_type)

            # Note: session_id is already generated in MobileItem.__init__()
            NodeEnvironment.add_node(new_node)

            if hasattr(new_node.__class__, 'post_registration_init'):
                UndoManager().disable()
                try:
                    new_node.__class__.post_registration_init(new_node)
                finally:
                    UndoManager().enable()

            return new_node
        except ImportError:
            raise ImportError(
                f'Could not import module for node type: {node_type.value}')
        except AttributeError:
            raise AttributeError(
                f'Could not find node class for node type: {node_type.value}')

    def destroy(self) ->None:
        from core.undo_manager import UndoManager
        UndoManager().push_state(f'Delete node: {self.node_path()}')
        for conn in list(self._inputs.values()):
            output_node = conn.output_node()
            output_idx = conn.output_index()
            if output_idx in output_node._outputs:
                if conn in output_node._outputs[output_idx]:
                    output_node._outputs[output_idx].remove(conn)
            del self._inputs[conn.input_index()]
            del conn
        for output_idx, conns in list(self._outputs.items()):
            for conn in list(conns):
                input_node = conn.input_node()
                input_idx = conn.input_index()
                if input_idx in input_node._inputs:
                    del input_node._inputs[input_idx]
                del conn
            self._outputs[output_idx].clear()
        NodeEnvironment.remove_node_from_dictionary(self.node_path())

    def type(self) ->NodeType:
        """Returns the NodeType for this node."""
        return self._node_type

    def inputs(self) ->Tuple[NodeConnection, ...]:
        """Returns a tuple of the NodeConnections connected to this node's input."""
        return tuple(self._inputs.values())

    def input_nodes(self) ->List['Node']:
        """
        Returns a list of all nodes connected to this node's inputs.
            """
        return [conn.output_node() for conn in self.inputs()]

    def outputs(self) ->Tuple['Node', ...]:
        """Returns a tuple of the nodes connected to this node's output."""
        return tuple(conn.input_node() for conns in self._outputs.values() for
            conn in conns)

    def set_input(self, input_index: int, input_node: 'Node', output_index:
        int=0) ->None:
        from core.undo_manager import UndoManager

        # Defensive type checking - ensure indices are integers
        if not isinstance(input_index, int):
            raise TypeError(f"input_index must be int, got {type(input_index).__name__}: {input_index}")
        if not isinstance(output_index, int):
            raise TypeError(f"output_index must be int, got {type(output_index).__name__}: {output_index}")

        # Validate indices are non-negative
        if input_index < 0:
            raise ValueError(f"input_index must be non-negative, got {input_index}")
        if output_index < 0:
            raise ValueError(f"output_index must be non-negative, got {output_index}")

        # Validate output index is in valid range (inputs can be dynamic for MergeNode)
        output_names = input_node.output_names()
        if output_index >= len(output_names):
            raise ValueError(f"output_index {output_index} out of range for {input_node.name()} (0-{len(output_names)-1})")

        UndoManager().push_state(
            f'Connect {input_node.name()}[{output_index}] to {self.name()}[{input_index}]'
            )
        if input_node == self:
            print(f'Rejected self-connection attempt for node: {self.name()}')
            return
        if hasattr(self, 'SINGLE_INPUT'
            ) and self.SINGLE_INPUT and self._inputs:
            self.add_warning(
                f'Node type {self.__class__.__name__} accepts only one input. Existing input will be replaced.'
                )
            UndoManager().disable()
            self.remove_connection(next(iter(self._inputs.values())))
            UndoManager().enable()
        if input_index in self._inputs:
            UndoManager().disable()
            self.remove_connection(self._inputs[input_index])
            UndoManager().enable()
        connection = NodeConnection(input_node, self, output_index, input_index
            )
        print('New Connection: from input ', self.name(), 'at ', input_index, ' to output: ',
            input_node.name(), 'at ', output_index)
        self._inputs[input_index] = connection
        input_node._outputs.setdefault(output_index, []).append(connection)
        self.set_state(NodeState.UNCOOKED)

    def set_next_input(self, input_node: 'Node', output_index: int=0) ->None:
        from core.undo_manager import UndoManager
        next_input_index = 0
        if hasattr(self, 'SINGLE_INPUT') and self.SINGLE_INPUT:
            next_input_index = 0
        elif not self._inputs:
            next_input_index = 0
        else:
            next_input_index = max(self._inputs.keys()) + 1
        UndoManager().push_state(
            f'Connect {input_node.name()}[{output_index}] to {self.name()}[{next_input_index}]'
            )
        UndoManager().disable()
        try:
            if hasattr(self, 'SINGLE_INPUT') and self.SINGLE_INPUT:
                self.set_input(0, input_node, output_index)
            elif not self._inputs:
                self.set_input(0, input_node, output_index)
            else:
                self.set_input(next_input_index, input_node, output_index)
        finally:
            UndoManager().enable()

    def remove_input(self, input_index: int) ->None:
        from core.undo_manager import UndoManager
        UndoManager().push_state(
            f'Remove input {input_index} from {self.name()}')
        if input_index in self._inputs:
            try:
                UndoManager().disable()
                self.remove_connection(self._inputs[input_index])
            finally:
                UndoManager().enable()

    def remove_connection(self, connection: NodeConnection) ->None:
        from core.undo_manager import UndoManager
        UndoManager().push_state(
            f'Remove connection between {connection.output_node().name()} and {connection.input_node().name()}'
            )

        # Clean up input side
        if connection.input_node() == self:
            input_idx = connection.input_index()
            if input_idx in self._inputs and self._inputs[input_idx] == connection:
                del self._inputs[input_idx]
                self.set_state(NodeState.UNCOOKED)

        # Clean up output side
        if connection.output_node() == self:
            output_idx = connection.output_index()
            if output_idx in self._outputs:
                if connection in self._outputs[output_idx]:
                    self._outputs[output_idx].remove(connection)

        # NEW: Also clean up the OTHER node's side
        # If we're the input node, clean up the output node's outputs
        if connection.input_node() == self:
            output_node = connection.output_node()
            output_idx = connection.output_index()
            if output_idx in output_node._outputs:
                if connection in output_node._outputs[output_idx]:
                    output_node._outputs[output_idx].remove(connection)

        # If we're the output node, clean up the input node's inputs
        elif connection.output_node() == self:
            input_node = connection.input_node()
            input_idx = connection.input_index()
            if input_idx in input_node._inputs and input_node._inputs[input_idx] == connection:
                del input_node._inputs[input_idx]

    def set_parent(self, new_parent_path: str) ->None:
        from core.undo_manager import UndoManager
        old_path = self.path()
        UndoManager().push_state(f'Move {old_path} to {new_parent_path}')
        try:
            new_path, name_changed = NodeEnvironment.update_node_path(old_path,
                new_parent_path)
            if name_changed:
                print(
                    f'Node renamed to maintain uniqueness at new location: {new_path}'
                    )
        except ValueError as e:
            print(f'Failed to move node: {e}')
            return

    def state(self) ->NodeState:
        """Returns the current state of the node."""
        return self._state

    def set_state(self, state: NodeState) ->None:
        """Sets the state of the node."""
        self._state = state

    def errors(self) ->Tuple[str, ...]:
        """Returns a tuple of error messages associated with this node."""
        return tuple(self._errors)

    def add_error(self, error: str) ->None:
        """Adds an error message to this node."""
        self._errors.append(error)

    def clear_errors(self) ->None:
        """Clears all error messages from this node."""
        self._errors.clear()

    def warnings(self) ->Tuple[str, ...]:
        """Returns a tuple of warning messages associated with this node."""
        return tuple(self._warnings)

    def add_warning(self, warning: str) ->None:
        """Adds a warning message to this node."""
        self._warnings.append(warning)

    def clear_warnings(self) ->None:
        """Clears all warning messages from this node."""
        self._warnings.clear()

    def input_names(self) ->Dict[int, str]:
        input_count = max(self._inputs.keys()) + 1 if self._inputs else 0
        return {i: str(i) for i in range(input_count)}

    def output_names(self) ->Dict[int, str]:
        output_count = max(self._outputs.keys()) + 1 if self._outputs else 0
        return {i: str(i) for i in range(output_count)}

    def input_data_types(self) ->Dict[int, str]:
        input_count = max(self._inputs.keys()) + 1 if self._inputs else 0
        return {i: 'any' for i in range(input_count)}

    def output_data_types(self) ->Dict[int, str]:
        output_count = max(self._outputs.keys()) + 1 if self._outputs else 0
        return {i: 'any' for i in range(output_count)}

    def network_item_type(self) ->NetworkItemType:
        """Implement the abstract method from NetworkEntity."""
        return NetworkItemType.NODE

    def isTimeDependent(self) ->bool:
        """Return whether the node is time dependent."""
        return self._is_time_dependent

    def cook_dependencies(self) ->List['Node']:
        """
        Gathers all input nodes that this node depends on into a list in the correct order (furthest nodes first).
        The actual cooking is deferred and should be handled later by the last node in the chain.
        Returns a list of nodes in the correct order they should be cooked.
        """
        nodes_to_cook: List[Node] = []
        visited_nodes: Set[Node] = set()

        def dfs(node: Node):
            if node in visited_nodes:
                return
            visited_nodes.add(node)
            for input_node in node.input_nodes():
                dfs(input_node)
            if node.needs_to_cook():
                nodes_to_cook.append(node)
        for input_node in self.input_nodes():
            dfs(input_node)
        return nodes_to_cook

    def cook(self, force: bool=False) ->None:
        """
        Public cook method which includes dependency handling and core cooking logic.
        This method should be called externally and will manage dependency cooking before
        executing the core logic of this node.
        """
        # Import at runtime to avoid circular dependency
        from core.parm import Parm, ParameterType

        # Ensure _parms exists and has "enabled" parameter
        if not hasattr(self, '_parms') or self._parms is None:
            self._parms = {}
        if "enabled" not in self._parms:
            self._parms["enabled"] = Parm("enabled", ParameterType.TOGGLE, self)
            self._parms["enabled"].set(True)

        # Check if node is disabled
        if not self._parms["enabled"].eval():
            # Cook dependencies first
            dependencies = self.cook_dependencies()
            for node in dependencies:
                node._internal_cook()

            # Pass through input unchanged or return empty
            if self.inputs():
                input_conn = self.inputs()[0]
                self._output = input_conn.output_node().get_output(requesting_node=self)
            else:
                self._output = []
            self.set_state(NodeState.UNCHANGED)
            return

        print(f'☀ Starting cook for {self.name()}')
        dependencies = self.cook_dependencies()
        for node in dependencies:
            # print(
            #     f'Cooking {node.name()} via _internal_cook() from {self.name()}'
            #     )
            node._internal_cook()
        self._internal_cook()

    def last_cook_time(self) ->float:
        """Returns the duration of the node’s last cook in milliseconds. Returns a 0 if the node cannot be cooked, doesn’t need to be cooked, is bypassed, or locked"""
        return self._last_cook_time

    def needs_to_cook(self) ->bool:
        """
        Determines if the node needs to be cooked.
        This method should be overridden by subclasses to implement specific logic.
        """
        return self._is_time_dependent or self.state() != NodeState.UNCHANGED

    def cook_count(self) ->int:
        """Returns the number of times this node has cooked in the current session."""
        return self._cook_count

    def _parse_string_list(self, s: str) -> list[str]:

        """
        Parses a text string as either a plain string or a Python-style list of strings.
        
        Supports:
        - Python list syntax: ["item1", "item2"]
        - Mixed quotes: ["item1", 'item2']
        - Escaped quotes: ["escaped\"quote"]
        - Empty strings: ["", "test", ""]
        - Empty lists: [] -> [""]
        
        Fallback behavior:
        - Invalid syntax (unclosed quotes, bad escapes) -> treats entire input as plain string
        - Unmatched brackets -> treats entire input as plain string
        - Plain string without brackets -> returns single-item list
        
        Args:
            s: Input string to parse
            
        Returns:
            list[str]: Parsed strings as list. Always returns at least a single item list.
        """  

        if not (s.startswith('[') and s.endswith(']')):
            return [s]
            
        result = []
        s = s[1:-1].strip()
        if not s:
            return ['']
            
        current = []
        in_string = False
        quote_char = None
        escape = False
        
        try:
            for c in s:
                if escape:
                    current.append(c)
                    escape = False
                    continue
                    
                if c == '\\':
                    escape = True
                    continue
                    
                if c in ['"', "'"]:
                    if not in_string:
                        in_string = True
                        quote_char = c
                    elif c == quote_char:
                        in_string = False
                        quote_char = None
                    else:
                        current.append(c)
                elif c == ',' and not in_string:
                    result.append(''.join(current))
                    current = []
                elif c.isspace() and not in_string:
                    continue
                else:
                    current.append(c)
                    
            if escape or in_string:  # Invalid syntax
                return [s]
                
            if current:
                result.append(''.join(current))
                
            return [x for x in result if x or x == '']  # Preserve empty strings
            
        except:
            return [s]

    def inputs_with_indices(self, use_names: bool=False) ->Sequence[Tuple[
        'Node', Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected input of this node.

        When use_names=False: returns (Node, int, int) - actual indices
        When use_names=True: returns (Node, str, str) - socket names
        """
        result = []
        for input_index, connection in self._inputs.items():
            output_node = connection.output_node()
            output_index = connection.output_index()
            if use_names:
                input_name = self.input_names().get(input_index, str(input_index))
                output_name = output_node.output_names().get(output_index,
                    str(output_index))
                result.append((output_node, output_name, input_name))
            else:
                result.append((output_node, output_index, input_index))
        return result

    def outputs_with_indices(self, use_names: bool=False) ->Sequence[Tuple[
        'Node', Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected output of this node.

        When use_names=False: returns (Node, int, int) - actual indices
        When use_names=True: returns (Node, str, str) - socket names
        """
        result = []
        for output_index, connections in self._outputs.items():
            for connection in connections:
                input_node = connection.input_node()
                input_index = connection.input_index()
                if use_names:
                    output_name = self.output_names().get(output_index,
                        str(output_index))
                    input_name = input_node.input_names().get(input_index,
                        str(input_index))
                    result.append((input_node, output_name, input_name))
                else:
                    result.append((input_node, output_index, input_index))
        return result

    def eval(self, force: bool = False, requesting_node: Optional['Node'] = None) -> Any:
        if self.state() != NodeState.UNCHANGED or force is True or self._is_time_dependent:
            self.cook()
        return self.get_output(requesting_node)

    def get_output(self, requesting_node: Optional['Node'] = None):
        if requesting_node and hasattr(self, 'SINGLE_OUTPUT') and not self.SINGLE_OUTPUT:
            for conns in self._outputs.values():
                for conn in conns:
                    if conn.input_node() == requesting_node:
                        if isinstance(self._output, list) and len(self._output) > conn.output_index():
                            return self._output[conn.output_index()]
        return self._output

    def __repr__(self) ->str:
        """Returns a string representation of the Node."""
        return (
            f"Node(name='{self.name()}', type={self._node_type}, path='{self.path()}')"
            )
