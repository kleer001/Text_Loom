import curses
import enum
import logging
import time
import os
import sys
import signal
from functools import wraps
from typing import Optional, List, Dict, Callable, Any, Set
from cursor_base import NodeCursor, CursorStyle, CursorManager
from events import Event
from window_mode import *
from palette import initialize_colors, MODELINE, ACTIVE_WINDOW, INACTIVE_WINDOW, GUTTER

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor_timing.log")

def setup_debug_logging():
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def log_timing(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter_ns()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end = time.perf_counter_ns()
            duration_ms = (end - start) / 1_000_000
            logging.debug(f'{func.__name__}: {duration_ms:.3f}ms')
    return wrapper

class EditorState(enum.Enum):
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    WINDOW = "WINDOW"

class Mode(enum.Enum):
    NODE = "Node"
    PARM = "Parm"
    GLOBAL = "Global"
    FILE = "File"
    HELP = "Help"
    KEYMAP = "Keymap"
    STATUS = "Status"
    WINDOW = "Window"
    INSERT = "Insert"

    @property
    def cursor_class(self) -> type:
        return NodeCursor if self == Mode.NODE else CursorManager

class EventDispatcher:
    def __init__(self):
        self._listeners: Dict[Event, List[Callable]] = {event: [] for event in Event}
        self._batch_mode: bool = False
        self._pending_events: List[tuple[Event, Any]] = []

    def subscribe(self, event_type: Event, listener: Callable) -> None:
        if not callable(listener):
            raise TypeError("Listener must be callable")
        self._listeners[event_type].append(listener)

    @log_timing
    def dispatch(self, event_type: Event, data: Any = None) -> None:
        if self._batch_mode:
            self._pending_events.append((event_type, data))
            return

        logging.debug(f'Dispatching event: {event_type}')
        for listener in self._listeners[event_type]:
            try:
                listener(data)
            except Exception as e:
                logging.error(f'Error in event listener: {e}')

    def start_batch(self) -> None:
        self._batch_mode = True

    def end_batch(self) -> None:
        self._batch_mode = False
        for event_type, data in self._pending_events:
            self.dispatch(event_type, data)
        self._pending_events.clear()

class ModeLine:
    def __init__(self, event_dispatcher: EventDispatcher):
        self.mode = Mode.GLOBAL
        self.editor_state = EditorState.NORMAL
        self.path = ""
        self.buffer_name = ""
        self.debug_info = ""
        self.text = ""
        self._dirty = True
        
        for event in (Event.MODE_CHANGE, Event.PATH_CHANGE, 
                     Event.BUFFER_CHANGE, Event.EDITOR_STATE_CHANGE, 
                     Event.DEBUG_INFO):
            event_dispatcher.subscribe(event, self._mark_dirty)

    def _mark_dirty(self, _: Any) -> None:
        self._dirty = True

    @log_timing
    def update(self) -> None:
        if not self._dirty:
            return
            
        self.text = (f"[{self.editor_state.value}] | [{self.mode.value}] "
                    f"{self.path} ({self.buffer_name}) | {self.debug_info}")
        self._dirty = False

    def handle_mode_change(self, mode: Mode) -> None:
        self.mode = mode
        self._mark_dirty(None)

    def handle_path_change(self, path: str) -> None:
        self.path = path
        self._mark_dirty(None)

    def handle_buffer_change(self, buffer_name: str) -> None:
        self.buffer_name = buffer_name
        self._mark_dirty(None)

    def handle_state_change(self, editor_state: EditorState) -> None:
        self.editor_state = editor_state
        self._mark_dirty(None)

    def handle_debug_info(self, debug_info: str) -> None:
        self.debug_info = debug_info
        self._mark_dirty(None)

class EditorStateManager:
    def __init__(self, editor):
        self.editor = editor
        self.pending_updates: Set[tuple[str, Any]] = set()
        self._transition_lock: bool = False
        self._state_handlers: Dict[EditorState, Callable] = {
            EditorState.NORMAL: self._handle_normal_transition,
            EditorState.INSERT: self._handle_insert_transition,
            EditorState.WINDOW: self._handle_window_transition
        }

    def transition_to(self, new_state: EditorState) -> None:
        if self._transition_lock:
            return
            
        try:
            self._transition_lock = True
            self._perform_transition(new_state)
        finally:
            self._transition_lock = False
            self._process_updates()

    def _perform_transition(self, new_state: EditorState) -> None:
        old_state = self.editor.editor_state
        if old_state == new_state:
            return
            
        self.editor.editor_state = new_state
        handler = self._state_handlers.get(new_state)
        if handler:
            handler(old_state)
            
        self.pending_updates.add(('state', new_state))

    def _handle_normal_transition(self, old_state: EditorState) -> None:
        if self.editor.current_cursor:
            self.editor.current_cursor.set_style(CursorStyle.BLOCK)

    def _handle_insert_transition(self, old_state: EditorState) -> None:
        if self.editor.current_cursor:
            self.editor.current_cursor.set_style(CursorStyle.VERTICAL)

    def _handle_window_transition(self, old_state: EditorState) -> None:
        if self.editor.current_cursor:
            self.editor.current_cursor.set_style(CursorStyle.BLOCK)
        self.editor.current_mode = Mode.WINDOW

    def _process_updates(self) -> None:
        if not self.pending_updates:
            return

        self.editor.dispatcher.start_batch()
        try:
            state_updates = [u for u in self.pending_updates if u[0] == 'state']
            if state_updates:
                _, latest_state = state_updates[-1]
                self.editor.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, latest_state)
                self.editor.debug_info = f"Transitioned to {latest_state.value} mode"
                self.editor.dispatcher.dispatch(Event.DEBUG_INFO, self.editor.debug_info)
        finally:
            self.editor.dispatcher.end_batch()
            self.pending_updates.clear()

class Editor:
    def __init__(self):
        self.stdscr = None
        self.screen_height = 0
        self.screen_width = 0
        self.main_window = None
        self.mode_line_window = None
        
        self.current_mode = Mode.NODE
        self.editor_state = EditorState.NORMAL
        self.focused_window = 0
        
        self.path = "/"
        self.buffer_name = "untitled"
        self.debug_info = ""
        
        self.windows = []
        self.cursors = []
        self.current_cursor = None
        
        self.buffer_contents = {}
        self.mode_buffers = {}
        
        self.dispatcher = EventDispatcher()
        self.mode_line = ModeLine(self.dispatcher)
        self.state_manager = EditorStateManager(self)
        self.window_mode = WindowMode(self)
        
        self._setup_event_handlers()
        self._last_key_time = 0
        self._resize_pending = False

    def _setup_event_handlers(self) -> None:
        self.dispatcher.subscribe(Event.WINDOW_SPLIT, self._handle_window_split)
        self.dispatcher.subscribe(Event.WINDOW_CLOSE, self._handle_window_close)
        self.dispatcher.subscribe(Event.WINDOW_CHANGED, self._handle_window_change)

    def _handle_sigint(self, sig, frame):
        raise SystemExit

    def initialize(self, stdscr) -> None:
        signal.signal(signal.SIGINT, self._handle_sigint)
        self.stdscr = stdscr
        self.screen_height, self.screen_width = stdscr.getmaxyx()
        
        os.environ.setdefault('ESCDELAY', '25')
        curses.curs_set(0)
        curses.start_color()
        initialize_colors()
        
        self._setup_initial_windows()
        self.window_mode.initialize(stdscr)
        self._setup_cursors()
        self._initialize_buffers()
        self.highlight_focused_window()

    def _setup_initial_windows(self) -> None:
        self.stdscr.clear()
        self.mode_line_window = self.stdscr.subwin(1, self.screen_width, 0, 0)
        self.main_window = self.stdscr.subwin(self.screen_height - 1, self.screen_width, 1, 0)
        
        self.mode_line_window.bkgd(' ', curses.color_pair(MODELINE))
        self.main_window.bkgd(' ', curses.color_pair(ACTIVE_WINDOW))
        
        self.windows = [self.main_window]
        
        self.stdscr.refresh()
        self.mode_line_window.refresh()
        self.main_window.refresh()

    def _setup_cursors(self) -> None:
        self.cursors = [self.current_mode.cursor_class(window) for window in self.windows]
        self.current_cursor = self.cursors[self.focused_window] if self.cursors else None

    def _initialize_buffers(self) -> None:
        for window in self.windows:
            if window not in self.buffer_contents:
                self.buffer_contents[window] = []
            if window not in self.mode_buffers:
                self.mode_buffers[window] = {mode: [] for mode in Mode}

    @log_timing
    def handle_keypress(self, stdscr, key: int) -> None:
        current_time = time.time()
        if current_time - self._last_key_time > 0.5:
            self._handle_resize_if_pending()
        self._last_key_time = current_time

        if key == curses.KEY_RESIZE:
            self._resize_pending = True
            return

        self.dispatcher.start_batch()
        try:
            if self.current_mode == Mode.WINDOW:
                self.window_mode.handle_key(key, stdscr)
            elif key in (23, ord('i')):  # Ctrl+w or 'i'
                self._handle_mode_transition(key)
            elif self.editor_state == EditorState.INSERT:
                self._handle_insert_state(key)
            else:
                self._handle_normal_state(key, stdscr)
        finally:
            self.dispatcher.end_batch()
            self.update_mode_line(stdscr)

    def _handle_resize_if_pending(self) -> None:
        if not self._resize_pending:
            return
            
        try:
            new_height, new_width = self.stdscr.getmaxyx()
            if (new_height, new_width) != (self.screen_height, self.screen_width):
                self._handle_resize(new_height, new_width)
        finally:
            self._resize_pending = False

    def _handle_resize(self, new_height: int, new_width: int) -> None:
        self.screen_height, self.screen_width = new_height, new_width
        
        try:
            self.mode_line_window.resize(1, new_width)
            self.mode_line_window.mvwin(0, 0)
            
            if self.window_mode.root_frame:
                self.window_mode.root_frame.redistribute_space(1, 0, new_height - 1, new_width)
            else:
                self.main_window.resize(new_height - 1, new_width)
                self.main_window.mvwin(1, 0)
            
            self._redraw_all()
        except curses.error:
            logging.error("Resize operation failed")

    @log_timing
    def _redraw_all(self) -> None:
        try:
            self.stdscr.clear()
            self.mode_line_window.clear()
            
            for window in self.windows:
                window.clear()
                window.refresh()
            
            self._restore_all_buffers()
            self.window_mode._redraw_gutters()
            self.highlight_focused_window()
            
            self.stdscr.refresh()
            self.mode_line_window.refresh()
        except curses.error:
            logging.error("Redraw operation failed")

    def _restore_all_buffers(self) -> None:
        original_focus = self.focused_window
        try:
            for idx, window in enumerate(self.windows):
                self.focused_window = idx
                self._restore_buffer(self.current_mode)
        finally:
            self.focused_window = min(original_focus, len(self.windows) - 1)

    def highlight_focused_window(self) -> None:
        for idx, window in enumerate(self.windows):
            color = ACTIVE_WINDOW if idx == self.focused_window else INACTIVE_WINDOW
            window.bkgd(' ', curses.color_pair(color))
            window.refresh()

    @log_timing
    def update_mode_line(self, stdscr) -> None:
        try:
            self.mode_line.update()
            self.mode_line_window.clear()
            self.mode_line_window.addstr(0, 0, self.mode_line.text)
            self.mode_line_window.refresh()
        except curses.error:
            logging.error("Mode line update failed")

    def _handle_window_split(self, _) -> None:
        self._setup_cursors()
        self._initialize_buffers()
        self.highlight_focused_window()

    def _handle_window_close(self, _) -> None:
        self._setup_cursors()
        if self.current_cursor:
            self.current_cursor.move_absolute(1, 0)
            self.current_cursor.render()

    def _handle_window_change(self, _) -> None:
        if self.current_cursor:
            self.current_cursor.move_absolute(1, 0)
            self.current_cursor.render()

    def run(self, stdscr) -> None:
        self.dispatcher.dispatch(Event.MODE_CHANGE, self.current_mode)
        self.debug_info = f"Started in {self.current_mode.value} mode"
        self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)

        while True:
            self.update_mode_line(stdscr)
            key = stdscr.getch()
            self.handle_keypress(stdscr, key)

    def _save_current_buffer(self) -> None:
        window = self.windows[self.focused_window]
        height, width = window.getmaxyx()
        buffer_content = []
        
        try:
            for y in range(height):
                line = []
                for x in range(width):
                    char = window.inch(y, x)
                    char_str = chr(char & curses.A_CHARTEXT)
                    attrs = char & curses.A_ATTRIBUTES
                    line.append((char_str, attrs))
                buffer_content.append(line)
            
            self.mode_buffers[window][self.current_mode] = buffer_content
        except curses.error:
            logging.error(f"Failed to save buffer for window {self.focused_window}")

    def _restore_buffer(self, mode: Mode) -> None:
        window = self.windows[self.focused_window]
        window.clear()
        
        try:
            if window in self.mode_buffers and mode in self.mode_buffers[window]:
                buffer_content = self.mode_buffers[window][mode]
                for y, line in enumerate(buffer_content):
                    for x, (char, attrs) in enumerate(line):
                        window.addch(y, x, ord(char), attrs)
            window.refresh()
        except curses.error:
            logging.error(f"Failed to restore buffer for window {self.focused_window}")

    def clear_current_buffer(self) -> None:
        window = self.windows[self.focused_window]
        try:
            window.clear()
            window.refresh()
            if window in self.mode_buffers:
                self.mode_buffers[window][self.current_mode] = []
        except curses.error:
            logging.error("Failed to clear current buffer")

    def _handle_mode_transition(self, key: int) -> None:
        if key == 23:  # Ctrl+w
            self._transition_to_window_mode()
        elif key == ord('i'):
            self.state_manager.transition_to(EditorState.INSERT)

    def _transition_to_window_mode(self) -> None:
        old_mode = self.current_mode
        self._save_current_buffer()
        self.current_mode = Mode.WINDOW
        self.state_manager.transition_to(EditorState.WINDOW)
        
        self.dispatcher.start_batch()
        try:
            self.dispatcher.dispatch(Event.MODE_CHANGE, self.current_mode)
            self.debug_info = (f"Window Mode - s:hsplit v:vsplit w:cycle q:close "
                             f"=:equalize _|:maximize <> -+:resize")
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)
        finally:
            self.dispatcher.end_batch()

    def _handle_normal_state(self, key: int, stdscr) -> None:
        if self._handle_mode_switch(key):
            return
            
        if self.current_cursor:
            self.current_cursor.handle_key(key)

    def _handle_insert_state(self, key: int) -> None:
        if key == 27:  # ESC key
            self.state_manager.transition_to(EditorState.NORMAL)
            return
            
        if not self.current_cursor or self.current_cursor.handle_key(key):
            return
            
        self._handle_insert_key(key)

    def _handle_insert_key(self, key: int) -> None:
        window = self.windows[self.focused_window]
        try:
            if key == 10:  # Enter
                y, x = self.current_cursor.get_position()
                max_y, _ = window.getmaxyx()
                if y < max_y - 1:
                    window.move(y + 1, 0)
            elif key == 127:  # Backspace
                y, x = self.current_cursor.get_position()
                if x > 0:
                    window.move(y, x - 1)
                    window.delch()
                elif y > 0:
                    window.move(y - 1, 0)
            elif 32 <= key <= 126:  # Printable ASCII
                window.addch(chr(key))
            
            window.refresh()
        except curses.error:
            logging.error("Failed to handle insert key")

    def _handle_mode_switch(self, key: int) -> bool:
        key_name = curses.keyname(key).decode('utf-8') if key != ord('=') else '='
        
        mode_keys = {
            'n': Mode.NODE,
            'p': Mode.PARM,
            'g': Mode.GLOBAL,
            'f': Mode.FILE,
            'h': Mode.HELP,
            'k': Mode.KEYMAP,
            't': Mode.STATUS
        }
        
        space_press = key_name == ' '
        if space_press:
            self._space_pressed = True
            return True
            
        if not getattr(self, '_space_pressed', False):
            return False
            
        self._space_pressed = False
        if key_name not in mode_keys:
            return False
            
        return self._perform_mode_switch(mode_keys[key_name])

    def _perform_mode_switch(self, new_mode: Mode) -> bool:
        if new_mode == self.current_mode:
            return True
            
        old_mode = self.current_mode
        self._save_current_buffer()
        self.clear_current_buffer()
        self.current_mode = new_mode
        
        self.dispatcher.start_batch()
        try:
            self._restore_buffer(new_mode)
            self._setup_cursors()  
            self.dispatcher.dispatch(Event.MODE_CHANGE, new_mode)
            
            if new_mode == Mode.HELP:
                self._load_help_content()
            elif new_mode == Mode.NODE:
                self._setup_test_nodes()
            
            self.debug_info = f"Switched from {old_mode.value} to {new_mode.value}"
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)
            return True
        except Exception as e:
            logging.error(f"Mode switch failed: {e}")
            return False
        finally:
            self.dispatcher.end_batch()

    def _load_help_content(self) -> None:
        help_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'help.md'
        )
        
        try:
            with open(help_path, 'r') as f:
                content = f.read().splitlines()
                window = self.windows[self.focused_window]
                max_y, max_x = window.getmaxyx()
                
                for y, line in enumerate(content):
                    if y >= max_y:
                        break
                    window.addstr(y, 0, line[:max_x-1])
                window.refresh()
        except FileNotFoundError:
            self.debug_info = f"Help file not found: {help_path}"
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)
        except curses.error:
            logging.error("Failed to load help content")

    def _setup_test_nodes(self) -> None:
        window = self.windows[self.focused_window]
        
        nodes = [
            # Level 0 nodes (Cities)
            [(2, 2, "Tokyo"), (4, 2, "Paris"), (6, 2, "London"), (8, 2, "New York")],
            # Level 1 nodes (Foods)
            [(2, 15, "Ramen"), (4, 15, "Baguette"), (6, 15, "Tea"), (8, 15, "Pizza")],
            # Level 2 nodes (Restaurants)
            [(2, 30, "Ichiran"), (4, 30, "Le Cheval d'Or"), 
             (6, 30, "The Wolseley"), (8, 30, "Grimaldi's")]
        ]
        
        try:
            for level, level_nodes in enumerate(nodes):
                for y, x, text in level_nodes:
                    window.addstr(y, x, text)
                    self.current_cursor.register_node(y, x, level, len(text))
                    
            for y in range(2, 9, 2):
                window.addstr(y, 12, "──")
                window.addstr(y, 25, "──")
                
            window.refresh()
            self.current_cursor.move_absolute(2, 2)
        except curses.error:
            logging.error("Failed to setup test nodes")

def setup_terminal() -> None:
    os.environ.setdefault('ESCDELAY', '25')
    os.environ.setdefault('TERM', 'xterm-256color')
    
    if os.name != 'nt':  # Not Windows
        os.system('tput init')

def cleanup_terminal() -> None:
    if os.name != 'nt':
        os.system('tput reset')

@log_timing
def main(stdscr) -> None:
    try:
        setup_debug_logging()
        setup_terminal()
        
        curses.raw()
        curses.noecho()
        curses.curs_set(0)
        
        editor = Editor()
        editor.initialize(stdscr)
        editor.run(stdscr)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise
    finally:
        cleanup_terminal()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Fatal error occurred: {e}")
        print("Check the log file for details.")
        sys.exit(1)