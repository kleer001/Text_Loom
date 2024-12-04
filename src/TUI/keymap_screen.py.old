from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Static

from TUI.logging_config import get_logger
import TUI.palette as pal

logger = get_logger('keymap')




class KeymapScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.keymap_screen')

    DEFAULT_CSS = f"""
    KeymapScreen {{
        align: center middle;
        background: {pal.KEYMAP_SCR_BACKGROUND};
        color: {pal.KEYMAP_SCR_TEXT};
        width: 100%;
        height: 100%;
    }}

    .keymap-content {{
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: {pal.KEYMAPCONTENT_SCR_BACKGROUND};
        color: {pal.KEYMAPCONTENT_SCR_TEXT}; 
    }}
    """

    def compose(self) -> ComposeResult:
        with Container(classes="keymap-content"):
            yield Static("Keymap Browser (Placeholder)")

    def on_mount(self) -> None:
        self.logger.info("KeymapScreen mounted")
