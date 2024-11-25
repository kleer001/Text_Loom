from textual.widgets import DataTable, Input
from textual.containers import Container
from textual.binding import Binding
from rich.text import Text

from core.global_store import GlobalStore
import TUI.palette as pal
from TUI.logging_config import get_logger
from TUI.messages import GlobalAdded, GlobalChanged, GlobalDeleted

logger = get_logger('global')


class GlobalWindow(Container):
    DEFAULT_CSS = f"""
    GlobalWindow {{
        width: 100%;
        height: 20%;
        background: {pal.GLOBAL_WIN_BACKGROUND_COLOR};
        border: heavy {pal.GLOBAL_WIN_BORDER_COLOR};
        layout: vertical;
    }}

    DataTable {{
        width: 100%;
        height: 1fr;
        background: {pal.GLOBAL_WIN_TABLE_COLOR};
        color: {pal.GLOBAL_WIN_TEXT_COLOR};
        overflow: auto scroll;
        scrollbar-gutter: stable;
    }}

    Input {{
        width: 100%;
        height: 3;
        dock: top;
        background: {pal.GLOBAL_WIN_INPUT_COLOR};
        color: {pal.GLOBAL_WIN_TEXT_COLOR};
        border: solid {pal.GLOBAL_WIN_BORDER_COLOR};
    }}
    """

    BINDINGS = [
        Binding("escape", "reset_input", "Reset Input"),
    ]

    def __init__(self):
        super().__init__()
        self.table = DataTable(show_header=False, zebra_stripes=True)
        self.input = Input(placeholder="Enter KEY:VALUE")

    can_focus = True

    def compose(self):
        yield self.input
        yield self.table
    
    def on_focus(self) -> None:
        self.input.focus()

    def on_mount(self):
        self.table.add_column(" ", key="key")
        self.table.add_column(" ", key="value")
        self.border_title = "Globals"    
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
        logger.debug("Starting flash_error")
        try:
            self.input.styles.background = pal.GLOBAL_WIN_ERROR_COLOR
            logger.debug("Set error background")
            self.app.set_timer(0.25, self.reset_background)
            logger.debug("Scheduled reset")
        except Exception as e:
            logger.debug(f"Flash error failed: {str(e)}")

    def reset_background(self):
        logger.debug("Resetting background")
        try:
            self.input.styles.background = None  # This removes our override and falls back to CSS
            logger.debug("Background reset complete")
        except Exception as e:
            logger.debug(f"Reset background failed: {str(e)}")

    def action_reset_input(self):
        self.input.value = ""

    def on_input_submitted(self, event: Input.Submitted):
        logger.debug(f"Input submitted with value: {event.value}")
        
        if ":" not in event.value:
            logger.debug("No colon found in input")
            self.flash_error()
            self.input.value = ""
            return
            
        try:
            key, value = event.value.split(":", 1)
            logger.debug(f"Split input into key: {key}, value: {value}")
            
            key = "".join(c for c in key.upper() if c.isupper())
            value = value.strip()
            logger.debug(f"Processed key: {key}, processed value: {value}")
            
            if len(key) < 2:
                logger.debug("Key length less than 2")
                self.flash_error()
                self.input.value = ""
                return

            store = GlobalStore()
            if key in store.list():
                logger.debug(f"Updating existing global: {key}")
                self.post_message(GlobalChanged(key, value))
            else:
                logger.debug(f"Adding new global: {key}")
                self.post_message(GlobalAdded(key, value))
                
            store.set(key, value)
            logger.debug("Successfully set global value")
            self.refresh_table()
            self.input.value = ""
        except Exception as e:
            logger.debug(f"Exception occurred: {str(e)}")
            self.flash_error()
            self.input.value = ""

    def delete_global(self, key: str) -> None:
        logger.debug(f"Deleting global: {key}")
        store = GlobalStore()
        if key in store.list():
            store.delete(key)
            self.post_message(GlobalDeleted(key))
            self.refresh_table()