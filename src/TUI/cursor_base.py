from enum import Enum, auto
import curses
import os

class CursorStyle(Enum):
    BLOCK = auto()
    VERTICAL = auto()
    HIDDEN = auto()

class CursorManager:
    def __init__(self, window):
        self.window = window
        self.x = 0
        self.y = 0
        self.max_x = curses.COLS * 2
        self.max_y = curses.LINES * 2
        self.scroll_x = 0
        self.scroll_y = 0
        self.style = CursorStyle.BLOCK
        self._setup_colors()
        
    def _setup_colors(self):
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.highlight_pair = curses.color_pair(10)
        self.normal_pair = curses.color_pair(11)
    
    def set_style(self, style: CursorStyle):
        self.style = style
        self.render()
    
    def get_window_relative_pos(self):
        return (
            self.y - self.scroll_y,
            self.x - self.scroll_x
        )
    
    def is_visible(self):
        rel_y, rel_x = self.get_window_relative_pos()
        height, width = self.window.getmaxyx()
        return 0 <= rel_y < height and 0 <= rel_x < width
    
    def handle_key(self, key):
        key_name = curses.keyname(key).decode('utf-8')
        
        moves = {
            'KEY_UP': (-1, 0),
            'KEY_DOWN': (1, 0),
            'KEY_LEFT': (0, -1),
            'KEY_RIGHT': (0, 1),
            'k': (-1, 0),
            'j': (1, 0),
            'h': (0, -1),
            'l': (0, 1),
            'w': (-1, 0),
            's': (1, 0),
            'a': (0, -1),
            'd': (0, 1),
        }
        
        if key_name in moves:
            dy, dx = moves[key_name]
            self.move_relative(dy, dx)
            return True
        return False

    def move_relative(self, dy, dx):
        new_y = max(0, min(self.y + dy, self.max_y))
        new_x = max(0, min(self.x + dx, self.max_x))
        
        if new_y != self.y or new_x != self.x:
            self.y, self.x = new_y, new_x
            self._handle_scroll()
            self.render()
    
    def move_absolute(self, y, x):
        self.y = max(0, min(y, self.max_y))
        self.x = max(0, min(x, self.max_x))
        self._handle_scroll()
        self.render()
    
    def _handle_scroll(self):
        height, width = self.window.getmaxyx()
        margin = 5
        
        if self.x - self.scroll_x > width - margin:
            self.scroll_x = self.x - width + margin
        elif self.x - self.scroll_x < margin:
            self.scroll_x = max(0, self.x - margin)
            
        if self.y - self.scroll_y > height - margin:
            self.scroll_y = self.y - height + margin
        elif self.y - self.scroll_y < margin:
            self.scroll_y = max(0, self.y - margin)
    
    def render(self):
        if not self.is_visible():
            return
            
        rel_y, rel_x = self.get_window_relative_pos()
        try:
            char = self.window.inch(rel_y, rel_x)
            char_str = chr(char & curses.A_CHARTEXT)
            
            if self.style == CursorStyle.BLOCK:
                self.window.addstr(rel_y, rel_x, char_str, self.highlight_pair)
            elif self.style == CursorStyle.VERTICAL:
                if rel_x < self.window.getmaxyx()[1] - 1:
                    self.window.addch(rel_y, rel_x, curses.ACS_VLINE)
            
            self.window.refresh()
        except curses.error:
            pass

    def clear_cursor(self):
        if not self.is_visible():
            return
            
        rel_y, rel_x = self.get_window_relative_pos()
        try:
            char = self.window.inch(rel_y, rel_x)
            char_str = chr(char & curses.A_CHARTEXT)
            self.window.addstr(rel_y, rel_x, char_str, self.normal_pair)
            self.window.refresh()
        except curses.error:
            pass

class NodeCursor(CursorManager):
    def __init__(self, window):
        super().__init__(window)
        self.current_level = 0
        self.nodes_by_level = {}
        self.style = CursorStyle.BLOCK
        self.current_highlighted_node = None
    
    def register_node(self, y, x, level, node_length):
        if level not in self.nodes_by_level:
            self.nodes_by_level[level] = []
        self.nodes_by_level[level].append((y, x, node_length))
        self.nodes_by_level[level].sort()
    
    def clear_nodes(self):
        self.nodes_by_level.clear()
        self.clear_highlight()
    
    def find_node_at_position(self, y, x):
        for level, nodes in self.nodes_by_level.items():
            for node_y, node_x, length in nodes:
                if node_y == y and node_x <= x < node_x + length:
                    return level, (node_y, node_x, length)
        return None, None
    
    def find_nearest_node(self, y, x, level):
        if level not in self.nodes_by_level or not self.nodes_by_level[level]:
            return None
        nodes = self.nodes_by_level[level]
        return min(nodes, key=lambda n: abs(n[0] - y) + abs(n[1] - x))
    
    def clear_highlight(self):
        if self.current_highlighted_node:
            y, x, length = self.current_highlighted_node
            rel_y = y - self.scroll_y
            rel_x = x - self.scroll_x
            try:
                for i in range(length):
                    char = self.window.inch(rel_y, rel_x + i)
                    char_str = chr(char & curses.A_CHARTEXT)
                    self.window.addstr(rel_y, rel_x + i, char_str, self.normal_pair)
            except curses.error:
                pass
            self.current_highlighted_node = None
            self.window.refresh()
    
    def highlight_current_node(self):
        level, node_info = self.find_node_at_position(self.y, self.x)
        if node_info:
            if self.current_highlighted_node != node_info:
                self.clear_highlight()
                y, x, length = node_info
                rel_y = y - self.scroll_y
                rel_x = x - self.scroll_x
                try:
                    for i in range(length):
                        char = self.window.inch(rel_y, rel_x + i)
                        char_str = chr(char & curses.A_CHARTEXT)
                        self.window.addstr(rel_y, rel_x + i, char_str, self.highlight_pair)
                except curses.error:
                    pass
                self.current_highlighted_node = node_info
                self.window.refresh()
        else:
            self.clear_highlight()
    
    def handle_key(self, key):
        key_name = curses.keyname(key).decode('utf-8')
        
        if key_name in ['KEY_LEFT', 'h', 'a']:
            self._move_left()
            return True
        elif key_name in ['KEY_RIGHT', 'l', 'd']:
            self._move_right()
            return True
        elif key_name in ['KEY_UP', 'k', 'w']:
            self._move_up()
            return True
        elif key_name in ['KEY_DOWN', 'j', 's']:
            self._move_down()
            return True
            
        return False
    
    def _move_left(self):
        if self.current_level > 0:
            self.current_level -= 1
            nearest = self.find_nearest_node(self.y, self.x, self.current_level)
            if nearest:
                self.move_absolute(nearest[0], nearest[1])
                self.highlight_current_node()
    
    def _move_right(self):
        if self.current_level + 1 in self.nodes_by_level:
            self.current_level += 1
            nearest = self.find_nearest_node(self.y, self.x, self.current_level)
            if nearest:
                self.move_absolute(nearest[0], nearest[1])
                self.highlight_current_node()
    
    def _move_up(self):
        current_nodes = self.nodes_by_level.get(self.current_level, [])
        current_pos = None
        for i, (y, x, _) in enumerate(current_nodes):
            if y == self.y and x == self.x:
                current_pos = i
                break
                
        if current_pos is not None and current_pos > 0:
            y, x, _ = current_nodes[current_pos - 1]
            self.move_absolute(y, x)
            self.highlight_current_node()
    
    def _move_down(self):
        current_nodes = self.nodes_by_level.get(self.current_level, [])
        current_pos = None
        for i, (y, x, _) in enumerate(current_nodes):
            if y == self.y and x == self.x:
                current_pos = i
                break
                
        if current_pos is not None and current_pos < len(current_nodes) - 1:
            y, x, _ = current_nodes[current_pos + 1]
            self.move_absolute(y, x)
            self.highlight_current_node()