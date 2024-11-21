from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Static

from TUI.logging_config import get_logger
import TUI.palette as pal




class FileScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.file_screen')

    DEFAULT_CSS = f"""
    FileScreen {{
        align: center middle;
        background: {pal.FILE_SCR_BACKGROUND};
        color: {pal.FILE_SCR_TEXT}
        width: 100%;
        height: 100%;
    }}

    .file-content {{
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: {pal.FILECONTENT_SCR_BACKGROUND};
        color: {pal.FILECONTENT_SCR_TEXT}
    }}
    """

    def compose(self) -> ComposeResult:
        with Container(classes="file-content"):
            yield Static("File Browser (Placeholder)")

    def on_mount(self) -> None:
        self.logger.info("FileScreen mounted")
