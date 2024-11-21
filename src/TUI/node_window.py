from typing import Optional, List
from dataclasses import dataclass
from textual.widgets import Static, OptionList, Input
from textual.keys    import Keys
from textual.binding import Binding
from textual.containers import ScrollableContainer, Vertical
from textual.screen import ModalScreen, Screen
from textual.message import Message
from textual.geometry import Region, Size
from rich.text import Text
import os
from collections import namedtuple
from enum import Enum, auto

from TUI.parameter_window import ParameterChanged
from core.base_classes import NodeEnvironment, NodeState, generate_node_types, Node, NodeType
from core.flowstate_manager import load_flowstate
from TUI.network_visualizer import layout_network, render_layout, LayoutEntry
from TUI.logging_config import get_logger
from TUI.messages import NodeSelected, NodeTypeSelected, OutputMessage
import TUI.palette as pal

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


class NodeTypeSelector(ModalScreen):
    DEFAULT_CSS = f"""
    NodeTypeSelector {{
        align: center middle;
    }}

    Vertical {{
        width: 40;
        height: auto;
        border: {pal.NODE_BORDER_MODAL} {pal.NODE_MODAL_BORDER};
        background: {pal.NODE_MODAL_SURFACE};
        color: {pal.NODE_MODAL_TEXT};
    }}

    OptionList {{
        height: auto;
        max-height: 20;
    }}
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.node_types = generate_node_types()
        logger.debug("NodeTypeSelector initialized")

    def compose(self):
        with Vertical():
            type_list = sorted(self.node_types.keys())
            logger.debug(f"Available node types: {type_list}")
            yield OptionList(*type_list)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        logger.debug(f"Option selected: {event.option.prompt}")
        self.app.pop_screen()
        logger.debug(f"Posting NodeTypeSelected message with type: {event.option.prompt}")
        self.app.query_one(NodeWindow).post_message(NodeTypeSelected(event.option.prompt))

    def action_cancel(self):
        logger.debug("Selection cancelled")
        self.app.pop_screen()

class DeleteConfirmation(ModalScreen[bool]):
    DEFAULT_CSS = f"""
    DeleteConfirmation {{
        align: center middle;
    }}

    Vertical {{
        width: 40;
        height: auto;
        border: {pal.NODE_BORDER_MODAL} {pal.NODE_MODAL_BORDER};
        background: {pal.NODE_MODAL_SURFACE};
        color: {pal.NODE_MODAL_TEXT};
        padding: 1;
    }}

    Static {{
        text-align: center;
        width: 100%;
    }}
    """

    def __init__(self, node_name: str):
        super().__init__()
        self.node_name = node_name

    def compose(self):
        with Vertical():
            yield Static(f"Delete node '{self.node_name}'?")
            yield Static("Y/N")

    def on_key(self, event):
        if event.key.lower() == "y":
            self.dismiss(True)
        elif event.key.lower() == "n" or event.key == "escape":
            self.dismiss(False)

class RenameInput(Input):
    DEFAULT_CSS = f"""
    RenameInput {{
        height: 3;
        background: {pal.NODE_INPUT_BACKGROUND};
        color: {pal.NODE_INPUT_TEXT}
        border: none;
        padding: 0;
    }}
    """
    
    def __init__(self, original_node_path: str):
        super().__init__()
        self.original_node_path = original_node_path
            
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not self.value:
            self.remove()
            return

        try:
            old_node = NodeEnvironment.get_instance().node_from_name(self.original_node_path)
            if not old_node:
                self.remove()
                return
            
            old_path = old_node.path()
            old_name = os.path.basename(old_path)
            new_path = old_path.replace(old_name, self.value)

            if NodeEnvironment.get_instance().node_exists(new_path):
                logger.warning(f"Failed to rename node: name '{new_path}' already exists")
                self.remove()
                return
            
            logger.info(f"Renaming node from {old_path} to {new_path}")
            env = NodeEnvironment.get_instance()
            nodes_to_update = []
            
            for path, node in env.nodes.items():
                if path == old_path or path.startswith(f"{old_path}/"):
                    nodes_to_update.append(node)
                    logger.info(f"Will update node: {path}")
            
            for node in nodes_to_update:
                old_node_path = node.path()
                new_node_path = old_node_path.replace(old_path, new_path)
                logger.info(f"Updating node path from {old_node_path} to {new_node_path}")
                env.nodes[new_node_path] = node
                if old_node_path in env.nodes:
                    del env.nodes[old_node_path]
                if(node.rename(os.path.basename(new_node_path))):
                    logger.info(f"Successfully renamed node from {self.original_node_path} to {new_node_path}")
                else:
                    logger.warning(f"Failed to rename node: name '{self.value}' already exists") 

        except Exception as e:
            logger.error(f"Error renaming node: {str(e)}", exc_info=True)
        
        self.remove()
        self.app.query_one(NodeWindow)._refresh_layout()

class NodeWindow(ScrollableContainer):
    DEFAULT_CSS = f"""
        NodeWindow {{
            width: 100%;
            height: 100%;
            background: {pal.NODE_WIN_BACKGROUND};
            border: {pal.NODE_BORDER_NORMAL} {pal.NODE_WIN_BORDER};
            color: {pal.NODE_MODAL_TEXT};
        }}

        NodeWindow:focus {{
            border: {pal.NODE_BORDER_FOCUS} {pal.NODE_WIN_BORDER_FOCUS};
        }}

        NodeContent {{
            width: 100%;
            padding: 0 1;
        }}
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
        Binding("e", "get_output", "Get Node Output"),
        Binding("escape", "cancel_connection", "Cancel Connection"),
        Binding("C", "cook_node", "Cook Node"),
    ]

    def _get_state_indicator(self, node_state: NodeState, node_path: str) -> str:
        if self._cooking_node == node_path:
            return "◇"
        if (self._connection_mode != ConnectionMode.NONE and 
            self._source_node and 
            self._source_node.path() == node_path):
            return "↑" if self._connection_mode == ConnectionMode.INPUT else "↓"
            
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
                    self.parent.post_message(OutputMessage(["NO OUTPUT FROM NODE"]))
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

    def action_cancel_connection(self) -> None:
        if self._connection_mode != ConnectionMode.NONE:
            self._connection_mode = ConnectionMode.NONE
            self._source_node = None
            logger.debug("Cancelled connection")
            self._refresh_layout()

    def action_select_or_connect_node(self) -> None:
        if self._connection_mode != ConnectionMode.NONE:
            self.action_complete_connection()
        else:
            self.action_select_node()

    def action_complete_connection(self) -> None:
        if not self._initialized or not self._source_node:
            return

        if self._selected_line >= len(self._node_data):
            return

        target_data = self._node_data[self._selected_line]
        target_node = self._env.node_from_name(target_data.path)
        
        if not target_node:
            return

        try:
            if self._connection_mode == ConnectionMode.INPUT:
                self._source_node.set_next_input(target_node)
                logger.info(f"Connected input of {self._source_node.path()} to output of {target_node.path()}")
            else:  # OUTPUT mode
                target_node.set_next_input(self._source_node)
                logger.info(f"Connected input of {target_node.path()} to output of {self._source_node.path()}")
                
            self._connection_mode = ConnectionMode.NONE
            self._source_node = None
            self._refresh_layout()
            
        except Exception as e:
            logger.error(f"Error creating connection: {str(e)}", exc_info=True)
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
                logger.debug(f"Successfully created node: {new_node.path()}")
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
        if not self._initialized:
            return
        if 0 <= self._selected_line < len(self._node_data):
            node_data = self._node_data[self._selected_line]
            logger.debug(f"Delete requested for node: {node_data.path}")
            
            def delete_node(confirmed: bool):
                if confirmed:
                    try:
                        node = self._env.node_from_name(node_data.path)
                        if node:
                            node.destroy()
                            logger.info(f"Deleted node: {node_data.path}")
                            self._refresh_layout()
                    except Exception as e:
                        logger.error(f"Error deleting node: {str(e)}", exc_info=True)

            self.app.push_screen(DeleteConfirmation(node_data.name), delete_node)

    def action_rename_node(self) -> None:
        if not self._initialized or self._selected_line >= len(self._node_data):
            return

        node_data = self._node_data[self._selected_line]
        indent_offset = node_data.indent_level + 2
        #EYEBALLED IT! But it works. Hahaha! 
        relative_y = (- len(self._node_data) * 2) + 4 + self._selected_line 

        self._rename_input = RenameInput(node_data.path)
        self.mount(self._rename_input)
        
        self._rename_input.styles.width = self.content.size.width - indent_offset
        self._rename_input.styles.height = 3
        self._rename_input.styles.offset = (indent_offset, relative_y)
        self._rename_input.value = node_data.name
        self._rename_input.focus()

    def compose(self):
        yield self.content

    def on_mount(self) -> None:
        logger.debug("NodeWindow mounted")
        self._initialize_network()
        self.border_title = "Node Network"

    def _initialize_network(self) -> None:
        logger.debug("Initializing network")
        try:
            file_path = os.path.abspath("save_file.json")
            logger.info(f"Loading flowstate from {file_path}")
            
            if not os.path.exists(file_path):
                error_msg = f"Save file not found: {file_path}"
                logger.error(error_msg)
                self.content.update(f"[red]{error_msg}")
                return

            load_flowstate(file_path)
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
            self._env = NodeEnvironment.get_instance()
            layout_entries = layout_network(self._env)
            self._node_data = []
            rendered_text = Text()

            for i, entry in enumerate(layout_entries):
                node = entry.node
                self._node_data.append(NodeData(
                    name=node.name(),
                    path=node.path(),
                    line_number=i,
                    indent_level=entry.indent
                ))

                state_indicator = self._get_state_indicator(node.state(), node.path())
                line = " " * entry.indent + f"{state_indicator} {node.name()}"

                if node._inputs:
                    connections = []
                    for idx, conn in sorted(node._inputs.items()):
                        out_node = conn.output_node()
                        connections.append(f"{out_node.name()}[{conn.output_index()}]")
                    if connections:
                        line += f" <- " + ", ".join(connections)

                style = []
                if i == self._selected_line:
                    style.append("reverse")
                if node.path() == self._cooking_node:
                    style.append("underline")
                
                rendered_text.append(line + "\n", style=" ".join(style) if style else "")

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

    def action_move_cursor_up(self) -> None:
        if not self._initialized:
            return
        if self._selected_line > 0:
            self._selected_line -= 1
            self._refresh_layout()
            self._ensure_line_visible(self._selected_line)

    def action_move_cursor_down(self) -> None:
        if not self._initialized:
            return
        if self._selected_line < len(self._node_data) - 1:
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
            
            # Start the refresh timer
            self._refresh_timer = self.set_timer(0.1, self._refresh_layout)
            
            # Use regular worker for sync function
            def do_eval():
                return node.eval()
                
            worker = self.app.run_worker(do_eval, thread=True)
            result = await worker.wait()
            
            self.app.post_message(OutputMessage(result))

        except Exception as e:
            error_msg = f"Error cooking node: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.app.post_message(OutputMessage([f"Error: {error_msg}"]))
        
        finally:
            if self._refresh_timer:
                self._refresh_timer.stop()
            self._cooking = False
            self._cooking_node = None
            self._refresh_layout()