import curses
import enum

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

    def dispatch(self, event_type, data=None):
        for listener in self.listeners[event_type]:
            listener(data)

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

    def _handle_state_change(self, editor_state):
        self.editor_state = editor_state
        self._update_text()

    def _handle_debug_info(self, debug_info):
        self.debug_info = debug_info
        self._update_text()

    def _update_text(self):
        self.text = f"[{self.editor_state.value}] [{self.mode.value}] {self.path} ({self.buffer_name}) | Debug: {self.debug_info}"

class Editor:
    def __init__(self):
        self.current_mode = Mode.NODE
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

    def run(self, stdscr):
        curses.curs_set(1)
        self.setup_colors()
        self.setup_windows(stdscr)
        self.highlight_focused_window()

        while True:
            self.update_mode_line(stdscr)
            key = stdscr.getch()
            self.handle_keypress(stdscr, key)

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
        self.main_window.addstr(0, 0, "Welcome.")
        self.main_window.refresh()
        self.mode_line_window.refresh()
        self.windows.append(self.main_window)

    def cycle_focus(self):
        self.focused_window = (self.focused_window + 1) % len(self.windows)
        self.highlight_focused_window()
        self.cursor_y = 1
        self.cursor_x = 0
        self.move_cursor()

    def highlight_focused_window(self):
        for idx, window in enumerate(self.windows):
            if idx == self.focused_window:
                window.bkgd(curses.color_pair(3))
            else:
                window.bkgd(curses.color_pair(2))
            window.refresh()

    def update_mode_line(self, stdscr):
        mode_line_content = self.mode_line.text
        self.mode_line_window.clear()
        self.mode_line_window.addstr(0, 0, mode_line_content)
        self.mode_line_window.refresh()

    def move_cursor(self):
        window = self.windows[self.focused_window]
        height, width = window.getmaxyx()
        self.cursor_y = max(1, min(self.cursor_y, height - 2))
        self.cursor_x = max(1, min(self.cursor_x, width - 2))
        window.move(self.cursor_y, self.cursor_x)
        window.refresh()


    def handle_keypress(self, stdscr, key):
        if self.editor_state == EditorState.INSERT:
            if key == 27:  # Escape key
                self.exit_insert_mode()
            else:
                self.handle_insert_mode(key)
        elif self.editor_state == EditorState.NORMAL:
            self.handle_normal_mode(key)
        elif self.editor_state == EditorState.WINDOW:
            self.handle_window_mode(key, stdscr)

        self.update_mode_line(stdscr)

    def exit_insert_mode(self):
        self.editor_state = EditorState.NORMAL
        self.dispatcher.dispatch(Event.EDITOR_STATE_CHANGE, self.editor_state)
        self.debug_info = "Exited Insert Mode"
        self.dispatcher.dispatch(Event.DEBUG_INFO, self.debug_info)

    def handle_insert_mode(self, key):
        window = self.windows[self.focused_window]
        if key == 10:  # Enter key
            window.addstr("\n")
        elif key == 127:  # Backspace key
            window.addstr(" ")  # Basic implementation for backspace
        else:
            window.addstr(chr(key) if key < 256 else "")
        window.refresh()

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

        if orientation == 'horizontal':
            if current_height > 6:  # Ensure enough space for both windows
                new_height = current_height // 2
                try:
                    current_window.resize(new_height - 1, current_width - 2)
                    new_window = stdscr.subwin(current_height - new_height - 1, current_width - 2, 
                            current_window.getbegyx()[0] + new_height, current_window.getbegyx()[1] + 1)
                    self.windows.append(new_window)
                except curses.error:
                    return  # If resize fails, don't create a new window
        elif orientation == 'vertical':
            if current_width > 10:  # Ensure enough space for both windows
                new_width = current_width // 2
                try:
                    current_window.resize(current_height - 2, new_width - 2)
                    new_window = stdscr.subwin(current_height - 2, current_width - new_width - 2, 
                            current_window.getbegyx()[0] + 1, current_window.getbegyx()[1] + new_width)
                    self.windows.append(new_window)
                except curses.error:
                    return  # If resize fails, don't create a new window

        if len(self.windows) > self.focused_window + 1:
            self.focused_window = len(self.windows) - 1
            for idx, window in enumerate(self.windows):
                window.clear()
                window.box()
                window.addstr(0, 2, f" Window {idx + 1} ")
                window.refresh()

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

def main(stdscr):
    editor = Editor()
    editor.run(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
