import curses
from enum import Enum
from typing import Optional, List, Dict, Tuple
from events import Event
from palette import MODELINE, ACTIVE_WINDOW, INACTIVE_WINDOW, GUTTER

class SplitType(Enum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'

class Frame:
    def __init__(self, window=None, split_type=None):
        self.window = window
        self.parent = None
        self.left = None
        self.right = None
        self.split_type = split_type
        self.MIN_GUTTER = 1
        self.MIN_SIZE = 3

    def validate_tree(self) -> list[str]:
        validation_errors = []
        
        if not self.window and not (self.left and self.right):
            validation_errors.append("Invalid frame: missing both window and children")
            
        if self.window and (self.left or self.right):
            validation_errors.append("Invalid frame: contains both window and children")
            
        if self.left and not isinstance(self.left, Frame):
            validation_errors.append("Invalid left child type")
            
        if self.right and not isinstance(self.right, Frame):
            validation_errors.append("Invalid right child type")
            
        if (self.left or self.right) and not self.split_type:
            validation_errors.append("Split frames must have split_type")
            
        if self.left:
            if self.left.parent is not self:
                validation_errors.append("Invalid left child parent reference")
            validation_errors.extend(self.left.validate_tree())
            
        if self.right:
            if self.right.parent is not self:
                validation_errors.append("Invalid right child parent reference")
            validation_errors.extend(self.right.validate_tree())
            
        return validation_errors

    def redistribute_space(self, y: int, x: int, height: int, width: int) -> bool:
        if height < self.MIN_SIZE or width < self.MIN_SIZE:
            return False

        if self.window:
            try:
                self.window.mvwin(y, x)
                self.window.resize(height, width)
                return True
            except curses.error:
                return False

        if not (self.left and self.right and self.split_type):
            return False

        gutter_space = self.MIN_GUTTER

        if self.split_type == SplitType.HORIZONTAL:
            left_height = (height - gutter_space) // 2
            right_height = height - left_height - gutter_space
            
            if left_height < self.MIN_SIZE or right_height < self.MIN_SIZE:
                return False
                
            return (self.left.redistribute_space(y, x, left_height, width) and
                   self.right.redistribute_space(y + left_height + gutter_space, x, right_height, width))

        if self.split_type == SplitType.VERTICAL:
            left_width = (width - gutter_space) // 2
            right_width = width - left_width - gutter_space
            
            if left_width < self.MIN_SIZE or right_width < self.MIN_SIZE:
                return False
                
            return (self.left.redistribute_space(y, x, height, left_width) and
                   self.right.redistribute_space(y, x + left_width + gutter_space, height, right_width))

        return False

    def collect_dimensions(self) -> list[tuple]:
        dimensions = []
        if self.window:
            y, x = self.window.getbegyx()
            height, width = self.window.getmaxyx()
            dimensions.append((self.window, y, x, height, width))
        if self.left:
            dimensions.extend(self.left.collect_dimensions())
        if self.right:
            dimensions.extend(self.right.collect_dimensions())
        return dimensions

    def find_frame_by_window(self, target_window) -> Optional['Frame']:
        if self.window == target_window:
            return self
            
        for child in (self.left, self.right):
            if child:
                found = child.find_frame_by_window(target_window)
                if found:
                    return found
        return None

    def get_sibling(self) -> Optional['Frame']:
        if not self.parent:
            return None
        return self.parent.right if self.parent.left is self else self.parent.left

    def ensure_consistent_tree(self) -> bool:
        validation_errors = self.validate_tree()
        if validation_errors:
            self._repair_tree()
        return not self.validate_tree()

    def _repair_tree(self):
        if self.window and (self.left or self.right):
            self.left = None
            self.right = None
            
        if not self.window and not (self.left and self.right):
            if self.left and not self.right:
                self.window = self.left.window
                self.left = None
            elif self.right and not self.left:
                self.window = self.right.window
                self.right = None
                
        for child in (self.left, self.right):
            if child:
                child.parent = self
                child._repair_tree()

    def get_root(self) -> 'Frame':
        current = self
        while current.parent:
            current = current.parent
        return current

    def is_leaf(self) -> bool:
        return bool(self.window)

    def get_available_space(self) -> tuple[int, int]:
        if not self.window:
            return 0, 0
        height, width = self.window.getmaxyx()
        return height, width







class WindowMode:
    def __init__(self, editor):
        self.editor = editor
        self.stdscr = None
        self.MIN_HEIGHT = 3
        self.MIN_WIDTH = 10
        self.GUTTER_SIZE = 1
        self.root_frame = None
        self._last_layout = None
        self._resize_lock = False

    def initialize(self, stdscr):
        self.stdscr = stdscr
        if self.editor.windows:
            self.root_frame = Frame(self.editor.windows[0])
            self._update_layout_state()

    def split_window(self, split_type: SplitType) -> bool:
        if not self.editor.windows:
            return False

        current_window = self.editor.windows[self.editor.focused_window]
        current_frame = self.root_frame.find_frame_by_window(current_window)
        
        if not current_frame:
            return False

        y, x = current_window.getbegyx()
        height, width = current_window.getmaxyx()
        
        min_size = self.MIN_HEIGHT if split_type == SplitType.HORIZONTAL else self.MIN_WIDTH
        total_space = height if split_type == SplitType.HORIZONTAL else width
        
        if total_space < (min_size * 2 + self.GUTTER_SIZE):
            return False

        try:
            if split_type == SplitType.HORIZONTAL:
                new_height = (height - self.GUTTER_SIZE) // 2
                remaining_height = height - new_height - self.GUTTER_SIZE
                current_window.resize(new_height, width)
                new_window = curses.newwin(remaining_height, width, 
                                         y + new_height + self.GUTTER_SIZE, x)
            else:
                new_width = (width - self.GUTTER_SIZE) // 2
                remaining_width = width - new_width - self.GUTTER_SIZE
                current_window.resize(height, new_width)
                new_window = curses.newwin(height, remaining_width,
                                         y, x + new_width + self.GUTTER_SIZE)

            self._setup_new_window(new_window, current_frame, split_type)
            self._update_layout_state()
            return True

        except curses.error:
            self._restore_layout()
            return False

    def close_window(self) -> bool:
        if len(self.editor.windows) <= 1:
            return False

        current_window = self.editor.windows[self.editor.focused_window]
        current_frame = self.root_frame.find_frame_by_window(current_window)
        
        if not current_frame or not current_frame.parent:
            return False

        try:
            sibling_frame = current_frame.get_sibling()
            if not sibling_frame:
                return False

            self._save_layout_state()
            
            parent_frame = current_frame.parent
            grandparent = parent_frame.parent

            if grandparent:
                if grandparent.left == parent_frame:
                    grandparent.left = sibling_frame
                else:
                    grandparent.right = sibling_frame
                sibling_frame.parent = grandparent
            else:
                self.root_frame = sibling_frame
                sibling_frame.parent = None

            window_idx = self.editor.windows.index(current_window)
            self.editor.windows.pop(window_idx)
            self.editor.cursors.pop(window_idx)

            if self.editor.focused_window >= len(self.editor.windows):
                self.editor.focused_window = len(self.editor.windows) - 1

            self._redistribute_all_space()
            self._update_current_cursor()
            
            # Clear the old window before deletion
            current_window.clear()
            current_window.refresh()
            del current_window
            
            # Full refresh sequence
            self.editor.stdscr.clear()
            self.editor.stdscr.refresh()
            
            for window in self.editor.windows:
                window.clear()
                window.refresh()
            
            self._redraw_gutters()
            self.editor.highlight_focused_window()
            
            # Ensure mode line is refreshed
            self.editor.mode_line_window.refresh()
            
            return True

        except Exception:
            self._restore_layout()
            return False

    def _setup_new_window(self, new_window, current_frame, split_type):
        new_window.bkgd(' ', curses.color_pair(INACTIVE_WINDOW))
        
        new_frame = Frame(new_window)
        current_frame.window = None
        current_frame.split_type = split_type
        current_frame.left = Frame(self.editor.windows[self.editor.focused_window])
        current_frame.right = new_frame
        
        current_frame.left.parent = current_frame
        current_frame.right.parent = current_frame
        
        self.editor.windows.append(new_window)
        new_cursor = self.editor.current_mode.cursor_class(new_window)
        self.editor.cursors.append(new_cursor)
        self.editor.current_cursor = new_cursor
        
        self._redraw_gutters()
        self.editor.highlight_focused_window()

    def _redistribute_all_space(self) -> bool:
        if not self.root_frame:
            return False
            
        screen_height, screen_width = self.stdscr.getmaxyx()
        usable_height = screen_height - 1  # Reserve space for status line
        
        return self.root_frame.redistribute_space(0, 0, usable_height, screen_width)

    def _save_layout_state(self):
        if not self.root_frame:
            return
            
        self._last_layout = [
            (window, *window.getbegyx(), *window.getmaxyx())
            for window in self.editor.windows
        ]

    def _restore_layout(self):
        if not self._last_layout:
            return False
            
        try:
            for window, y, x, height, width in self._last_layout:
                window.mvwin(y, x)
                window.resize(height, width)
            return True
        except curses.error:
            return False

    def _update_layout_state(self):
        self._save_layout_state()
        self.root_frame.ensure_consistent_tree()

    def _update_current_cursor(self):
        if self.editor.windows:
            self.editor.current_cursor = self.editor.cursors[self.editor.focused_window]
            self.editor.dispatcher.dispatch(Event.WINDOW_CHANGED, None)

    def handle_key(self, key: int, stdscr) -> None:
        if self.stdscr is None:
            self.stdscr = stdscr
            
        if key == 27 or key == 23:  # ESC or Ctrl-W
            self._exit_window_mode()
            return
            
        key_name = curses.keyname(key).decode('utf-8') if key != ord('=') else '='
        
        key_handlers = {
            's': lambda: self.split_window(SplitType.HORIZONTAL),
            'v': lambda: self.split_window(SplitType.VERTICAL),
            'w': self.cycle_focus,
            'q': self.close_window,
            'c': self.close_window,
            '=': self.equalize_windows,
            '_': lambda: self.maximize_dimension('height'),
            '|': lambda: self.maximize_dimension('width'),
            '+': lambda: self.resize_window('height', 1),
            '-': lambda: self.resize_window('height', -1),
            '>': lambda: self.resize_window('width', 1),
            '<': lambda: self.resize_window('width', -1)
        }
        
        handler = key_handlers.get(key_name)
        if handler:
            handler()
            
    def _exit_window_mode(self) -> None:
        self.editor._exit_window_mode()  # Delegate to the editor

    def resize_window(self, dimension: str, delta: int) -> bool:
        if self._resize_lock or not self.editor.windows:
            return False

        try:
            self._resize_lock = True
            current = self.editor.windows[self.editor.focused_window]
            current_frame = self.root_frame.find_frame_by_window(current)
            
            if not current_frame or not current_frame.parent:
                return False

            parent = current_frame.parent
            sibling = current_frame.get_sibling()
            
            if not sibling or not sibling.window:
                return False

            if not self._can_resize(current_frame, sibling, dimension, delta):
                return False

            self._save_layout_state()
            success = self._apply_resize(current, sibling.window, dimension, delta)
            
            if success:
                self._cascade_resize(parent, dimension)
                self._redraw_gutters()
                return True
                
            self._restore_layout()
            return False

        finally:
            self._resize_lock = False

    def maximize_dimension(self, dimension: str) -> bool:
        if not self.editor.windows:
            return False

        try:
            self._save_layout_state()
            current = self.editor.windows[self.editor.focused_window]
            current_frame = self.root_frame.find_frame_by_window(current)
            
            if not current_frame:
                return False

            screen_height, screen_width = self.stdscr.getmaxyx()
            max_height = screen_height - 1  # Reserve status line
            siblings = self._collect_siblings(current_frame, dimension)

            if dimension == 'height':
                for sibling, _ in siblings:
                    if sibling.window:
                        sibling.window.resize(self.MIN_HEIGHT, sibling.window.getmaxyx()[1])
                current.resize(max_height - (len(siblings) * (self.MIN_HEIGHT + self.GUTTER_SIZE)),
                             current.getmaxyx()[1])
            else:
                for sibling, _ in siblings:
                    if sibling.window:
                        sibling.window.resize(sibling.window.getmaxyx()[0], self.MIN_WIDTH)
                current.resize(current.getmaxyx()[0],
                             screen_width - (len(siblings) * (self.MIN_WIDTH + self.GUTTER_SIZE)))

            self._redraw_gutters()
            return True

        except curses.error:
            self._restore_layout()
            return False

    def equalize_windows(self) -> bool:
        if not self.root_frame:
            return False

        try:
            self._save_layout_state()
            screen_height, screen_width = self.stdscr.getmaxyx()
            
            def equalize_dimension(frame: Frame, available: int, dimension: str) -> bool:
                if frame.window:
                    return True
                    
                if not frame.left or not frame.right:
                    return False
                    
                space_per_child = (available - self.GUTTER_SIZE) // 2
                
                if dimension == 'height' and frame.split_type == SplitType.HORIZONTAL:
                    if not self._resize_frame_height(frame.left, space_per_child):
                        return False
                    if not self._resize_frame_height(frame.right, space_per_child):
                        return False
                        
                elif dimension == 'width' and frame.split_type == SplitType.VERTICAL:
                    if not self._resize_frame_width(frame.left, space_per_child):
                        return False
                    if not self._resize_frame_width(frame.right, space_per_child):
                        return False
                        
                return (equalize_dimension(frame.left, space_per_child, dimension) and
                        equalize_dimension(frame.right, space_per_child, dimension))

            success = (equalize_dimension(self.root_frame, screen_height - 1, 'height') and
                      equalize_dimension(self.root_frame, screen_width, 'width'))
                      
            if success:
                self._redraw_gutters()
                return True
                
            self._restore_layout()
            return False

        except curses.error:
            self._restore_layout()
            return False

    def cycle_focus(self) -> None:
        if not self.editor.windows:
            return

        if self.editor.current_cursor:
            self.editor.current_cursor.clear_cursor()

        self.editor.focused_window = (self.editor.focused_window + 1) % len(self.editor.windows)
        self.editor.current_cursor = self.editor.cursors[self.editor.focused_window]
        self.editor.highlight_focused_window()
        self.editor._restore_buffer(self.editor.current_mode)
        
        if self.editor.current_cursor:
            self.editor.current_cursor.move_absolute(1, 0)
            self.editor.current_cursor.render()

    def _redraw_gutters(self) -> None:
        try:
            screen_height, screen_width = self.stdscr.getmaxyx()
            max_height = screen_height - 1
            
            for window in self.editor.windows:
                y, x = window.getbegyx()
                height, width = window.getmaxyx()
                
                is_rightmost = x + width >= screen_width - 1
                is_bottommost = y + height >= max_height
                
                if not is_rightmost:
                    gutter = curses.newwin(height, self.GUTTER_SIZE, y, x + width)
                    gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                    gutter.refresh()
                    
                if not is_bottommost:
                    gutter = curses.newwin(self.GUTTER_SIZE, width, y + height, x)
                    gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                    gutter.refresh()
            
            self.stdscr.refresh()
            
        except curses.error:
            pass

    def _can_resize(self, frame: Frame, sibling: Frame, dimension: str, delta: int) -> bool:
        if dimension == 'height':
            current_size = frame.window.getmaxyx()[0]
            sibling_size = sibling.window.getmaxyx()[0]
        else:
            current_size = frame.window.getmaxyx()[1]
            sibling_size = sibling.window.getmaxyx()[1]

        min_size = self.MIN_HEIGHT if dimension == 'height' else self.MIN_WIDTH
        return (current_size + delta >= min_size and 
                sibling_size - delta >= min_size)

    def _apply_resize(self, current_window, sibling_window, dimension: str, delta: int) -> bool:
        try:
            if dimension == 'height':
                current_height = current_window.getmaxyx()[0]
                sibling_height = sibling_window.getmaxyx()[0]
                current_window.resize(current_height + delta, current_window.getmaxyx()[1])
                sibling_window.resize(sibling_height - delta, sibling_window.getmaxyx()[1])
            else:
                current_width = current_window.getmaxyx()[1]
                sibling_width = sibling_window.getmaxyx()[1]
                current_window.resize(current_window.getmaxyx()[0], current_width + delta)
                sibling_window.resize(sibling_window.getmaxyx()[0], sibling_width - delta)
            return True
        except curses.error:
            return False

    def _cascade_resize(self, frame: Frame, dimension: str) -> None:
        if not frame:
            return
            
        if frame.split_type == (SplitType.HORIZONTAL if dimension == 'height' else SplitType.VERTICAL):
            self._redistribute_all_space()
            
        self._cascade_resize(frame.parent, dimension)

    def _collect_siblings(self, frame: Frame, dimension: str) -> list[tuple[Frame, bool]]:
        siblings = []
        current = frame
        
        while current.parent:
            parent = current.parent
            if ((dimension == 'height' and parent.split_type == SplitType.HORIZONTAL) or
                (dimension == 'width' and parent.split_type == SplitType.VERTICAL)):
                sibling = parent.right if parent.left == current else parent.left
                siblings.append((sibling, parent.split_type))
            current = parent
            
        return siblings

    def _resize_frame_height(self, frame: Frame, height: int) -> bool:
        if frame.window:
            try:
                frame.window.resize(height, frame.window.getmaxyx()[1])
                return True
            except curses.error:
                return False
        return True

    def _resize_frame_width(self, frame: Frame, width: int) -> bool:
        if frame.window:
            try:
                frame.window.resize(frame.window.getmaxyx()[0], width)
                return True
            except curses.error:
                return False
        return True

    def _update_layout_state(self) -> None:
        self._save_layout_state()
        if self.root_frame:
            self.root_frame.ensure_consistent_tree()

    def get_window_info(self) -> list[str]:
        return [f"Window {i}: pos({window.getbegyx()}) size({window.getmaxyx()}) "
                f"{'active' if i == self.editor.focused_window else 'inactive'}"
                for i, window in enumerate(self.editor.windows)]