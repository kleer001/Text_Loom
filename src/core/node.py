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

class Node(MobileItem):
    """
    Represents a Node in the workspace, inheriting from MobileItem.
    This class implements the Composite pattern, allowing for a hierarchical structure of nodes.
    It also implements the Observer pattern for NodeConnections.
    """

    def __init__(self, name: str, path: str, position: List[float],
        node_type: NodeType):
        super().__init__(name, path, position)
        self._node_type: NodeType = node_type
        self._children: List['Node'] = []
        self._depth = self._calculate_depth()
        self._inputs: Dict[str, NodeConnection] = {}
        self._outputs: Dict[str, List[NodeConnection]] = {}
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
            new_node._session_id = new_node._generate_unique_session_id()
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
        print('New Connection: from input ', self.name(), ' to output: ',
            input_node.name())
        self._inputs[input_index] = connection
        input_node._outputs.setdefault(output_index, []).append(connection)

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

    def remove_input(self, input_index: str) ->None:
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
        if connection.input_node() == self:
            input_idx = connection.input_index()
            if input_idx in self._inputs and self._inputs[input_idx
                ] == connection:
                del self._inputs[input_idx]
        if connection.output_node() == self:
            output_idx = connection.output_index()
            if output_idx in self._outputs:
                if connection in self._outputs[output_idx]:
                    self._outputs[output_idx].remove(connection)

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

    def input_names(self) ->Dict[str, str]:
        input_count = max(self._inputs.keys()) + 1 if self._inputs else 0
        return {str(i): str(i) for i in range(input_count)}

    def output_names(self) ->Dict[str, str]:
        output_count = max(self._outputs.keys()) + 1 if self._outputs else 0
        return {str(i): str(i) for i in range(output_count)}

    def input_data_types(self) ->Dict[str, str]:
        input_count = max(self._inputs.keys()) + 1 if self._inputs else 0
        return {str(i): 'any' for i in range(input_count)}

    def output_data_types(self) ->Dict[str, str]:
        output_count = max(self._outputs.keys()) + 1 if self._outputs else 0
        return {str(i): 'any' for i in range(output_count)}

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

    def inputs_with_indices(self, use_names: bool=False) ->Sequence[Tuple[
        'Node', Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected input of this node."""
        result = []
        for input_index, connection in self._inputs.items():
            output_node = connection.output_node()
            output_index = connection.output_index()
            if use_names:
                input_name = self.input_names().get(input_index, input_index)
                output_name = output_node.output_names().get(output_index,
                    output_index)
                result.append((output_node, output_name, input_name))
            else:
                result.append((output_node, output_index, input_index))
        return result

    def outputs_with_indices(self, use_names: bool=False) ->Sequence[Tuple[
        'Node', Union[int, str], Union[int, str]]]:
        """Returns a sequence of tuples representing each connected output of this node."""
        result = []
        for output_index, connections in self._outputs.items():
            for connection in connections:
                input_node = connection.input_node()
                input_index = connection.input_index()
                if use_names:
                    output_name = self.output_names().get(output_index,
                        output_index)
                    input_name = input_node.input_names().get(input_index,
                        input_index)
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
