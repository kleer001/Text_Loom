from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Deque
from enum import Enum
from pathlib import PurePosixPath
from collections import deque
from weakref import WeakSet
from TUI.logging_config import get_logger
from core.base_classes import NodeEnvironment, Node, NodeConnection, NodeType, NodeState
from core.parm import Parm

"""
Undo System Implementation Guide:

Key Principles:
- Push state BEFORE changes occur (like a bookmark)
- Each undoable action pushes its own state
- Parent methods must disable undo for child methods that push state
- Always use try/finally when disabling undo to ensure it's re-enabled

Example Pattern:
    def parent_method():
        from core.undo_manager import UndoManager
        UndoManager().push_state("Parent operation")
        UndoManager().disable_undo()
        try:
            child_method()  # Has its own push_state
        finally:
            UndoManager().enable_undo()

    def child_method():
        UndoManager().push_state("Child operation")
        # make changes

To avoid circular imports:
    from core.undo_manager import UndoManager
    UndoManager().push_state("Operation name")


Stack Size: Limited to 100 operations. Arbitrary, but a starting point.
Eventually it should be limited by memory, not number
State Capture: Full network state including nodes, connections, parameters
Restoration: Two-phase process (clear all, then rebuild) to avoid state conflicts
"""

MAX_STACK_SIZE = 100

@dataclass
class ParmState:
    """Captures the state of a parameter including its type, value, and callback"""
    name: str
    parm_type: str
    value: Union[int, float, str, List[str], bool]
    script_callback: str

@dataclass
class NodeConnectionState:
    """Represents a connection between two nodes with input/output references"""
    output_node_path: str
    input_node_path: str
    output_index: int
    input_index: int
    output_ref: Optional[WeakSet]
    input_ref: Optional[WeakSet]

@dataclass
class FullNodeState:
    """Complete snapshot of a node's state including position, parameters, and connections"""
    name: str
    path: str
    position: List[float]
    node_type: str
    state: str
    errors: List[str]
    warnings: List[str]
    is_time_dependent: bool
    last_cook_time: float
    cook_count: int
    file_hash: Optional[str]
    param_hash: Optional[str]
    last_input_size: int
    internal_nodes_created: bool
    parent_looper: bool
    parms: Dict[str, ParmState]
    inputs: Dict[str, NodeConnectionState]
    outputs: Dict[str, List[NodeConnectionState]]

@dataclass
class GlobalStoreState:
    """Captures the state of the global store dictionary"""
    store: Dict[str, Any]

@dataclass
class NetworkState:
    """Complete network state including all nodes and global store data"""
    nodes: Dict[str, FullNodeState]
    global_store: GlobalStoreState
    restore_order: List[str]

class UndoManager:
    """Singleton manager handling undo/redo operations for the node network.
    
    Maintains stacks of network states and provides methods to capture, restore,
    and manage the history of network operations. Uses a singleton pattern to 
    ensure consistent state management across the application.
    """
    _instance: Optional['UndoManager'] = None
    _initialized: bool = False
    _undo_active: bool = True  # Class level variable

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UndoManager, cls).__new__(cls)
            cls._instance.logger = get_logger('undo', level=1)
            cls._instance._undo_active = True
            cls._initialized = False
        return cls._instance

    def __init__(self):
        if not UndoManager._initialized:
            self.undo_stack: Deque[Tuple[str, NetworkState]] = deque(maxlen=MAX_STACK_SIZE)
            self.redo_stack: Deque[Tuple[str, NetworkState]] = deque(maxlen=MAX_STACK_SIZE)
            self._restoring: bool = False
            self._current_operation: Optional[str] = None
            self._node_paths_restored: Set[str] = set()
            self.logger.info("Initializing UndoManager")
            UndoManager._initialized = True

    @property
    def undo_active(self) -> bool:
        return self._undo_active

    @undo_active.setter 
    def undo_active(self, value: bool) -> None:
        self.logger.info(f"Setting undo_active to {value}")
        self._undo_active = value

    def capture_network_state(self) -> NetworkState:
        from core.global_store import GlobalStore
        
        """Captures the complete current state of the network including all nodes and global store.
        Returns a NetworkState object containing all node states, connections, and global variables.
        """

        self.logger.debug("Capturing network state")
        node_order = []
        captured_nodes = {}
        
        all_nodes = NodeEnvironment.list_nodes()
        self.logger.debug(f"Nodes found in environment: {all_nodes}")
        
        for node_path in all_nodes:
            node = NodeEnvironment.node_from_name(node_path)
            if not node:
                self.logger.debug(f"Skipping non-existent node: {node_path}")
                continue
            
            self.logger.debug(f"Capturing state for node: {node_path}")
            node_order.append(node_path)
            captured_nodes[node_path] = self._capture_node_state(node)
            
        self.logger.debug(f"Captured nodes: {list(captured_nodes.keys())}")
        self.logger.debug(f"Node order: {node_order}")
        
        network_state = NetworkState(
            nodes=captured_nodes,
            global_store=GlobalStoreState(dict(GlobalStore.list())),
            restore_order=node_order
        )
        self.logger.debug(f"Final network state nodes: {list(network_state.nodes.keys())}")
        return network_state

    def _capture_node_state(self, node: 'Node') -> FullNodeState:

        """
        Creates a comprehensive snapshot of a single node's current state.
        Includes parameters, connections, position, and internal state variables.
        Returns a FullNodeState object.
        """

        parms = {}
        if hasattr(node, '_parms'):
            for parm_name, parm in node._parms.items():
                if str(parm.type()) == 'ParameterType.BUTTON':
                    continue
                parms[parm_name] = ParmState(
                    name=parm.name(),
                    parm_type=str(parm.type()),
                    value=parm.raw_value(),
                    script_callback=parm.script_callback()
                )

        inputs = {}
        for idx, conn in node._inputs.items():
            inputs[str(idx)] = self._capture_connection_state(conn)

        outputs = {}
        for idx, conns in node._outputs.items():
            outputs[str(idx)] = [self._capture_connection_state(c) for c in conns]

        return FullNodeState(
            name=node.name(),
            path=node.path(),
            position=node._position,
            node_type=str(node.type()),
            state=node._state,
            errors=node._errors.copy(),
            warnings=node._warnings.copy(),
            is_time_dependent=node._is_time_dependent,
            last_cook_time=node._last_cook_time,
            cook_count=node._cook_count,
            file_hash=node._file_hash,
            param_hash=node._param_hash,
            last_input_size=node._last_input_size,
            internal_nodes_created=node._internal_nodes_created,
            parent_looper=node._parent_looper,
            parms=parms,
            inputs=inputs,
            outputs=outputs
        )

    def _capture_connection_state(self, conn: 'NodeConnection') -> NodeConnectionState:
        self.logger.debug(f"Capturing connection from {conn.output_node().path()} to {conn.input_node().path()}")
        return NodeConnectionState(
            output_node_path=conn.output_node().path(),
            input_node_path=conn.input_node().path(),
            output_index=conn.output_index(),
            input_index=conn.input_index(),
            output_ref=None,
            input_ref=None
        )
    
    def restore_network_state(self, state: NetworkState) -> None:

        """
        Two-phase restoration of a previously captured network state.
        First removes nodes not present in target state, then rebuilds network
        from stored state including all connections and parameters.
        """


        if self._restoring:
            self.logger.debug("Already restoring state, skipping")
            return

        self.logger.info("Starting network state restoration")
        self._restoring = True
        self._node_paths_restored.clear()
        
        try:
            # First, remove nodes that shouldn't exist in this state
            current_nodes = set(NodeEnvironment.list_nodes())
            target_nodes = set(state.nodes.keys())
            nodes_to_remove = current_nodes - target_nodes
            
            self.logger.debug(f"Removing nodes not in target state: {nodes_to_remove}")
            for node_path in nodes_to_remove:
                NodeEnvironment.remove_node(node_path)  # Changed: pass the path directly
            
            self._restore_global_store(state.global_store)
            
            for node_path in state.restore_order:
                if node_path not in self._node_paths_restored:
                    self._restore_node(state.nodes[node_path])
            
            self._restore_connections(state)
            self.logger.info("Network state restoration completed")
            
        except Exception as e:
            self.logger.error(f"Error during state restoration: {str(e)}")
            raise
        finally:
            self._restoring = False
            self._node_paths_restored.clear()
            
    def _restore_global_store(self, state: GlobalStoreState) -> None:
        from core.global_store import GlobalStore
        self.logger.debug("Restoring global store")
        GlobalStore.flush_all_globals()
        for key, value in state.store.items():
            GlobalStore.set(key, value)

    def _restore_node(self, state: FullNodeState) -> None:
        if state.path in self._node_paths_restored:
            return
        self.logger.debug(f"Restoring node: {state.path}")
        node = NodeEnvironment.node_from_name(state.path)
        if not node:
            node_type_str = state.node_type.split('.')[-1] if '.' in state.node_type else state.node_type
            node = Node.create_node(
                NodeType[node_type_str],
                state.name,
                str(PurePosixPath(state.path).parent)
            )

        node._position = state.position
        node._state = NodeState(state.state)
        node._errors = state.errors
        node._warnings = state.warnings
        node._is_time_dependent = state.is_time_dependent
        node._last_cook_time = state.last_cook_time
        node._cook_count = state.cook_count
        node._file_hash = state.file_hash
        node._param_hash = state.param_hash
        node._last_input_size = state.last_input_size
        node._internal_nodes_created = state.internal_nodes_created
        node._parent_looper = state.parent_looper
        if hasattr(node, '_parms'):
            for parm_name, parm_state in state.parms.items():
                parm = node._parms.get(parm_name)
                if parm and str(parm.type()) != 'ParameterType.BUTTON':
                    parm.set(parm_state.value)
                    parm.set_script_callback(parm_state.script_callback)
        self._node_paths_restored.add(state.path)

    def _restore_connections(self, state: NetworkState) -> None:

        """
        Reconstructs all node connections from a stored network state.
        Handles clearing existing connections and rebuilding them based on
        stored input/output relationships.
        """


        self.logger.debug("Starting connection restoration")
        try:
            for node_path, node_state in state.nodes.items():
                node = NodeEnvironment.node_from_name(node_path)
                if not node:
                    self.logger.error(f"Missing node {node_path} during connection restore")
                    continue
                    
                self.logger.debug(f"Clearing existing connections for node {node_path}")
                node._inputs.clear()
                node._outputs.clear()

            for node_path, node_state in state.nodes.items():
                node = NodeEnvironment.node_from_name(node_path)
                if not node:
                    continue
                    
                self.logger.debug(f"Restoring connections for node {node_path}")
                self._restore_node_connections(node, node_state)
                
        except Exception as e:
            self.logger.error(f"Error during connection restoration: {str(e)}", exc_info=True)
            raise

    def _restore_node_connections(self, node: 'Node', state: FullNodeState) -> None:
        self.logger.debug(f"Processing inputs for node {node.path()}")
        for idx_str, conn_state in state.inputs.items():
            idx = int(idx_str)
            output_node = NodeEnvironment.node_from_name(conn_state.output_node_path)
            if not output_node:
                self.logger.warning(f"Missing output node {conn_state.output_node_path} for connection to {node.path()}")
                continue
                
            self.logger.debug(f"Setting input {idx} from {output_node.path()}[{conn_state.output_index}] to {node.path()}")
            node.set_input(idx, output_node, conn_state.output_index)
            
        self.logger.debug(f"Processing outputs for node {node.path()}")
        for idx_str, conn_states in state.outputs.items():
            idx = int(idx_str)
            for conn_state in conn_states:
                input_node = NodeEnvironment.node_from_name(conn_state.input_node_path)
                if not input_node:
                    self.logger.warning(f"Missing input node {conn_state.input_node_path} for connection from {node.path()}")
                    continue
                    
                if not any(c.output_node() == node for c in input_node._inputs.values()):
                    self.logger.debug(f"Setting input {conn_state.input_index} from {node.path()}[{idx}] to {input_node.path()}")
                    input_node.set_input(conn_state.input_index, node, idx)


    def _validate_connection_refs(self, state: NodeConnectionState) -> bool:
        return (state.output_ref and state.input_ref and
                bool(state.output_ref) and bool(state.input_ref))

    def _recreate_connection(self, state: NodeConnectionState) -> None:
        output_node = next(iter(state.output_ref))
        input_node = next(iter(state.input_ref))
        input_node.set_input(state.input_index, output_node, state.output_index)

    def push_state(self, operation_name: str = "") -> None:
        if not self._restoring and self.undo_active:
            self.logger.info(f"Pushing new state: {operation_name}")
            current_state = self.capture_network_state()
            self.undo_stack.append((operation_name, current_state))
            self.redo_stack.clear()
    
    def disable(self) -> None:
        self.logger.debug("Disabling undo system")
        self._undo_active = False
        
    def enable(self) -> None:
        self.logger.debug("Enabling undo system")
        self._undo_active = True

    def undo(self) -> Optional[str]:
        if not self.undo_stack:
            self.logger.debug("No states to undo")
            return None
        
        self.disable()
        try:
            operation_name, previous_state = self.undo_stack.pop()
            self.logger.info(f"Undoing operation: {operation_name}")
            current_state = self.capture_network_state()
            self.redo_stack.append((operation_name, current_state))
            self.restore_network_state(previous_state)
            return operation_name
        finally:
            self.enable()

    def redo(self) -> Optional[str]:
        if not self.redo_stack:
            self.logger.debug("No states to redo")
            return None
            
        self.disable()
        try:
            operation_name, next_state = self.redo_stack.pop()
            self.logger.info(f"Redoing operation: {operation_name}")
            current_state = self.capture_network_state()
            self.undo_stack.append((operation_name, current_state))
            self.restore_network_state(next_state)
            return operation_name
        finally:
            self.enable()
    
    def get_undo_text(self) -> str:
        if not self.undo_stack:
            return "Nothing to undo"
        return "\n".join(f"{i+1}: {action}" for i, (action, _) in enumerate(reversed(self.undo_stack)))

    def get_redo_text(self) -> str:
        if not self.redo_stack:
            return "Nothing to redo"
        return "\n".join(f"{i+1}: {action}" for i, (action, _) in enumerate(reversed(self.redo_stack)))
    
    def flush_all_undos(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.logger.info("Cleared all undo and redo stacks")