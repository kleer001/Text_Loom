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
    DEFAULT_CSS = """
    GlobalWindow {
        width: 100%;
        height: 50%;
        background: $background;
        border: solid $primary;
        layout: vertical;
    }

    GlobalWindow:focus, GlobalWindow:focus-within {
        border: double $secondary;
    }

    DataTable {
        width: 100%;
        height: 1fr;
        background: $background;
        color: $foreground;
        overflow: auto scroll;
        scrollbar-gutter: stable;
    }

    Input {
        width: 100%;
        height: 3;
        dock: top;
        background: $background;
        color: $text;
        border: solid $accent;
    }
    Input:focus {
        border: double $secondary;
    }
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
        global_store = GlobalStore().list()

        if not global_store:
            self.table.add_row("NONE", "NONE")
            return

        for key, value in global_store.items():
            self.table.add_row(key, str(value))

    def flash_error(self):
        logger.debug("Starting flash_error")
        try:
            self.input.styles.background = "$error"
            logger.debug("Set error background")
            self.app.set_timer(0.25, self.reset_background)
            logger.debug("Scheduled reset")
        except Exception as e:
            logger.debug(f"Flash error failed: {str(e)}")

    def reset_background(self):
        logger.debug("Resetting background")
        try:
            self.input.styles.background = "$background" #might need to be None ?
            logger.debug("Background reset complete")
        except Exception as e:
            logger.debug(f"Reset background failed: {str(e)}")

    def action_reset_input(self):
        self.input.value = ""

    def on_input_submitted(self, event: Input.Submitted):
        logger.debug(f"Input submitted with value: {event.value}")

        if event.value.lower() == "cut all globals":
            logger.debug("Cut all globals command detected")
            store = GlobalStore()
            all_globals = store.list()
            for key in list(all_globals):  # Create a copy of the list to iterate
                try:
                    self.delete_global(key)
                except Exception as e:
                    logger.debug(f"Error deleting global {key}: {str(e)}")
            self.input.value = ""
            return

        if "cut" in event.value:
            key_to_cut = event.value.split(" ", 1)[1]
            self.delete_global(key_to_cut)
            self.input.value = ""
            return


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
            store.cut(key)
            self.post_message(GlobalDeleted(key))
            self.refresh_table()
