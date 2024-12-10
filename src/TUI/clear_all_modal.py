from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Static
from textual.app import ComposeResult

class ClearAllConfirmation(ModalScreen[bool]):
    DEFAULT_CSS = """
    ClearAllConfirmation {
        align: center middle;
    }
    Vertical {
        width: 40;
        height: auto;
        border: solid $primary;
        background: $accent;
        color: $panel;
        padding: 1;
    }
    Static {
        text-align: center;
        width: 100%;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Clear all nodes and globals?")
            yield Static("This action cannot be undone")
            yield Static("Y/N")
            
    def on_key(self, event):
        if event.key.lower() == "y":
            self.dismiss(True)
        elif event.key.lower() == "n" or event.key == "escape":
            self.dismiss(False)