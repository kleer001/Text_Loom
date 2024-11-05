import curses
import enum
from cursor_base import *
import logging
import time
from functools import wraps

file_path = os.path.abspath("editor_timing.log")

def setup_debug_logging():
    logging.basicConfig(
        filename=file_path,
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(message)s',
        datefmt='%H:%M:%S'
    )

def log_timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logging.debug(f'{func.__name__}: {(end - start) * 1000:.2f}ms')
        return result
    return wrapper

class EditorState(enum.Enum):
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    WINDOW = "WINDOW"

class Mode(enum.Enum):
    NODE = "Node" #wasd/arrow/hjkl movement etc... 
    PARM = "Parm" #line base key:value boxes, 1 per line (keys cannot be changed)
    GLOBAL = "Global" #line based key:value boxes, 1 per line
    FILE = "File" #up/down/enter/backspace
    HELP = "Help" #no input
    KEYMAP = "Keymap" #line based key:value boxes, 1 per line
    STATUS = "Status" #no input

class Event(enum.Enum):
    MODE_CHANGE = "mode_change"
    PATH_CHANGE = "path_change"
    BUFFER_CHANGE = "buffer_change"
    WINDOW_SPLIT = "window_split"
    WINDOW_CLOSE = "window_close"
    EDITOR_STATE_CHANGE = "editor_state_change"
    DEBUG_INFO = "debug_info"

class EventDispatcher:
    def __init__(self):
        self.listeners = {event: [] for event in Event}

    def subscribe(self, event_type, listener):
        self.listeners[event_type].append(listener)

    @log_timing
    def dispatch(self, event_type, data=None):
        logging.debug(f'Dispatching event: {event_type}')
        for listener in self.listeners[event_type]:
            start = time.perf_counter()
            listener(data)
            end = time.perf_counter()
            logging.debug(f'Event listener took: {(end - start) * 1000:.2f}ms')

class ModeLine:
    def __init__(self, event_dispatcher: EventDispatcher):
        self.mode = Mode.GLOBAL
        self.editor_state = EditorState.NORMAL
        self.path = ""
        self.buffer_name = ""
        self.debug_info = ""
        self.text = ""

        event_dispatcher.subscribe(Event.MODE_CHANGE, self._handle_mode_change)
        event_dispatcher.subscribe(Event.PATH_CHANGE, self._handle_path_change)
        event_dispatcher.subscribe(Event.BUFFER_CHANGE, self._handle_buffer_change)
        event_dispatcher.subscribe(Event.EDITOR_STATE_CHANGE, self._handle_state_change)
        event_dispatcher.subscribe(Event.DEBUG_INFO, self._handle_debug_info)

        self._update_text()

    def _handle_mode_change(self, mode):
        self.mode = mode
        self._update_text()

    def _handle_path_change(self, path):
        self.path = path
        self._update_text()

    def _handle_buffer_change(self, buffer_name):
        self.buffer_name = buffer_name
        self._update_text()

    @log_timing
    def _handle_state_change(self, editor_state):
        logging.debug(f'Handling state change to: {editor_state}')
        self.editor_state = editor_state
        self._update_text()

    def _handle_debug_info(self, debug_info):
        self.debug_info = debug_info
        self._update_text()

    @log_timing
    def _update_text(self):
        logging.debug('Updating mode line text')
        # Update ModeLine class _update_text method
        self.text = f"[{self.editor_state.value}] | [{self.mode.value}] {self.path} ({self.buffer_name}) | Debug: {self.debug_info}"

class EditorStateManager:
    def __init__(self, editor):
        self.editor = editor
        self.pending_updates = set()
        
    def transition_to(self, new_state):
        """Fast state transition with batched updates"""
        old_state = self.editor.editor_state
        self.editor.editor_state = new_state
        
        # Update cursor style immediately
        if self.editor.current_cursor:
            if new_state == EditorState.INSERT:
                self.editor.current_cursor.set_style(CursorStyle.VERTICAL)
            else:
                self.editor.current_cursor.set_style(CursorStyle.BLOCK)
        
        # Queue required updates
        self.pending_updates.add(('state', new_state))
        
        # Dispatch events in batch
        self._process_updates()
        
    def _process_updates(self):
        """Process all pending updates at once"""
        if not self.pending_updates:
            return
            
        # Group similar updates
        state_updates = [u for u in self.pending_updates if u[0] == 'state']
        
        # Only dispatch the most recent state change
        if state_updates:
            _, latest_state = state_updates[-1]
            self.editor.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, latest_state)
            self.editor.debug_info = f"Transitioned to {latest_state.value} mode"
            self.editor.dispatcher.dispatch(Event.DEBUG_INFO, self.editor.debug_info)
        
        self.pending_updates.clear()

class Editor:
    def __init__(self):
        self.current_mode = Mode.NODE
        self.space_pressed = False
        self.path = "/"
        self.buffer_name = "untitled"
        self.debug_info = ""
        self.windows = []
        self.dispatcher = EventDispatcher()
        self.mode_line = ModeLine(self.dispatcher)
        self.palette = [
            ("modeline", "color_white", "color_blue"),
            ("default", "color_black", "color_white"),
        ]
        self.insert_mode = False
        self.editor_state = EditorState.NORMAL
        self.focused_window = 0
        self.cursor_y = 1
        self.cursor_x = 0
        self.cursors = []
        self.current_cursor = None
        self.buffer_contents = {}
        self.mode_buffers = {}        
        self.state_manager = EditorStateManager(self) 
        setup_debug_logging()

    def initialize(self, stdscr):
        self.setup_colors()
        self.setup_windows(stdscr)
        self._setup_cursors()
        self._initialize_buffers()

    def _initialize_buffers(self):
        for window in self.windows:
            self.buffer_contents[window] = []
            for mode in Mode:
                if window not in self.mode_buffers:
                    self.mode_buffers[window] = {}
                self.mode_buffers[window][mode] = []

    def _save_current_buffer(self):
        window = self.windows[self.focused_window]
        height, width = window.getmaxyx()
        buffer_content = []
        for y in range(height):
            line = []
            for x in range(width):
                try:
                    char = window.inch(y, x)
                    char_str = chr(char & curses.A_CHARTEXT)
                    attrs = char & curses.A_ATTRIBUTES
                    line.append((char_str, attrs))
                except curses.error:
                    break
            buffer_content.append(line)
        self.mode_buffers[window][self.current_mode] = buffer_content

    def _restore_buffer(self, mode):
        window = self.windows[self.focused_window]
        window.clear()
        if window in self.mode_buffers and mode in self.mode_buffers[window]:
            buffer_content = self.mode_buffers[window][mode]
            for y, line in enumerate(buffer_content):
                for x, (char, attrs) in enumerate(line):
                    try:
                        window.addch(y, x, ord(char), attrs)
                    except curses.error:
                        break
        window.refresh()

    def clear_current_buffer(self):
        window = self.windows[self.focused_window]
        window.clear()
        window.refresh()
        if window in self.mode_buffers:
            self.mode_buffers[window][self.current_mode] = []


    def setup_colors(self):
        curses.start_color()
        for idx, (name, fg, bg) in enumerate(self.palette):
            curses.init_pair(idx + 1, getattr(curses, fg.upper()), getattr(curses, bg.upper()))
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Focused window color


    def setup_windows(self, stdscr):
        stdscr.clear()
        self.main_window = stdscr.subwin(curses.LINES - 1, curses.COLS, 1, 0)
        self.mode_line_window = stdscr.subwin(1, curses.COLS, 0, 0)
        self.mode_line_window.bkgd(curses.color_pair(1))
        self.main_window.refresh()
        self.mode_line_window.refresh()
        self.windows.append(self.main_window)
        self._setup_cursors()
        self._initialize_buffers()
        self.highlight_focused_window()

    def _setup_cursors(self):
        self.cursors = [NodeCursor(window) for window in self.windows]
        if self.cursors:
            self.current_cursor = self.cursors[self.focused_window]
        else:
            self.current_cursor = None

    def cycle_focus(self):
        if self.current_cursor:
            self.current_cursor.clear_cursor()
        self.focused_window = (self.focused_window + 1) % len(self.windows)
        self.current_cursor = self.cursors[self.focused_window]
        self.highlight_focused_window()
        self._restore_buffer(self.current_mode)
        self.current_cursor.move_absolute(1, 0)
        self.current_cursor.render()

    def highlight_focused_window(self):
        for idx, window in enumerate(self.windows):
            color_pair = curses.color_pair(3 if idx == self.focused_window else 2)
            window.bkgd(' ', color_pair)
            window.refresh()

    @log_timing
    def update_mode_line(self, stdscr):
        logging.debug('Starting mode line update')
        mode_line_content = self.mode_line.text
        self.mode_line_window.clear()
        self.mode_line_window.addstr(0, 0, mode_line_content)
        self.mode_line_window.refresh()

    def move_cursor(self):
        if not self.current_cursor:
            return
        window = self.windows[self.focused_window]
        height, width = window.getmaxyx()
        self.current_cursor.max_y = height - 1
        self.current_cursor.max_x = width - 1
        self.current_cursor.render()

    def handle_mode_switch(self, key):
        key_name = curses.keyname(key).decode('utf-8')
        
        if key_name == ' ':
            self.space_pressed = True
            return True
            
        if not self.space_pressed:
            return False
            
        self.space_pressed = False
        
        mode_keys = {
            'n': Mode.NODE,
            'p': Mode.PARM,
            'g': Mode.GLOBAL,
            'f': Mode.FILE,
            'h': Mode.HELP,
            'k': Mode.KEYMAP,
            't': Mode.STATUS
        }
        
        if key_name in mode_keys:
            old_mode = self.current_mode
            self._save_current_buffer()
            self.clear_current_buffer()
            self.current_mode = mode_keys[key_name]
            self._restore_buffer(self.current_mode)
            self.dispatcher.dispatch(Event.MODE_CHANGE, self.current_mode)
            
            if self.current_mode == Mode.HELP:
                self.load_help_file()
            elif self.current_mode == Mode.NODE:
                self.setup_test_nodes()
            
            self.debug_info = f"Switched from {old_mode.value} to {self.current_mode.value}"
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)
            return True
            
        return False
    
    @log_timing
    def handle_keypress(self, stdscr, key):
        logging.debug(f'Starting keypress handler with key: {key}')
        # Simplified keypress handling
        if key == 27 and self.editor_state == EditorState.INSERT:  # ESC in INSERT mode
            self.state_manager.transition_to(EditorState.NORMAL)
            return
            
        handlers = {
            EditorState.WINDOW: self._handle_window_state,
            EditorState.INSERT: self._handle_insert_state,
            EditorState.NORMAL: self._handle_normal_state
        }
        
        handler = handlers.get(self.editor_state)
        if handler:
            handler(key, stdscr)
            
        self.update_mode_line(stdscr)

    def exit_insert_mode(self):
        self.editor_state = EditorState.NORMAL
        self.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, self.editor_state)
        self.debug_info = "Exited Insert Mode"
        self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)

    @log_timing
    def handle_insert_mode(self, key):
        logging.debug('Entering insert mode handler')
        window = self.windows[self.focused_window]
        if key == 10:  # Enter key
            window.addstr("\n")
        elif key == 127:  # Backspace key
            window.addstr(" ")  # Basic implementation for backspace
        else:
            window.addstr(chr(key) if key < 256 else "")
        window.refresh()

    def _handle_normal_state(self, key, stdscr):
        if not self.handle_mode_switch(key):
            if key == ord('i'):
                self.state_manager.transition_to(EditorState.INSERT)
            elif key == 23:  # Ctrl+w
                self.state_manager.transition_to(EditorState.WINDOW)
            elif self.current_cursor:
                self.current_cursor.handle_key(key)

    def _handle_insert_state(self, key, stdscr):
        if self.current_cursor and not self.current_cursor.handle_key(key):
            self.handle_insert_mode(key)

    def _handle_window_state(self, key, stdscr):
        if key == 27:  # ESC
            self.state_manager.transition_to(EditorState.NORMAL)
        else:
            self.handle_window_mode(key, stdscr)

    @log_timing
    def exit_insert_mode(self):
        logging.debug('Starting exit from insert mode')
        self.editor_state = EditorState.NORMAL
        self.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, self.editor_state)
        self.debug_info = "Exited Insert Mode"
        self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)
        logging.debug('Finished exit from insert mode')

    def handle_normal_mode(self, key):
        if key == ord('i'):
            self.editor_state = EditorState.INSERT
            self.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, self.editor_state)
            self.debug_info = "Entered Insert Mode"
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)
        elif key == 23:  # Ctrl+w
            self.editor_state = EditorState.WINDOW
            self.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, self.editor_state)
            self.debug_info = "Entered WINDOW Mode"
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)

    def handle_window_mode(self, key, stdscr):
        if key == ord('s'):
            self.split_window(stdscr, 'horizontal')
        elif key == ord('v'):
            self.split_window(stdscr, 'vertical')
        elif key == ord('w'):
            self.cycle_focus()
        elif key == 27:  # Escape key
            self.editor_state = EditorState.NORMAL
            self.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, self.editor_state)
            self.debug_info = "Exited WINDOW Mode"
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)

        self.debug_info = f"Key pressed in WINDOW mode: {chr(key) if key < 256 else key}"
        self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)

    def split_window(self, stdscr, orientation):
        height, width = stdscr.getmaxyx()
        current_window = self.windows[self.focused_window]
        current_height, current_width = current_window.getmaxyx()
        begin_y, begin_x = current_window.getbegyx()
        
        modeline_offset = 1 if begin_y == 1 else 0
        
        if orientation == 'horizontal':
            if current_height > 6:
                new_height = current_height // 2
                try:
                    current_window.resize(new_height, current_width)
                    
                    gutter = stdscr.subwin(1, current_width, begin_y + new_height, begin_x)
                    gutter.bkgd(' ', curses.A_REVERSE)
                    gutter.refresh()
                    
                    new_window = stdscr.subwin(
                        current_height - new_height - modeline_offset,
                        current_width,
                        begin_y + new_height + 1,
                        begin_x
                    )
                    self.windows.append(new_window)
                    self._initialize_buffers()
                except curses.error:
                    return
        
        elif orientation == 'vertical':
            if current_width > 10:
                new_width = current_width // 2
                try:
                    current_window.resize(current_height, new_width)
                    
                    gutter = stdscr.subwin(current_height, 1, begin_y, begin_x + new_width)
                    gutter.bkgd(' ', curses.A_REVERSE)
                    gutter.refresh()
                    
                    new_window = stdscr.subwin(
                        current_height - modeline_offset,
                        current_width - new_width - 1,
                        begin_y,
                        begin_x + new_width + 1
                    )
                    self.windows.append(new_window)
                    self._initialize_buffers()
                except curses.error:
                    return

        if len(self.windows) > self.focused_window + 1:
            new_cursor = NodeCursor(self.windows[-1])
            self.cursors.append(new_cursor)
            self.current_cursor = new_cursor
        
        self.highlight_focused_window()
        self.cursor_y = 1
        self.cursor_x = 1
        self.move_cursor()
        
        self.dispatcher.dispatch(Event.WINDOW_SPLIT, None)
        self.update_mode_line(stdscr)

    def resize_windows(self, stdscr):
        for win in self.windows:
            win.clear()
            win.refresh()
        self.update_mode_line(stdscr)

    def load_help_file(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        help_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'help.md')
        
        try:
            with open(help_path, 'r') as f:
                content = f.read()
                window = self.windows[self.focused_window]
                window.clear()
                
                y = 0
                for line in content.split('\n'):
                    try:
                        window.addstr(y, 0, line)
                        y += 1
                    except curses.error:
                        break
                        
                window.refresh()
        except FileNotFoundError:
            self.debug_info = f"help.md not found at {help_path}"
            self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)


    def setup_test_nodes(self):
        window = self.windows[self.focused_window]
        
        # Level 0 nodes (Cities)
        cities = [
            (2, 2, "Tokyo"),
            (4, 2, "Paris"),
            (6, 2, "London"),
            (8, 2, "New York")
        ]
        
        # Level 1 nodes (Foods)
        foods = [
            (2, 15, "Ramen"),
            (4, 15, "Baguette"),
            (6, 15, "Tea"),
            (8, 15, "Pizza")
        ]
        
        # Level 2 nodes (Restaurants)
        restaurants = [
            (2, 30, "Ichiran"),
            (4, 30, "Le Cheval d'Or"),
            (6, 30, "The Wolseley"),
            (8, 30, "Grimaldi's")
        ]
        
        # Add all nodes to the window and register them
        for y, x, text in cities:
            try:
                window.addstr(y, x, text)
                self.current_cursor.register_node(y, x, 0, len(text))
            except curses.error:
                pass
                
        for y, x, text in foods:
            try:
                window.addstr(y, x, text)
                self.current_cursor.register_node(y, x, 1, len(text))
            except curses.error:
                pass
                
        for y, x, text in restaurants:
            try:
                window.addstr(y, x, text)
                self.current_cursor.register_node(y, x, 2, len(text))
            except curses.error:
                pass
                
        # Draw some connecting lines
        for y in range(2, 9, 2):
            try:
                window.addstr(y, 12, "──")
                window.addstr(y, 25, "──")
            except curses.error:
                pass
        
        window.refresh()
        
        # Set initial cursor position
        self.current_cursor.move_absolute(2, 2)

    def run(self, stdscr):
        curses.curs_set(0)
        self.setup_colors()
        self.setup_windows(stdscr)
        self.highlight_focused_window()
        self.setup_test_nodes()
        
        # Initial mode dispatch
        self.dispatcher.dispatch(Event.MODE_CHANGE, self.current_mode)
        self.debug_info = f"Started in {self.current_mode.value} mode"
        self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)

        while True:
            self.update_mode_line(stdscr)
            key = stdscr.getch()
            self.handle_keypress(stdscr, key)

def main(stdscr):
    setup_debug_logging()
    editor = Editor()
    editor.initialize(stdscr)
    editor.run(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
