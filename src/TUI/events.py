# events.py
from enum import Enum, auto

class Event(Enum):
    MODE_CHANGE = "mode_change"
    PATH_CHANGE = "path_change"
    BUFFER_CHANGE = "buffer_change"
    WINDOW_SPLIT = "window_split"
    WINDOW_CLOSE = "window_close"
    EDITOR_STATE_CHANGE = "editor_state_change"
    DEBUG_INFO = "debug_info"