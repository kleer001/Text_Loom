from textual.reactive import reactive
from textual.widgets import Static
from typing import ClassVar
from enum import Enum
from dataclasses import dataclass
import TUI.palette as pal


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
    mode: Mode = reactive(Mode.NODE)
    path: str = reactive("untitled")
    debug_info: str = reactive("")
    keypress: str = reactive("")

    def watch_mode(self) -> None:
        self._refresh_display()

    def watch_path(self) -> None:
        self._refresh_display()
        
    def watch_debug_info(self) -> None:
        self._refresh_display()

    def watch_keypress(self) -> None:
        self._refresh_display()

    def _refresh_display(self) -> None:
        display_text = f"📝🧵 [{self.mode}] {self.path}"
        if self.debug_info:
            display_text += f" | {self.debug_info}"
        if self.keypress:
            display_text += f" | Keys: {self.keypress}"
        self.update(display_text)