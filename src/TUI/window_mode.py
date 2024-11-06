import curses
import logging
import time
from functools import wraps
from palette import initialize_colors, MODELINE, ACTIVE_WINDOW, INACTIVE_WINDOW, GUTTER
from events import Event

def log_timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logging.debug(f'{func.__name__}: {(end - start) * 1000:.2f}ms')
        return result
    return wrapper

class WindowMode:
    def __init__(self, editor):
        self.editor = editor
        self.stdscr = None
        self.MIN_HEIGHT = 2
        self.MIN_WIDTH = 10

    def initialize(self, stdscr):
        self.stdscr = stdscr

    def _get_stdscr(self):
        return self.stdscr

    @log_timing
    def cycle_focus(self):
        if not self.editor.windows:
            return
            
        if self.editor.current_cursor:
            self.editor.current_cursor.clear_cursor()
            
        self.editor.focused_window = (self.editor.focused_window + 1) % len(self.editor.windows)
        self.editor.current_cursor = self.editor.cursors[self.editor.focused_window]
        self.editor.highlight_focused_window()
        self.editor._restore_buffer(self.editor.current_mode)
        self.editor.current_cursor.move_absolute(1, 0)
        self.editor.current_cursor.render()

    @log_timing
    def handle_key(self, key, stdscr):
        if self.stdscr is None:
            self.stdscr = stdscr
            
        key_name = curses.keyname(key).decode('utf-8') if key != ord('=') else '='
        
        match key_name:
            case 's':
                self.split_window(self.stdscr, 'horizontal')
            case 'v':
                self.split_window(self.stdscr, 'vertical')
            case 'w':
                self.cycle_focus()
            case 'q' | 'c':
                self.close_window()
            case '=':
                self.equalize_windows()
            case '_':
                self.maximize_window('height')
            case '|':
                self.maximize_window('width')
            case '+':
                self.resize_window('height', 1)
            case '-':
                self.resize_window('height', -1)
            case '>':
                self.resize_window('width', 1)
            case '<':
                self.resize_window('width', -1)

    def _get_adjacent_windows(self, window, dimension='width'):
        y, x = window.getbegyx()
        height, width = window.getmaxyx()
        adjacent = []
        
        for other in self.editor.windows:
            if other is window:
                continue
                
            other_y, other_x = other.getbegyx()
            other_height, other_width = other.getmaxyx()
            
            if dimension == 'width':
                if other_y == y:
                    if other_x == x + width + 1:
                        adjacent.append(('right', other))
                    elif x == other_x + other_width + 1:
                        adjacent.append(('left', other))
            else:
                if other_x == x:
                    if other_y == y + height + 1:
                        adjacent.append(('below', other))
                    elif y == other_y + other_height + 1:
                        adjacent.append(('above', other))
                        
        return adjacent

    def resize_window(self, dimension, delta):
        if not self.editor.windows:
            return
            
        current = self.editor.windows[self.editor.focused_window]
        y, x = current.getbegyx()
        height, width = current.getmaxyx()
        adjacent = self._get_adjacent_windows(current, dimension)
        
        try:
            if dimension == 'width':
                if x == 0 and delta < 0:  # Left edge
                    return
                if x + width >= curses.COLS - 1 and delta > 0:  # Right edge
                    return
                    
                new_width = width + delta
                if new_width < self.MIN_WIDTH:
                    return
                    
                current.resize(height, new_width)
                
                for direction, window in adjacent:
                    win_y, win_x = window.getbegyx()
                    win_height, win_width = window.getmaxyx()
                    
                    if direction == 'right':
                        if win_width - delta >= self.MIN_WIDTH:
                            window.mvwin(win_y, win_x + delta)
                            window.resize(win_height, win_width - delta)
                    elif direction == 'left':
                        if win_width - delta >= self.MIN_WIDTH:
                            window.resize(win_height, win_width - delta)
                            current.mvwin(y, x - delta)
                
            else:  # height
                if y == 0 and delta < 0:  # Top edge
                    return
                if y + height >= curses.LINES - 2 and delta > 0:  # Bottom edge
                    return
                    
                new_height = height + delta
                if new_height < self.MIN_HEIGHT:
                    return
                    
                current.resize(new_height, width)
                
                for direction, window in adjacent:
                    win_y, win_x = window.getbegyx()
                    win_height, win_width = window.getmaxyx()
                    
                    if direction == 'below':
                        if win_height - delta >= self.MIN_HEIGHT:
                            window.mvwin(win_y + delta, win_x)
                            window.resize(win_height - delta, win_width)
                    elif direction == 'above':
                        if win_height - delta >= self.MIN_HEIGHT:
                            window.resize(win_height - delta, win_width)
                            current.mvwin(y - delta, x)
            
            for window in self.editor.windows:
                window.refresh()
                
            self._redraw_gutters()
            
        except curses.error as e:
            logging.debug(f"Resize failed: {str(e)}")
            return

    def _redraw_gutters(self):
        try:
            for window in self.editor.windows:
                y, x = window.getbegyx()
                height, width = window.getmaxyx()
                
                is_rightmost = x + width >= curses.COLS - 1
                is_bottommost = y + height >= curses.LINES - 2
                
                if not is_rightmost:
                    for i in range(height):
                        self.stdscr.addch(y + i, x + width, curses.ACS_VLINE)
                        
                if not is_bottommost:
                    for i in range(width):
                        self.stdscr.addch(y + height, x + i, curses.ACS_HLINE)
                        
            self.stdscr.refresh()
        except curses.error:
            pass

    def split_window(self, stdscr, orientation):
        if not self.editor.windows:
            return
            
        current = self.editor.windows[self.editor.focused_window]
        y, x = current.getbegyx()
        height, width = current.getmaxyx()
        
        try:
            if orientation == 'horizontal' and height > self.MIN_HEIGHT * 2:
                new_height = height // 2
                current.resize(new_height, width)
                
                gutter = stdscr.subwin(1, width, y + new_height, x)
                gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                
                new_win = stdscr.subwin(
                    height - new_height - 1,
                    width,
                    y + new_height + 1,
                    x
                )
                new_win.bkgd(' ', curses.color_pair(INACTIVE_WINDOW))
                
                self.editor.windows.append(new_win)
                new_cursor = self.editor.cursor_class(new_win)
                self.editor.cursors.append(new_cursor)
                self.editor.current_cursor = new_cursor
                
            elif orientation == 'vertical' and width > self.MIN_WIDTH * 2:
                new_width = width // 2
                current.resize(height, new_width)
                
                gutter = stdscr.subwin(height, 1, y, x + new_width)
                gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                
                new_win = stdscr.subwin(
                    height,
                    width - new_width - 1,
                    y,
                    x + new_width + 1
                )
                new_win.bkgd(' ', curses.color_pair(INACTIVE_WINDOW))
                
                self.editor.windows.append(new_win)
                new_cursor = self.editor.cursor_class(new_win)
                self.editor.cursors.append(new_cursor)
                self.editor.current_cursor = new_cursor
                
            self._redraw_gutters()
            self.editor.highlight_focused_window()
            self.editor.dispatcher.dispatch(Event.WINDOW_SPLIT, None)
            
        except curses.error:
            return

    def close_window(self):
        if len(self.editor.windows) <= 1:
            return
            
        current = self.editor.windows[self.editor.focused_window]
        y, x = current.getbegyx()
        height, width = current.getmaxyx()
        
        try:
            adjacent = (
                self._get_adjacent_windows(current, 'width') +
                self._get_adjacent_windows(current, 'height')
            )
            
            if adjacent:
                direction, window = adjacent[0]
                win_y, win_x = window.getbegyx()
                win_height, win_width = window.getmaxyx()
                
                if direction in ('right', 'left'):
                    new_width = win_width + width + 1
                    if direction == 'right':
                        window.mvwin(win_y, x)
                    window.resize(win_height, new_width)
                else:
                    new_height = win_height + height + 1
                    if direction == 'below':
                        window.mvwin(y, win_x)
                    window.resize(new_height, win_width)
                    
            self.editor.windows.pop(self.editor.focused_window)
            self.editor.cursors.pop(self.editor.focused_window)
            self.editor.focused_window = max(0, self.editor.focused_window - 1)
            self.editor.current_cursor = self.editor.cursors[self.editor.focused_window]
            
            self._redraw_gutters()
            self.editor.highlight_focused_window()
            self.editor.dispatcher.dispatch(Event.WINDOW_CLOSE, None)
            
        except curses.error:
            return

    def maximize_window(self, dimension):
        if not self.editor.windows:
            return
            
        current = self.editor.windows[self.editor.focused_window]
        y, x = current.getbegyx()
        height, width = current.getmaxyx()
        
        try:
            if dimension == 'height':
                max_height = curses.LINES - 2
                current.resize(max_height, width)
                
                for window in self.editor.windows:
                    if window != current and window.getbegyx()[1] == x:
                        win_height, win_width = window.getmaxyx()
                        window.resize(self.MIN_HEIGHT, win_width)
                        
            else:
                current.resize(height, curses.COLS)
                
                for window in self.editor.windows:
                    if window != current and window.getbegyx()[0] == y:
                        win_height, win_width = window.getmaxyx()
                        window.resize(win_height, self.MIN_WIDTH)
                        
            self._redraw_gutters()
            self.editor.highlight_focused_window()
            
        except curses.error:
            return

    def equalize_windows(self):
        if not self.editor.windows:
            return
            
        try:
            rows = {}
            for window in self.editor.windows:
                y = window.getbegyx()[0]
                if y not in rows:
                    rows[y] = []
                rows[y].append(window)
                
            total_height = curses.LINES - 2
            row_height = total_height // len(rows)
            
            for y, windows in rows.items():
                col_width = (curses.COLS - len(windows) + 1) // len(windows)
                x = 0
                
                for i, window in enumerate(windows):
                    if i == len(windows) - 1:
                        width = curses.COLS - x
                    else:
                        width = col_width
                        
                    window.mvwin(y, x)
                    window.resize(row_height, width)
                    x += width + 1
                    
            self._redraw_gutters()
            self.editor.highlight_focused_window()
            
        except curses.error:
            return