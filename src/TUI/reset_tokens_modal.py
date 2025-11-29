from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Static
from textual.app import ComposeResult
from textual.events import Key

class ResetTokensConfirmation(ModalScreen[bool]):
    DEFAULT_CSS = """
    ResetTokensConfirmation {
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
            yield Static("Reset all token tracking data?")
            yield Static("This action cannot be undone")
            yield Static("Y/N")

    def on_key(self, event: Key) -> None:
        if event.key.lower() == "y":
            event.stop()
            self.dismiss(True)
        elif event.key.lower() == "n" or event.key == "escape":
            event.stop()
            self.dismiss(False)
