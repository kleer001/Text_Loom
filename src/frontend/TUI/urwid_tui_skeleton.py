import urwid
import enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict

class EditorState(enum.Enum):
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    WINDOW = "WINDOW"  # New state for window commands

class Mode(enum.Enum):
    NODE = "Node"
    PARM = "Parm"
    GLOBAL = "Global"
    FILE = "File"
    HELP = "Help"
    KEYMAP = "Keymap"
    STATUS = "Status"

class Event(enum.Enum):
    MODE_CHANGE = "mode_change"
    PATH_CHANGE = "path_change"
    BUFFER_CHANGE = "buffer_change"
    WINDOW_SPLIT = "window_split"
    WINDOW_CLOSE = "window_close"
    EDITOR_STATE_CHANGE = "editor_state_change"
    DEBUG_INFO = "debug_info"  # New event type for debugging

@dataclass
class EventData:
    event_type: Event
    data: Any

class EventDispatcher:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, event_type: Event, callback: Callable[[EventData], None]):
        self.subscribers[event_type].append(callback)
    
    def dispatch(self, event: EventData):
        for callback in self.subscribers[event.event_type]:
            callback(event)

class EditBuffer(urwid.Edit):
    def __init__(self, parent_buffer):
        super().__init__(multiline=True)
        self.parent_buffer = parent_buffer

    def keypress(self, size, key):
        if self.parent_buffer.editor_state in [EditorState.NORMAL, EditorState.WINDOW]:
            return key
        return super().keypress(size, key)

class Buffer(urwid.ListBox):
    def __init__(self, event_dispatcher: EventDispatcher):
        self.event_dispatcher = event_dispatcher
        self.editor_state = EditorState.NORMAL
        self.edit = EditBuffer(self)
        self.content = urwid.SimpleFocusListWalker([self.edit])
        super().__init__(self.content)

        self.event_dispatcher.subscribe(Event.EDITOR_STATE_CHANGE, self._handle_state_change)

    def _handle_state_change(self, event: EventData):
        self.editor_state = event.data

class WindowManager:
    def __init__(self, event_dispatcher: EventDispatcher):
        self.event_dispatcher = event_dispatcher
        self.main_buffer = Buffer(event_dispatcher)
        self.split_container = self.main_buffer
        self.current_container = self.split_container

    def get_main_widget(self):
        return self.current_container
    
    def _get_focused_buffer(self):
        if isinstance(self.split_container, Buffer):
            return self.split_container
        elif isinstance(self.split_container, (urwid.Pile, urwid.Columns)):
            widget_focus = self.split_container.get_focus()
            if widget_focus is not None and len(widget_focus) == 2:
                widget, _ = widget_focus
                return self._get_buffer_from_widget(widget)
        return self.main_buffer
    
    def _get_buffer_from_widget(self, widget):
        if isinstance(widget, Buffer):
            return widget
        elif isinstance(widget, (urwid.Pile, urwid.Columns)):
            focused_widget = widget.get_focus()
            if focused_widget is not None and len(focused_widget) == 2:
                focused_widget, _ = focused_widget
                return self._get_buffer_from_widget(focused_widget)
        return None
    
    def _initialize_split(self, orientation):
        current_buffer = self._get_focused_buffer()
        new_buffer = Buffer(self.event_dispatcher)

        if orientation == "vertical" and isinstance(self.split_container, urwid.Columns):
            self.split_container.contents.append((new_buffer, ('weight', 1)))
        elif orientation == "horizontal" and isinstance(self.split_container, urwid.Pile):
            self.split_container.contents.append((new_buffer, ('weight', 1)))
        else:
            if orientation == "vertical":
                self.split_container = urwid.Columns([
                    (urwid.WEIGHT, 1, current_buffer),
                    (urwid.WEIGHT, 1, new_buffer)
                ])
            else:
                self.split_container = urwid.Pile([
                    (urwid.WEIGHT, 1, current_buffer),
                    (urwid.WEIGHT, 1, new_buffer)
                ])
            self.current_container = self.split_container
            self.split_container.set_focus(1)

        return new_buffer

    def vsplit(self):
        return self._initialize_split("vertical")
    
    def hsplit(self):
        return self._initialize_split("horizontal")


class ModeLine(urwid.WidgetWrap):
    def __init__(self, event_dispatcher: EventDispatcher):
        self.mode = Mode.GLOBAL
        self.editor_state = EditorState.NORMAL
        self.path = ""
        self.buffer_name = ""
        self.debug_info = ""
        self.text = urwid.Text("")
        super().__init__(urwid.AttrMap(self.text, "modeline"))
        
        event_dispatcher.subscribe(Event.MODE_CHANGE, self._handle_mode_change)
        event_dispatcher.subscribe(Event.PATH_CHANGE, self._handle_path_change)
        event_dispatcher.subscribe(Event.BUFFER_CHANGE, self._handle_buffer_change)
        event_dispatcher.subscribe(Event.EDITOR_STATE_CHANGE, self._handle_state_change)
        event_dispatcher.subscribe(Event.DEBUG_INFO, self._handle_debug_info)
        
        self._update_text()
    
    def _handle_mode_change(self, event: EventData):
        self.mode = event.data
        self._update_text()
    
    def _handle_path_change(self, event: EventData):
        self.path = event.data
        self._update_text()
    
    def _handle_buffer_change(self, event: EventData):
        self.buffer_name = event.data
        self._update_text()

    def _handle_state_change(self, event: EventData):
        self.editor_state = event.data
        self._update_text()

    def _handle_debug_info(self, event: EventData):
        self.debug_info = event.data
        self._update_text()
    
    def _update_text(self):
        text = f"[{self.editor_state.value}] [{self.mode.value}] {self.path} ({self.buffer_name}) | Debug: {self.debug_info}"
        self.text.set_text(text)

class Editor:
    def __init__(self):
        self.event_dispatcher = EventDispatcher()
        self.window_manager = WindowManager(self.event_dispatcher)
        self.editor_state = EditorState.NORMAL
        
        self.modeline = ModeLine(self.event_dispatcher)
        self.main_display = self.window_manager.get_main_widget()
        
        self.layout = urwid.Frame(
            urwid.AttrMap(self.window_manager.get_main_widget(), 'default'), 
            header=self.modeline
        )

        self.palette = [
            ("modeline", "white", "dark blue"),
            ("default", "white", "black"),
        ]
        
        self.loop = urwid.MainLoop(
            self.layout,
            palette=self.palette,
            unhandled_input=self._handle_input
        )

    def _set_editor_state(self, state: EditorState):
        self.editor_state = state
        self.event_dispatcher.dispatch(EventData(Event.EDITOR_STATE_CHANGE, state))

    def _set_debug_info(self, info: str):
        self.event_dispatcher.dispatch(EventData(Event.DEBUG_INFO, info))
    
    def _handle_input(self, key):
        # Debug the key input
        self._set_debug_info(f"Key pressed: {key}")

        if key == "esc":
            self._set_editor_state(EditorState.NORMAL)
            return True
        
        if self.editor_state == EditorState.NORMAL:
            if key == "i":
                self._set_editor_state(EditorState.INSERT)
                return True
            elif key == " ":
                self.event_dispatcher.dispatch(EventData(Event.MODE_CHANGE, Mode.NODE))
                return True
            elif key == "ctrl w":
                self._set_debug_info("Entered window mode")
                self._set_editor_state(EditorState.WINDOW)
                return True
        
        elif self.editor_state == EditorState.WINDOW:
            self._set_debug_info(f"Window command: {key}")
            if key == "v":
                self.window_manager.vsplit()
                self._set_editor_state(EditorState.NORMAL)
                return True
            elif key == "s":
                self.window_manager.hsplit()
                self._set_editor_state(EditorState.NORMAL)
                return True
            elif key == "esc":
                self._set_editor_state(EditorState.NORMAL)
                return True
        
        return False
    
    def run(self):
        self._set_editor_state(EditorState.NORMAL)
        self.event_dispatcher.dispatch(EventData(Event.MODE_CHANGE, Mode.GLOBAL))
        self.event_dispatcher.dispatch(EventData(Event.PATH_CHANGE, "untitled"))
        self.event_dispatcher.dispatch(EventData(Event.BUFFER_CHANGE, "scratch"))
        self._set_debug_info("Editor started")
        self.loop.run()

if __name__ == "__main__":
    editor = Editor()
    editor.run()