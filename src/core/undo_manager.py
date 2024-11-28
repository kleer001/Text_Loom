from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Deque
from enum import Enum
from pathlib import PurePosixPath
from collections import deque
from weakref import WeakSet
from TUI.logging_config import get_logger
from core.base_classes import NodeEnvironment, Node, NodeConnection, NodeType, NodeState
from core.parm import Parm

MAX_STACK_SIZE = 100

@dataclass
class ParmState:
    name: str
    parm_type: str
    value: Union[int, float, str, List[str], bool]
    script_callback: str

@dataclass
class NodeConnectionState:
    output_node_path: str
    input_node_path: str
    output_index: int
    input_index: int
    output_ref: Optional[WeakSet]
    input_ref: Optional[WeakSet]

@dataclass
class NodeState:
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
    store: Dict[str, Any]

@dataclass
class NetworkState:
    nodes: Dict[str, NodeState]
    global_store: GlobalStoreState
    restore_order: List[str]

class UndoManager:
    _instance: Optional['UndoManager'] = None
    _initialized: bool = False
    _undo_active: bool = True  # Class level variable

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UndoManager, cls).__new__(cls)
            cls._instance.logger = get_logger('undo')
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
        
        self.logger.debug("Capturing network state")
        node_order = []
        captured_nodes = {}
        
        for node_path in NodeEnvironment.list_nodes():
            node = NodeEnvironment.node_from_name(node_path)
            if not node:
                self.logger.debug(f"Skipping non-existent node: {node_path}")
                continue

            node_order.append(node_path)
            captured_nodes[node_path] = self._capture_node_state(node)

        return NetworkState(
            nodes=captured_nodes,
            global_store=GlobalStoreState(dict(GlobalStore.list())),
            restore_order=node_order
        )

    def _capture_node_state(self, node: 'Node') -> NodeState:
        parms = {}
        for parm_name, parm in node._parms.items():
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

        return NodeState(
            name=node.name(),
            path=node.path(),
            position=node._position,
            node_type=str(node.type()),
            state=str(node._state),
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
        return NodeConnectionState(
            output_node_path=conn.output_node().path(),
            input_node_path=conn.input_node().path(),
            output_index=conn.output_index(),
            input_index=conn.input_index(),
            output_ref=WeakSet([conn.output_node()]),
            input_ref=WeakSet([conn.input_node()])
        )

    def restore_network_state(self, state: NetworkState) -> None:
        if self._restoring:
            self.logger.debug("Already restoring state, skipping")
            return

        self.logger.info("Starting network state restoration")
        self._restoring = True
        self._node_paths_restored.clear()
        
        try:
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

    def _restore_node(self, state: NodeState) -> None:
        if state.path in self._node_paths_restored:
            return

        self.logger.debug(f"Restoring node: {state.path}")
        node = NodeEnvironment.node_from_name(state.path)
        if not node:
            node = Node.create_node(
                NodeType[state.node_type],
                state.name,
                str(PurePosixPath(state.path).parent)
            )

        node._position = state.position
        node._state = state.state
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

        for parm_name, parm_state in state.parms.items():
            parm = node._parms.get(parm_name)
            if parm:
                parm.set(parm_state.value)
                parm.set_script_callback(parm_state.script_callback)

        self._node_paths_restored.add(state.path)

    def _restore_connections(self, state: NetworkState) -> None:
        try:
            for node_state in state.nodes.values():
                node = NodeEnvironment.node_from_name(node_state.path)
                if not node:
                    raise ValueError(f"Missing node {node_state.path} during connection restore")
                self._restore_node_connections(node, node_state)
        except Exception as e:
            self.logger.error("Corrupt network state detected during connection restoration")
            raise

    def _restore_node_connections(self, node: 'Node', state: NodeState) -> None:
        node._inputs.clear()
        node._outputs.clear()

        for idx_str, conn_state in state.inputs.items():
            idx = int(idx_str)
            if self._validate_connection_refs(conn_state):
                self._recreate_connection(conn_state)
            else:
                output_node = NodeEnvironment.node_from_name(conn_state.output_node_path)
                if output_node:
                    node.set_input(idx, output_node, conn_state.output_index)

        for idx_str, conn_states in state.outputs.items():
            idx = int(idx_str)
            for conn_state in conn_states:
                if not self._validate_connection_refs(conn_state):
                    input_node = NodeEnvironment.node_from_name(conn_state.input_node_path)
                    if input_node:
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
    
    def undo(self) -> Optional[str]:
        if not self.undo_stack:
            self.logger.debug("No states to undo")
            return None
        
        operation_name, previous_state = self.undo_stack.pop()
        self.logger.info(f"Undoing operation: {operation_name}")
        current_state = self.capture_network_state()
        self.redo_stack.append((operation_name, current_state))
        self.restore_network_state(previous_state)
        return operation_name

    def redo(self) -> Optional[str]:
        if not self.redo_stack:
            self.logger.debug("No states to redo")
            return None
            
        operation_name, next_state = self.redo_stack.pop()
        self.logger.info(f"Redoing operation: {operation_name}")
        current_state = self.capture_network_state()
        self.undo_stack.append((operation_name, current_state))
        self.restore_network_state(next_state)
        return operation_name
    
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