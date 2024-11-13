from typing import Optional, List
from dataclasses import dataclass
from textual.widgets import Static
from textual.message import Message
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.geometry import Region
from rich.text import Text
import os

from core.base_classes import NodeEnvironment
from core.flowstate_manager import load_flowstate
from network_visualizer import layout_network, render_layout, LayoutEntry
from logging_config import get_logger

logger = get_logger('tui.node')

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
    ]

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
        self._initialize_network()

    def _initialize_network(self) -> None:
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

                line = " " * entry.indent + node.name()
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