from textual.app import App, ComposeResult
from textual.containers import Container
from textual.binding import Binding
from textual.widgets import Static
from textual.reactive import reactive
from palette import STYLES, TUIPalette
from textual import log
import os

os.environ["TEXTUAL"] = "debug"

class ModeLine(Static):
    def __init__(self):
        super().__init__("")
        self.update_info()

    def update_info(self, mode="Node", file="untitled", debug=""):
        self.update(f"[{mode}] {file} | {debug}")

class ContentArea(Static):
    def update_content(self, mode: str):
        content = {
            "node": "Node Tree View",
            "parameter": "Parameter View",
            "status": "Status View",
            "output": "Output View",
            "global": "Global View",
            "file": "File Browser",
            "help": "Help View",
            "keymap": "Keymap View"
        }
        self.update(content.get(mode, "Unknown Mode"))

class TUIApp(App):
    CSS_PATH = "tui.css"
    
    BINDINGS = [
        Binding("ctrl+n", "switch_mode('node')", "Node Mode"),
        Binding("ctrl+r", "switch_mode('parameter')", "Parameter Mode"),
        Binding("ctrl+g", "switch_mode('global')", "Global Mode"),
        Binding("ctrl+f", "switch_mode('file')", "File Mode"),
        Binding("ctrl+h", "switch_mode('help')", "Help Mode"),
        Binding("ctrl+k", "switch_mode('keymap')", "Keymap Mode"),
        Binding("ctrl+t", "switch_mode('status')", "Status Mode"),
        Binding("ctrl+o", "switch_mode('output')", "Output Mode"),
    ]

    current_mode = reactive("node")

    def compose(self) -> ComposeResult:
        yield ModeLine()
        yield ContentArea(id="content")
    
    def on_mount(self) -> None:
        log.info("App mounted")
        self.styles.background = TUIPalette.BACKGROUND_BASE
        self.styles.color = TUIPalette.FOREGROUND
        self.action_switch_mode("node")  # Set initial mode
        
    def action_switch_mode(self, mode: str) -> None:
        log.info(f"Switching to {mode} mode")
        self.current_mode = mode
        self.query_one(ModeLine).update_info(mode=mode.title())
        self.query_one(ContentArea).update_content(mode)

if __name__ == "__main__":
    app = TUIApp()
    app.run()