from typing import Optional, List, Callable
from dataclasses import dataclass
from textual.widgets import Static, OptionList, Input
from textual.keys    import Keys
from textual.binding import Binding
from textual.containers import ScrollableContainer, Vertical
from textual.screen import ModalScreen, Screen
from textual.message import Message
from textual.geometry import Region, Size
from textual.timer import Timer
from rich.text import Text
from rich.style import Style

import os
import time
from collections import namedtuple
from enum import Enum, auto

from TUI.parameter_window import ParameterChanged
from core.base_classes import NodeEnvironment, NodeState, generate_node_types, Node, NodeType
from core.flowstate_manager import load_flowstate
from TUI.network_visualizer import layout_network, render_layout, LayoutEntry
from TUI.logging_config import get_logger
from TUI.messages import (NodeAdded, NodeDeleted, ConnectionAdded, 
ConnectionDeleted, NodeSelected, NodeTypeSelected, OutputMessage, FileLoaded)
from TUI.node_support_modals import NodeTypeSelector, DeleteConfirmation, RenameInput, NodeMoveDestinationSelected, NodeMoveSelector
from TUI.node_type_emojis import get_node_emoji, NODE_TYPE_EMOJIS

logger = get_logger('node')

Point = namedtuple('Point', ['x', 'y'])

@dataclass
class NodeData:
    name: str
    path: str
    line_number: int
    indent_level: int


class NodeContent(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_line = 0

class ConnectionMode(Enum):
    NONE = auto()
    INPUT = auto()
    OUTPUT = auto()
    DELETE = auto()

class NodeWindow(ScrollableContainer):
    BRAILLE_SEQUENCE = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    ANIMATION_FRAME_TIME = .1  
    DEFAULT_CSS = """
        NodeWindow {
            width: 100%;
            height: 100%;
            background: $background;
            border: solid $secondary;
            
        }

        NodeWindow:focus {
            border: double $secondary;
        }

        NodeContent {
            width: 100%;
            padding: 0 1;
        }
        """

    BINDINGS = [
        Binding("up", "move_cursor_up", "Move Up"),
        Binding("down", "move_cursor_down", "Move Down"),
        Binding("enter", "select_or_connect_node", "Select/Connect Node"),
        Binding("p", "select_node", "Select Node Parameters"),
        Binding("space", "toggle_node", "Expand/Collapse Node"),
        Binding("a", "add_node", "Add Node"),
        Binding("d", "delete_node", "Delete Node"),
        Binding("r", "rename_node", "Rename Node"),
        Binding("i", "start_input_connection", "Input Connection"),
        Binding("o", "start_output_connection", "Output Connection"),
        Binding("x", "start_delete_connection", "Delete Connection"),
        Binding("m", "move_node", "Change Node Path"),
        Binding("e", "get_output", "Get Node Output"),
        Binding("escape", "cancel_connection", "Cancel Connection"),
        Binding("C", "cook_node", "Cook Node"),
    ]

    def _get_state_indicator(self, node_state: NodeState, node_path: str) -> str:
        if self._cooking_node == node_path:
            return self.BRAILLE_SEQUENCE[self._animation_frame]

        if self._connection_mode != ConnectionMode.NONE and self._source_node:
            if self._connection_mode == ConnectionMode.DELETE:
                source_node = self._env.node_from_name(self._source_node.path())
                if source_node and hasattr(source_node, '_inputs'):
                    for conn in source_node._inputs.values():
                        if conn.output_node().path() == node_path:
                            return "←"
            elif self._source_node.path() == node_path:
                return "↓" if self._connection_mode == ConnectionMode.INPUT else "↑"
                
        return {
            NodeState.COOKED: "◆",
            NodeState.COOKING: "◇",
            NodeState.UNCOOKED: "▪",
            NodeState.UNCHANGED: "▫",
        }[node_state]
    
    def __init__(self) -> None:
        super().__init__()
        self._node_data: List[NodeData] = []
        self._selected_line: int = 0
        self._env: Optional[NodeEnvironment] = None
        self._initialized: bool = False
        self.content = NodeContent()
        self._rename_input: Optional[RenameInput] = None
        self._node_position: Optional[Point] = None
        self._connection_mode = ConnectionMode.NONE
        self._source_node: Optional[Node] = None
        self._cooking: bool = False
        self._cooking_node: Optional[str] = None
        self._refresh_timer: Optional[Timer] = None
        self._animation_frame: int = 0
        self._last_frame_time: float = 0

    can_focus = True

    def on_parameter_changed(self, message: ParameterChanged) -> None:
            try:
                node = self._env.node_from_name(message.node_path)
                if node:
                    self._refresh_layout()
                    logger.info(f"Refreshed network after parameter change: {message.param_name}={message.new_value}")
            except Exception as e:
                logger.error(f"Error handling parameter change: {str(e)}", exc_info=True)

    def action_get_output(self) -> None:
        if not self._initialized or self._selected_line >= len(self._node_data):
            logger.debug("Not initialized or invalid line selected")
            return
            
        try:
            node_data = self._node_data[self._selected_line]
            node = self._env.node_from_name(node_data.path)
            if node:
                logger.debug(f"Getting output from node: {node_data.path}")
                output_data = node.get_output()
                
                if output_data is None:
                    logger.debug("Node returned None output")
                    self.parent.post_message(OutputMessage([f"NO OUTPUT FROM NODE {node.name()}"]))
                    return
                    
                if not isinstance(output_data, list):
                    output_data = [str(output_data)]
                    
                logger.debug(f"Posted output message with {len(output_data)} lines: {output_data}")
                self.parent.post_message(OutputMessage(output_data))
                
        except Exception as e:
            logger.error(f"Error getting node output: {str(e)}", exc_info=True)

    def action_start_input_connection(self) -> None:
        if not self._initialized or self._selected_line >= len(self._node_data):
            return
            
        if self._connection_mode == ConnectionMode.NONE:
            node_data = self._node_data[self._selected_line]
            source_node = self._env.node_from_name(node_data.path)
            if source_node:
                self._connection_mode = ConnectionMode.INPUT
                self._source_node = source_node
                logger.debug(f"Started input connection from {source_node.path()}")
                self._refresh_layout()

    def action_start_output_connection(self) -> None:
        if not self._initialized or self._selected_line >= len(self._node_data):
            return
            
        if self._connection_mode == ConnectionMode.NONE:
            node_data = self._node_data[self._selected_line]
            source_node = self._env.node_from_name(node_data.path)
            if source_node:
                self._connection_mode = ConnectionMode.OUTPUT
                self._source_node = source_node
                logger.debug(f"Started output connection from {source_node.path()}")
                self._refresh_layout()

    def action_complete_connection(self) -> None:
        if not self._initialized or not self._source_node:
            return

        try:
            target_data = self._node_data[self._selected_line]
            target_node = self._env.node_from_name(target_data.path)
            
            if target_node:
                if self._connection_mode == ConnectionMode.INPUT:
                    target_node.set_next_input(self._source_node)
                    logger.info(f"Connected input of {target_node.path()} to output of {self._source_node.path()}")
                    self.post_message(ConnectionAdded(self._source_node.path(), target_node.path()))
                else:  # OUTPUT mode
                    self._source_node.set_next_input(target_node)
                    logger.info(f"Connected input of {self._source_node.path()} to output of {target_node.path()}")
                    self.post_message(ConnectionAdded(target_node.path(), self._source_node.path()))
                    
        except Exception as e:
            logger.error(f"Error creating connection: {str(e)}", exc_info=True)
            
        finally:
            self._connection_mode = ConnectionMode.NONE
            self._source_node = None
            self._refresh_layout()

    def action_cancel_connection(self) -> None:
        if self._connection_mode != ConnectionMode.NONE:
            self._connection_mode = ConnectionMode.NONE
            self._source_node = None
            logger.debug("Cancelled connection")
            self._refresh_layout()

    def action_select_or_connect_node(self) -> None:
        if self._connection_mode == ConnectionMode.DELETE:
            self.action_delete_connection()
        elif self._connection_mode != ConnectionMode.NONE:
            self.action_complete_connection()
        else:
            self.action_select_node()


    def _get_deletable_connections(self, node) -> list:
        if not hasattr(node, '_inputs'):
            return []
        return [(idx, conn.output_node()) for idx, conn in node._inputs.items()]

    def action_start_delete_connection(self) -> None:
        if not self._initialized or self._selected_line >= len(self._node_data):
            logger.debug("Delete connection attempted but not initialized or invalid line")
            return
            
        node_data = self._node_data[self._selected_line]
        target_node = self._env.node_from_name(node_data.path)
        
        if not target_node or not target_node.inputs():
            logger.debug(f"No connections available to delete for node: {node_data.path}")
            return
            
        self._connection_mode = ConnectionMode.DELETE
        self._source_node = target_node
        
        valid_lines = self._get_valid_lines_for_delete_mode()
        if valid_lines:
            self._selected_line = valid_lines[0]
            
        logger.info(f"Entered delete connection mode for node: {node_data.path}")
        self._refresh_layout()
        self._ensure_line_visible(self._selected_line)

    def action_delete_connection(self) -> None:
        if not self._initialized or not self._source_node:
            return

        try:
            target_data = self._node_data[self._selected_line]
            source_node = self._source_node
            target_node = self._env.node_from_name(target_data.path)
            
            if not target_node:
                return
                
            # Find input index where target_node is connected to source_node
            for input_idx, conn in source_node._inputs.items():
                if conn.output_node() == target_node:
                    source_node.remove_input(input_idx)
                    logger.info(f"Deleted connection from {target_data.path} to {source_node.path()}")
                    self.post_message(ConnectionDeleted(target_data.path, source_node.path()))
                    break
                    
            self._connection_mode = ConnectionMode.NONE
            self._source_node = None
            self._refresh_layout()
            
        except Exception as e:
            logger.error(f"Error deleting connection: {str(e)}", exc_info=True)
            self._connection_mode = ConnectionMode.NONE
            self._source_node = None
            self._refresh_layout()
                
    def on_node_type_selected(self, message: NodeTypeSelected) -> None:
        logger.debug(f"NodeWindow received NodeTypeSelected message: {message.node_type}")
        self._create_new_node(message.node_type)

    def _create_new_node(self, node_type_str: str) -> None:
        logger.debug(f"_create_new_node called with node_type_str: {node_type_str}")
        try:
            reference_path = "/"
            if 0 <= self._selected_line < len(self._node_data):
                reference_path = os.path.dirname(self._node_data[self._selected_line].path)
            
            logger.debug(f"Creating node of type {node_type_str} with parent path {reference_path}")
            node_type = getattr(NodeType, node_type_str)
            new_node = Node.create_node(node_type, parent_path=reference_path)
            
            if new_node:
                logger.debug(f"Suessfully created node: {new_node.path()}")
                self.post_message(NodeAdded(new_node.path(), node_type_str))
                self._refresh_layout()
                for i, node_data in enumerate(self._node_data):
                    if node_data.path == new_node.path():
                        self._selected_line = i
                        self._ensure_line_visible(i)
                        break
            else:
                logger.error("Node creation failed: create_node returned None")
        except Exception as e:
            logger.error(f"Failed to create node: {str(e)}", exc_info=True)

    def action_add_node(self) -> None:
        if not self._initialized or not self._env:
            logger.debug("Add node called but environment not initialized")
            return
        logger.debug("Showing node type selector")
        self.app.push_screen(NodeTypeSelector())

    def action_delete_node(self) -> None:
        if not self._initialized or self._selected_line >= len(self._node_data):
            return

        node_data = self._node_data[self._selected_line]
        logger.debug(f"Delete requested for node: {node_data.path}")
        
        def delete_node(confirmed: bool):
            if confirmed:
                try:
                    node = self._env.node_from_name(node_data.path)
                    if node:
                        node.destroy()
                        logger.info(f"Deleted node: {node_data.path}")
                        
                        # Get parameter window reference
                        main_content = self.app.query_one("MainContent")
                        param_window = main_content.query_one("ParameterWindow")
                        
                        # Create message once
                        delete_msg = NodeDeleted(node_data.path)
                        
                        # Post to both parameter window and app
                        if param_window:
                            logger.debug("Posting NodeDeleted to parameter window")
                            param_window.post_message(delete_msg)
                        
                        logger.debug("Posting NodeDeleted to app")
                        self.app.post_message(delete_msg)
                        
                        self._refresh_layout()
                except Exception as e:
                    logger.error(f"Error deleting node: {str(e)}", exc_info=True)
                    
        self.app.push_screen(DeleteConfirmation(node_data.name), delete_node)


    def action_rename_node(self) -> None:
        try:
            logger.info("Beginning rename action")
            
            if not self._initialized or self._selected_line >= len(self._node_data):
                return

            node_data = self._node_data[self._selected_line]
            
            try:
                indent_level = int(node_data.indent_level) if node_data.indent_level else 0
            except ValueError:
                indent_level = 0
                
            indent_offset = indent_level + 2
            relative_y = self._selected_line - len(self._node_data) - 2
            
            self._rename_input = RenameInput(node_data.path)
            self.mount(self._rename_input)
            
            self._rename_input.styles.width = self.content.size.width - indent_offset
            self._rename_input.styles.height = 3
            self._rename_input.styles.offset = (indent_offset, relative_y)
            self._rename_input.value = node_data.name
            self._rename_input.focus()
            
        except Exception as e:
            logger.error(f"Error in rename action: {str(e)}", exc_info=True)

    def action_move_node(self) -> None:
            if not self._initialized or self._selected_line >= len(self._node_data):
                return
            
            node_data = self._node_data[self._selected_line]
            self.app.push_screen(NodeMoveSelector(node_data.path))
            
    def on_node_move_destination_selected(self, message: NodeMoveDestinationSelected) -> None:
            if not self._initialized or self._selected_line >= len(self._node_data):
                return
                
            try:
                node_data = self._node_data[self._selected_line]
                node = self._env.node_from_name(node_data.path)
                if node:
                    node.set_parent(message.destination_path)
                    self._refresh_layout()
            except Exception as e:
                logger.error(f"Error moving node: {str(e)}", exc_info=True)

    def compose(self):
        yield self.content

    def on_mount(self) -> None:
        logger.debug("NodeWindow mounted")
        self._init_empty_network() #uncomment for forced load
        self.border_title = "[b]N[/]ode Network"

    def _init_empty_network(self) -> None: 
        logger.debug("Initializing empty network")
        try:        
            self._env = NodeEnvironment.get_instance()
            self._initialized = True
            logger.info("Successfully initialized NodeEnvironment")
            self._refresh_layout()

        except Exception as e:
            error_msg = f"Failed to initialize network: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.content.update(f"[red]{error_msg}")

    def _initialize_network(self) -> None:
        from core.undo_manager import UndoManager
        logger.debug("Initializing network")
        try:
            file_path = os.path.abspath("save_file_2.json")
            logger.info(f"Loading flowstate from {file_path}")
            
            if not os.path.exists(file_path):
                error_msg = f"Save file not found: {file_path}"
                logger.error(error_msg)
                self.content.update(f"[red]{error_msg}")
                return

            UndoManager().flush_all_undos()
            UndoManager().undo_active = False
            load_flowstate(file_path)
            UndoManager().undo_active = True        
            self._env = NodeEnvironment.get_instance()
            self._initialized = True
            logger.info("Successfully initialized NodeEnvironment")
            self._refresh_layout()

        except Exception as e:
            error_msg = f"Failed to initialize network: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.content.update(f"[red]{error_msg}")

    def _refresh_layout(self) -> None:
        if not self._initialized or not self._env:
            return

        try:
            # Get colors from theme
            css_vars = self.app.get_css_variables()
            
            # Define our segment styles using the theme colors
            NODE_STYLE = f" {css_vars['text']}"              
            ARROW_STYLE = f"bold {css_vars['text-secondary']}"            
            INPUT_STYLE = f"italic {css_vars['primary-muted']}"          
            OUTPUT_STYLE = f"bold {css_vars['primary']}"       

            self._env = NodeEnvironment.get_instance()
            layout_entries = layout_network(self._env)
            self._node_data = []
            rendered_text = Text()

            def format_node(node: Node, indent: int) -> tuple[str, str]:
                state_indicator = self._get_state_indicator(node.state(), node.path())
                type_indicator = get_node_emoji(node.type().name)
                
                i = len(self._node_data)
                self._node_data.append(NodeData(
                    name=node.name(),
                    path=node.path(),
                    line_number=i,
                    indent_level=indent
                ))
                
                self._current_line = i
                
                style = []
                if i == self._selected_line:
                    style.append("reverse")
                if node.path() == self._cooking_node:
                    style.append("underline")
                
                return f"{state_indicator}{type_indicator} {node.name()}", " ".join(style) if style else ""

            rendered_lines = render_layout(layout_entries, format_node)
            
            for line_info in rendered_lines:
                segments = []
                node = line_info['node']
                node_text, style = format_node(node, line_info['indent'])
                
                # Add segments with appropriate styling
                segments.append((line_info['indent'], ""))
                segments.append((node_text, style))  # Node name with potential reverse highlight

                if line_info['output_nodes']:
                    segments.append((" > (", ARROW_STYLE))  # Arrow
                    output_names = [n.name() for n in line_info['output_nodes']]
                    segments.append((", ".join(output_names), OUTPUT_STYLE))  # Output nodes
                    segments.append((")", ARROW_STYLE))

                if line_info['input_nodes']:
                    segments.append((" < ", ARROW_STYLE))  # Arrow
                    input_names = [n.name() for n in line_info['input_nodes']]
                    segments.append((", ".join(input_names), INPUT_STYLE))  # Input nodes
                

                # Add all segments to rendered text
                for text, segment_style in segments:
                    rendered_text.append(text, style=segment_style)
                rendered_text.append("\n")

            self.content.update(rendered_text)
            self.content.refresh()

        except Exception as e:
            error_msg = f"Error refreshing layout: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.content.update(f"[red]{error_msg}")


    async def _refresh_states(self) -> None:
        self._refresh_timer = self.set_timer(0.1, self._refresh_layout)

    def _stop_refresh(self) -> None:
        if self._refresh_timer:
            self._refresh_timer.stop()
            self._refresh_timer = None

    def _ensure_line_visible(self, line_number: int) -> None:
        region = Region(0, line_number, self.size.width, 1)
        self.scroll_to_region(region)

    def _get_valid_lines_for_delete_mode(self) -> list:
        if not self._source_node:
            return []
        valid_paths = set()
        for conn in self._source_node._inputs.values():
            valid_paths.add(conn.output_node().path())
        return [i for i, data in enumerate(self._node_data) if data.path in valid_paths]

    def action_move_cursor_up(self) -> None:
        if not self._initialized:
            return
            
        if self._connection_mode == ConnectionMode.DELETE:
            valid_lines = self._get_valid_lines_for_delete_mode()
            if not valid_lines:
                return
            current_idx = valid_lines.index(self._selected_line) if self._selected_line in valid_lines else -1
            if current_idx > 0:
                self._selected_line = valid_lines[current_idx - 1]
                self._refresh_layout()
                self._ensure_line_visible(self._selected_line)
        elif self._selected_line > 0:
            self._selected_line -= 1
            self._refresh_layout()
            self._ensure_line_visible(self._selected_line)

    def action_move_cursor_down(self) -> None:
        if not self._initialized:
            return
            
        if self._connection_mode == ConnectionMode.DELETE:
            valid_lines = self._get_valid_lines_for_delete_mode()
            if not valid_lines:
                return
            current_idx = valid_lines.index(self._selected_line) if self._selected_line in valid_lines else -1
            if current_idx < len(valid_lines) - 1:
                self._selected_line = valid_lines[current_idx + 1]
                self._refresh_layout()
                self._ensure_line_visible(self._selected_line)
        elif self._selected_line < len(self._node_data) - 1:
            self._selected_line += 1
            self._refresh_layout()
            self._ensure_line_visible(self._selected_line)

    def action_select_node(self) -> None:
        if not self._initialized:
            return
        if 0 <= self._selected_line < len(self._node_data):
            node_data = self._node_data[self._selected_line]
            self.post_message(NodeSelected(node_data.path))
            logger.debug(f"Selected node: {node_data.path}")

    def action_toggle_node(self) -> None:
        if not self._initialized:
            return
        # Future implementation for expanding/collapsing node hierarchies
        pass


    def _animate_cooking(self) -> None:
        self._animation_frame = (self._animation_frame + 1) % len(self.BRAILLE_SEQUENCE)
        self._refresh_layout()

    async def action_cook_node(self) -> None:
        if not self._initialized or self._cooking:
            return

        if self._selected_line >= len(self._node_data):
            return

        try:
            node_data = self._node_data[self._selected_line]
            node = self._env.node_from_name(node_data.path)
            
            if not node:
                return

            self._cooking = True
            self._cooking_node = node.path()
            self._animation_frame = 0
            
            # Set up animation timer
            self._animation_timer = self.set_interval(self.ANIMATION_FRAME_TIME, self._animate_cooking)
            
            def do_eval():
                return node.eval(force=True)
                
            worker = self.app.run_worker(do_eval, thread=True)
            result = await worker.wait()
            
            self.app.post_message(OutputMessage(result))

        except Exception as e:
            error_msg = f"Error cooking node: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.app.post_message(OutputMessage([f"Error: {error_msg}"]))
        
        finally:
            if self._animation_timer:
                self._animation_timer.stop()
            self._cooking = False
            self._cooking_node = None
            self._refresh_layout()
            self.action_get_output()