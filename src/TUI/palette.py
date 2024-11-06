# palette.py
import curses

def initialize_colors():
    """Initialize all color pairs used in the application"""
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Modeline
    curses.init_pair(2, curses.COLOR_BLACK, 230)                 # Active window
    curses.init_pair(3, 248, 238)                               # Inactive window
    curses.init_pair(4, 231, curses.COLOR_BLACK)                # Cursor highlight
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLACK) # Gutters

# Color pair constants
MODELINE = 1
ACTIVE_WINDOW = 2
INACTIVE_WINDOW = 3
CURSOR_HIGHLIGHT = 4
GUTTER = 5