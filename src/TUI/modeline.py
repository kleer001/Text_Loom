from textual.reactive import reactive
from textual.widgets import Static
from textual.binding import Binding
from typing import ClassVar
from enum import Enum
from dataclasses import dataclass

from core.token_manager import get_token_manager
from TUI.messages import OutputMessage, FileLoaded


class Mode(Enum):
    NODE = "NODE"
    PARAMETER = "PARAMETER"
    GLOBAL = "GLOBAL"
    HELP = "HELP"
    KEYMAP = "KEYMAP"
    STATUS = "STATUS"
    OUTPUT = "OUTPUT"

class ModeLine(Static):
    DEFAULT_CSS = """
    ModeLine {
        width: 100%;
        height: 1;
        background: $background;
        color: $secondary;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("t", "toggle_token_view", "Toggle Token View", show=False),
        Binding("shift+x", "reset_tokens", "Reset Tokens", show=False),
    ]

    mode: Mode = reactive(Mode.NODE)
    path: str = reactive("untitled")
    debug_info: str = reactive("")
    keypress: str = reactive("")
    token_info: str = reactive("")
    selected_node_name: str = reactive("")
    token_view_mode: str = reactive("session")

    def on_mount(self) -> None:
        self._update_token_info()

    def on_output_message(self, message: OutputMessage) -> None:
        self._update_token_info()

    def on_file_loaded(self, message: FileLoaded) -> None:
        self._update_token_info()

    def watch_mode(self) -> None:
        self._refresh_display()

    def watch_path(self) -> None:
        self._refresh_display()

    def watch_debug_info(self) -> None:
        self._refresh_display()

    def watch_keypress(self) -> None:
        self._refresh_display()

    def watch_token_info(self) -> None:
        self._refresh_display()

    def watch_token_view_mode(self) -> None:
        self._update_token_info()

    def watch_selected_node_name(self) -> None:
        if self.token_view_mode == "node":
            self._update_token_info()

    def _update_token_info(self) -> None:
        try:
            token_manager = get_token_manager()

            if self.token_view_mode == "session":
                totals = token_manager.get_totals()
                self.token_info = f"in:{totals['input_tokens']:,} out:{totals['output_tokens']:,} total:{totals['total_tokens']:,}"
            elif self.token_view_mode == "node" and self.selected_node_name:
                totals = token_manager.get_node_totals(self.selected_node_name)
                self.token_info = f"{self.selected_node_name}: in:{totals['input_tokens']:,} out:{totals['output_tokens']:,} total:{totals['total_tokens']:,}"
            elif self.token_view_mode == "node":
                self.token_info = "node: (none selected)"
            else:
                self.token_info = ""
        except Exception:
            self.token_info = ""

    def action_toggle_token_view(self) -> None:
        if self.token_view_mode == "session":
            self.token_view_mode = "node"
        else:
            self.token_view_mode = "session"

    def action_reset_tokens(self) -> None:
        try:
            token_manager = get_token_manager()
            token_manager.reset()
            self._update_token_info()
        except Exception:
            pass

    def _refresh_display(self) -> None:
        display_text = f"📝🧵 [{self.mode}] {self.path}"
        if self.debug_info:
            display_text += f" | {self.debug_info}"
        if self.keypress:
            display_text += f" | Keys: {self.keypress}"
        if self.token_info:
            display_text += f"   🪙 {self.token_info}"
        self.update(display_text)