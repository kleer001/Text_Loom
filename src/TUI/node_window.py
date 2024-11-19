from typing import Optional, List
from dataclasses import dataclass
from textual.widgets import Static, OptionList
from textual.message import Message
from textual.binding import Binding
from textual.containers import ScrollableContainer, Vertical
from textual.screen import ModalScreen, Screen
from textual.geometry import Region
from rich.text import Text
import os

from core.base_classes import NodeEnvironment, NodeState, generate_node_types, Node, NodeType
from core.flowstate_manager import load_flowstate
from TUI.network_visualizer import layout_network, render_layout, LayoutEntry
from TUI.logging_config import get_logger

logger = get_logger('node')

@dataclass
class NodeData:
    name: str
    path: str
    line_number: int
    indent_level: int

class NodeSelected(Message):
    def __init__(self, node_path: str) -> None:
        self.node_path = node_path
        super().__init__()

class NodeContent(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_line = 0


class NodeTypeSelected(Message):
    def __init__(self, node_type: str) -> None:
        self.node_type = node_type
        super().__init__()

class NodeTypeSelector(ModalScreen):
    DEFAULT_CSS = """
    NodeTypeSelector {
        align: center middle;
    }

    Vertical {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
    }

    OptionList {
        height: auto;
        max-height: 20;
    }
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
    DEFAULT_CSS = """
    DeleteConfirmation {
        align: center middle;
    }

    Vertical {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    Static {
        text-align: center;
        width: 100%;
    }
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

class NodeWindow(ScrollableContainer):
    DEFAULT_CSS = """
    NodeWindow {
        width: 100%;
        height: 100%;
        background: $boost;
        border: solid $background;
    }
    
    NodeWindow:focus {
        border: double $accent;
    }
    
    NodeContent {
        width: 100%;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("up", "move_cursor_up", "Move Up"),
        Binding("down", "move_cursor_down", "Move Down"),
        Binding("enter", "select_node", "Select Node"),
        Binding("space", "toggle_node", "Expand/Collapse Node"),
        Binding("a", "add_node", "Add Node"),
        Binding("d", "delete_node", "Delete Node"),
    ]

    # def watch_node_type_selected(self, message: NodeTypeSelected) -> None:
    #     """Watch for NodeTypeSelected messages"""
    #     logger.debug(f"NodeWindow received NodeTypeSelected message: {message.node_type}")
    #     self._create_new_node(message.node_type)

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


    def _get_state_indicator(self, node_state: NodeState) -> str:
        """Get the character indicator for a node's state."""
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

    def compose(self):
        yield self.content

    def on_mount(self) -> None:
        logger.debug("NodeWindow mounted")
        self._initialize_network()

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
        logger.debug("Refreshing layout")
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

                state_indicator = self._get_state_indicator(node.state())
                line = " " * entry.indent + f"{state_indicator} {node.name()}"

                if node._inputs:
                    connections = []
                    for idx, conn in sorted(node._inputs.items()):
                        out_node = conn.output_node()
                        connections.append(f"{out_node.name()}[{conn.output_index()}]")
                    if connections:
                        line += f" <- " + ", ".join(connections)

                style = "reverse" if i == self._selected_line else ""
                rendered_text.append(line + "\n", style=style)

            self.content.update(rendered_text)
            self.content.refresh()
            logger.debug(f"Refreshed layout with {len(self._node_data)} nodes")

        except Exception as e:
            error_msg = f"Error refreshing layout: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.content.update(f"[red]{error_msg}")

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