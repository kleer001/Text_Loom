from enum import Enum, auto
import curses
import os
from typing import Optional, Tuple, List, Dict, Set
from dataclasses import dataclass
from palette import ACTIVE_WINDOW, INACTIVE_WINDOW, CURSOR_HIGHLIGHT

class CursorStyle(Enum):
    BLOCK = auto()
    VERTICAL = auto()
    HIDDEN = auto()

@dataclass
class Node:
    y: int
    x: int
    length: int
    
    def contains_point(self, point_y: int, point_x: int) -> bool:
        return self.y == point_y and self.x <= point_x < self.x + self.length
        
    def distance_to(self, y: int, x: int) -> int:
        return abs(self.y - y) + abs(self.x - x)

class CursorManager:
    def __init__(self, window):
        self.window = window
        self.x: int = 0
        self.y: int = 0
        self.scroll_x: int = 0
        self.scroll_y: int = 0
        self.style: CursorStyle = CursorStyle.BLOCK
        self._last_render_pos: Optional[Tuple[int, int]] = None
        self._setup_bounds()
        self._setup_colors()

    def _setup_bounds(self) -> None:
        height, width = self.window.getmaxyx()
        self.max_y = height - 1
        self.max_x = width - 1

    def _setup_colors(self) -> None:
        self.highlight_pair = curses.color_pair(CURSOR_HIGHLIGHT)
        self.normal_pair = curses.color_pair(ACTIVE_WINDOW)

    def set_style(self, style: CursorStyle) -> None:
        if style != self.style:
            self.style = style
            self.render()

    def get_position(self) -> Tuple[int, int]:
        return self.y, self.x

    def get_window_relative_pos(self) -> Tuple[int, int]:
        return (self.y - self.scroll_y, self.x - self.scroll_x)

    def is_visible(self) -> bool:
        rel_y, rel_x = self.get_window_relative_pos()
        return 0 <= rel_y <= self.max_y and 0 <= rel_x <= self.max_x

    def handle_key(self, key: int) -> bool:
        key_name = curses.keyname(key).decode('utf-8')
        
        moves = {
            'KEY_UP':    (-1, 0),  'k': (-1, 0),  'w': (-1, 0),
            'KEY_DOWN':  (1, 0),   'j': (1, 0),   's': (1, 0),
            'KEY_LEFT':  (0, -1),  'h': (0, -1),  'a': (0, -1),
            'KEY_RIGHT': (0, 1),   'l': (0, 1),   'd': (0, 1),
        }
        
        if move := moves.get(key_name):
            dy, dx = move
            self.move_relative(dy, dx)
            return True
        return False

    def move_relative(self, dy: int, dx: int) -> None:
        new_y = max(0, min(self.y + dy, self.max_y))
        new_x = max(0, min(self.x + dx, self.max_x))
        
        if (new_y, new_x) != (self.y, self.x):
            self.clear_cursor()
            self.y, self.x = new_y, new_x
            self._handle_scroll()
            self.render()

    def move_absolute(self, y: int, x: int) -> None:
        if not (0 <= y <= self.max_y and 0 <= x <= self.max_x):
            return
            
        if (y, x) != (self.y, self.x):
            self.clear_cursor()
            self.y, self.x = y, x
            self._handle_scroll()
            self.render()

    def _handle_scroll(self) -> None:
        MARGIN = 5
        height, width = self.window.getmaxyx()
        
        if self.x - self.scroll_x > width - MARGIN:
            self.scroll_x = min(self.x - width + MARGIN, self.max_x - width + 1)
        elif self.x - self.scroll_x < MARGIN:
            self.scroll_x = max(0, self.x - MARGIN)
            
        if self.y - self.scroll_y > height - MARGIN:
            self.scroll_y = min(self.y - height + MARGIN, self.max_y - height + 1)
        elif self.y - self.scroll_y < MARGIN:
            self.scroll_y = max(0, self.y - MARGIN)

    def render(self) -> None:
        if not self.is_visible() or self.style == CursorStyle.HIDDEN:
            return
            
        rel_y, rel_x = self.get_window_relative_pos()
        try:
            char = self.window.inch(rel_y, rel_x)
            char_str = chr(char & curses.A_CHARTEXT)
            
            match self.style:
                case CursorStyle.BLOCK:
                    self.window.addstr(rel_y, rel_x, char_str, self.highlight_pair)
                case CursorStyle.VERTICAL:
                    if rel_x < self.max_x:
                        self.window.addch(rel_y, rel_x, curses.ACS_VLINE)
            
            self._last_render_pos = (rel_y, rel_x)
            self.window.refresh()
        except curses.error:
            pass

    def clear_cursor(self) -> None:
        if not self._last_render_pos:
            return
            
        rel_y, rel_x = self._last_render_pos
        try:
            char = self.window.inch(rel_y, rel_x)
            char_str = chr(char & curses.A_CHARTEXT)
            self.window.addstr(rel_y, rel_x, char_str, self.normal_pair)
            self.window.refresh()
            self._last_render_pos = None
        except curses.error:
            pass

class NodeCursor(CursorManager):
    def __init__(self, window):
        super().__init__(window)
        self.current_level: int = 0
        self.nodes_by_level: Dict[int, List[Node]] = {}
        self.current_highlighted: Optional[Node] = None
        self._highlighted_chars: Set[Tuple[int, int]] = set()

    def register_node(self, y: int, x: int, level: int, node_length: int) -> None:
        if level not in self.nodes_by_level:
            self.nodes_by_level[level] = []
            
        node = Node(y, x, node_length)
        self.nodes_by_level[level].append(node)
        self.nodes_by_level[level].sort(key=lambda n: (n.y, n.x))

    def clear_nodes(self) -> None:
        self.nodes_by_level.clear()
        self.clear_highlight()
        self.current_highlighted = None
        self._highlighted_chars.clear()

    def find_node_at_position(self, y: int, x: int) -> Tuple[Optional[int], Optional[Node]]:
        for level, nodes in self.nodes_by_level.items():
            for node in nodes:
                if node.contains_point(y, x):
                    return level, node
        return None, None

    def find_nearest_node(self, y: int, x: int, level: int) -> Optional[Node]:
        if level not in self.nodes_by_level:
            return None
            
        nodes = self.nodes_by_level[level]
        if not nodes:
            return None
            
        return min(nodes, key=lambda n: n.distance_to(y, x))

    def clear_highlight(self) -> None:
        if not self._highlighted_chars:
            return
            
        try:
            for rel_y, rel_x in self._highlighted_chars:
                char = self.window.inch(rel_y, rel_x)
                char_str = chr(char & curses.A_CHARTEXT)
                self.window.addstr(rel_y, rel_x, char_str, self.normal_pair)
                
            self.window.refresh()
            self._highlighted_chars.clear()
            self.current_highlighted = None
        except curses.error:
            pass

    def highlight_current_node(self) -> None:
        level, node = self.find_node_at_position(self.y, self.x)
        if not node or node == self.current_highlighted:
            return
            
        self.clear_highlight()
        rel_y = node.y - self.scroll_y
        rel_x = node.x - self.scroll_x
        
        try:
            for i in range(node.length):
                if 0 <= rel_x + i <= self.max_x:
                    char = self.window.inch(rel_y, rel_x + i)
                    char_str = chr(char & curses.A_CHARTEXT)
                    self.window.addstr(rel_y, rel_x + i, char_str, self.highlight_pair)
                    self._highlighted_chars.add((rel_y, rel_x + i))
                    
            self.window.refresh()
            self.current_highlighted = node
        except curses.error:
            pass

    def handle_key(self, key: int) -> bool:
        key_name = curses.keyname(key).decode('utf-8')
        
        handlers = {
            'KEY_LEFT':  self._move_left,   'h': self._move_left,   'a': self._move_left,
            'KEY_RIGHT': self._move_right,  'l': self._move_right,  'd': self._move_right,
            'KEY_UP':    self._move_up,     'k': self._move_up,     'w': self._move_up,
            'KEY_DOWN':  self._move_down,   'j': self._move_down,   's': self._move_down
        }
        
        if handler := handlers.get(key_name):
            handler()
            return True
        return False

    def _move_left(self) -> None:
        if self.current_level > 0:
            self.current_level -= 1
            if nearest := self.find_nearest_node(self.y, self.x, self.current_level):
                self.move_absolute(nearest.y, nearest.x)
                self.highlight_current_node()

    def _move_right(self) -> None:
        if self.current_level + 1 in self.nodes_by_level:
            self.current_level += 1
            if nearest := self.find_nearest_node(self.y, self.x, self.current_level):
                self.move_absolute(nearest.y, nearest.x)
                self.highlight_current_node()

    def _move_up(self) -> None:
        nodes = self.nodes_by_level.get(self.current_level, [])
        for i, node in enumerate(nodes):
            if node.y == self.y and node.x == self.x and i > 0:
                self.move_absolute(nodes[i-1].y, nodes[i-1].x)
                self.highlight_current_node()
                break

    def _move_down(self) -> None:
        nodes = self.nodes_by_level.get(self.current_level, [])
        for i, node in enumerate(nodes):
            if node.y == self.y and node.x == self.x and i < len(nodes) - 1:
                self.move_absolute(nodes[i+1].y, nodes[i+1].x)
                self.highlight_current_node()
                break