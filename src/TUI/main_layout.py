from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.widgets import Static

from TUI.node_window import NodeWindow, NodeSelected
from TUI.parameter_window import ParameterWindow
from TUI.global_window import GlobalWindow
from TUI.output_window import OutputWindow
from TUI.status_window import StatusWindow
from TUI.messages import OutputMessage

from TUI.logging_config import get_logger

logger = get_logger('tui.main_layout')

class MainLayout(Grid):
    DEFAULT_CSS = """
    MainLayout {
        height: 100%;
        width: 100%;
        grid-size: 3 1;
        grid-columns: 1fr 2fr 2fr;
        grid-rows: 1fr;
        grid-gutter: 0;
        background: $background;
        color: $foreground;
    }
    
    Vertical {
        height: 100%;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield NodeWindow()
        yield ParameterWindow()
        with Vertical():
            yield GlobalWindow()
            yield OutputWindow()
            yield StatusWindow()

    def on_node_selected(self, event: NodeSelected) -> None:
        self.query_one(ParameterWindow).on_node_selected(event)

    def on_output_message(self, message: OutputMessage) -> None:
        logger.debug("MainLayout received output message")
        output_window = self.query_one(OutputWindow)
        output_window.on_output_message(message)

class MainContent(Static):
    def compose(self) -> ComposeResult:
        yield MainLayout()

    def on_mount(self) -> None:
        self.query_one(NodeWindow).focus()