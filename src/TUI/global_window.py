from textual.widgets import DataTable, Input
from textual.containers import Container
from textual.binding import Binding
from rich.text import Text

from core.global_store import GlobalStore

BACKGROUND_COLOR = "#E6E6FA"
HEADER_COLOR = "#FFE15D"
TABLE_COLOR = "#98FF98"
INPUT_COLOR = "#87CEEB"
ERROR_COLOR = "#FF9999"
TEXT_COLOR = "#2E4052"
BORDER_COLOR = "#FFB6C1"

class GlobalWindow(Container):
    DEFAULT_CSS = f"""
    GlobalWindow {{
        width: 100%;
        height: 12.5%;
        background: {BACKGROUND_COLOR};
        border: heavy {BORDER_COLOR};
        layout: vertical;
    }}

    DataTable {{
        width: 100%;
        height: 1fr;
        background: {TABLE_COLOR};
        color: {TEXT_COLOR};
        overflow: auto scroll;
        scrollbar-gutter: stable;
    }}

    Input {{
        width: 100%;
        height: 3;
        dock: top;
        background: {INPUT_COLOR};
        color: {TEXT_COLOR};
        border: solid {BORDER_COLOR};
    }}
    """

    BINDINGS = [
        Binding("escape", "reset_input", "Reset Input"),
    ]

    def __init__(self):
        super().__init__()
        self.table = DataTable(show_header=False, zebra_stripes=True)
        self.input = Input(placeholder="Enter KEY:VALUE")

    def compose(self):
        yield self.input
        yield self.table
        

    def on_mount(self):
        self.table.add_column(" ", key="key")
        self.table.add_column(" ", key="value")
        self.refresh_table()

    def refresh_table(self):
        self.table.clear()
        globals = GlobalStore().list()
        
        if not globals:
            self.table.add_row("NONE", "NONE")
            return
            
        for key, value in globals.items():
            self.table.add_row(key, str(value))

    def flash_error(self):
        self.input.styles.background = ERROR_COLOR
        self.call_after(0.25, setattr, self.input.styles, "background", INPUT_COLOR)

    def action_reset_input(self):
        self.input.value = ""

    def on_input_submitted(self, event: Input.Submitted):
        if ":" not in event.value:
            self.flash_error()
            return
            
        key, value = event.value.split(":", 1)
        key = "".join(c for c in key.upper() if c.isupper())
        value = value.strip()
        
        if len(key) < 2:
            self.flash_error()
            return
            
        try:
            GlobalStore().set(key, value)
            self.refresh_table()
            self.input.value = ""
        except ValueError:
            self.flash_error()