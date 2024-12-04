from enum import Enum, auto
from typing import Dict, Type
from textual.screen import Screen
from textual.message import Message
from dataclasses import dataclass

class Mode(Enum):
    NODE = auto()
    PARAMETER = auto()
    GLOBAL = auto()
    FILE = auto()
    HELP = auto()
    KEYMAP = auto()
    STATUS = auto()
    OUTPUT = auto()

    def __str__(self) -> str:
        return self.name.title()

@dataclass
class ModeChanged(Message):
    """Message sent when mode changes"""
    mode: Mode

# Screen identifiers
MAIN_SCREEN = "main"
FILE_SCREEN = "file"
KEYMAP_SCREEN = "keymap"

# Common action commands
ACTION_SWITCH_TO_MAIN = "app.switch_screen('main')"
ACTION_SWITCH_TO_FILE = "app.switch_screen('file')"
ACTION_SWITCH_TO_KEYMAP = "app.switch_screen('keymap')"

# Screen registration function
def get_screen_registry(file_screen_cls: Type[Screen], keymap_screen_cls: Type[Screen]) -> Dict[str, Type[Screen]]:
    return {
        MAIN_SCREEN: Screen,
        FILE_SCREEN: file_screen_cls,
        KEYMAP_SCREEN: keymap_screen_cls
    }