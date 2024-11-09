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
        self.width = 0
        self.height = 0
        self.win_x = 0
        self.win_y = 0
        self.MIN_SIZE = 3

    def frame_new_height(self, height: int, topfirst: bool, resize_siblings: bool) -> bool:
        if height < self.MIN_SIZE:
            return False

        if self.window:
            try:
                old_height = self.height
                self.height = height
                if resize_siblings:
                    self.window.resize(height, self.window.getmaxyx()[1])
                return True
            except curses.error:
                self.height = old_height
                return False

        if not (self.left and self.right):
            return False

        if self.split_type == SplitType.HORIZONTAL:
            available = height - 1
            if topfirst:
                if not self.left.frame_new_height(available // 2, True, resize_siblings):
                    return False
                remaining = available - self.left.height
                if not self.right.frame_new_height(remaining, False, resize_siblings):
                    return False
            else:
                if not self.right.frame_new_height(available // 2, True, resize_siblings):
                    return False
                remaining = available - self.right.height
                if not self.left.frame_new_height(remaining, False, resize_siblings):
                    return False
        else:
            return (self.left.frame_new_height(height, topfirst, resize_siblings) and
                   self.right.frame_new_height(height, topfirst, resize_siblings))
        
        self.height = height
        return True

    def frame_new_width(self, width: int, leftfirst: bool, resize_siblings: bool) -> bool:
        if width < self.MIN_SIZE:
            return False

        if self.window:
            try:
                old_width = self.width
                self.width = width
                if resize_siblings:
                    self.window.resize(self.window.getmaxyx()[0], width)
                return True
            except curses.error:
                self.width = old_width
                return False

        if not (self.left and self.right):
            return False

        if self.split_type == SplitType.VERTICAL:
            available = width - 1
            if leftfirst:
                if not self.left.frame_new_width(available // 2, True, resize_siblings):
                    return False
                remaining = available - self.left.width
                if not self.right.frame_new_width(remaining, False, resize_siblings):
                    return False
            else:
                if not self.right.frame_new_width(available // 2, True, resize_siblings):
                    return False
                remaining = available - self.right.width
                if not self.left.frame_new_width(remaining, False, resize_siblings):
                    return False
        else:
            return (self.left.frame_new_width(width, leftfirst, resize_siblings) and
                   self.right.frame_new_width(width, leftfirst, resize_siblings))

        self.width = width
        return True

    def frame_minheight(self, next_curwin=None) -> int:
        if self.window:
            if self.window == next_curwin:
                return 3
            return self.MIN_SIZE
        
        if self.split_type == SplitType.HORIZONTAL:
            min_height = 0
            for child in (self.left, self.right):
                child_min = child.frame_minheight(next_curwin)
                min_height = max(min_height, child_min)
            return min_height
        else:
            return (self.left.frame_minheight(next_curwin) + 
                   self.right.frame_minheight(next_curwin))

    def frame_minwidth(self, next_curwin=None) -> int:
        if self.window:
            if self.window == next_curwin:
                return 12
            return self.MIN_SIZE

        if self.split_type == SplitType.VERTICAL:
            min_width = 0
            for child in (self.left, self.right):
                child_min = child.frame_minwidth(next_curwin)
                min_width = max(min_width, child_min)
            return min_width
        else:
            return (self.left.frame_minwidth(next_curwin) + 
                   self.right.frame_minwidth(next_curwin))

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



class WindowMode:
    def __init__(self, editor):
        self.editor = editor
        self.stdscr = None
        self.MIN_HEIGHT = 3
        self.MIN_WIDTH = 10
        self.MIN_GUTTER = 1
        self.root_frame = None
        self._last_layout = None
        self._resize_lock = False
        self.p_wmh = 1  
        self.p_wmw = 10
        self.p_wh = 3   
        self.p_wiw = 12 

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
        
        if total_space < (min_size * 2 + self.MIN_GUTTER):
            return False

        try:
            if split_type == SplitType.HORIZONTAL:
                new_height = (height - self.MIN_GUTTER) // 2
                remaining_height = height - new_height - self.MIN_GUTTER
                current_window.resize(new_height, width)
                new_window = curses.newwin(remaining_height, width, 
                                         y + new_height + self.MIN_GUTTER, x)
            else:
                new_width = (width - self.MIN_GUTTER) // 2
                remaining_width = width - new_width - self.MIN_GUTTER
                current_window.resize(height, new_width)
                new_window = curses.newwin(height, remaining_width,
                                         y, x + new_width + self.MIN_GUTTER)

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
            current_window.clear()
            current_window.refresh()
            del current_window
            self.editor.stdscr.clear()
            self.editor.stdscr.refresh()
            
            for window in self.editor.windows:
                window.clear()
                window.refresh()
            
            self._redraw_gutters()
            self.editor.highlight_focused_window()
            self.editor.mode_line_window.refresh()
            return True

        except Exception:
            self._restore_layout()
            return False

    def resize_window(self, dimension: str, delta: int) -> bool:
        if self._resize_lock or not self.editor.windows:
            return False
            
        try:
            self._resize_lock = True
            current = self.editor.windows[self.editor.focused_window]
            current_frame = self.root_frame.find_frame_by_window(current)
            
            if not current_frame or not current_frame.parent:
                return False
            
            self._save_layout_state()
            height, width = current.getmaxyx()
            parent = current_frame.parent
            is_first = parent.left == current_frame
            
            if dimension == 'height':
                new_height = height + delta
                success = current_frame.frame_new_height(
                    new_height, is_first, True)
            else:
                new_width = width + delta
                success = current_frame.frame_new_width(
                    new_width, is_first, True)
                
            if success:
                self.win_comp_pos()
                self._redraw_gutters()
                return True
                
            self._restore_layout()
            return False
            
        finally:
            self._resize_lock = False

    def equalize_windows(self) -> bool:
        if not self.root_frame:
            return False

        try:
            self._save_layout_state()
            screen_height, screen_width = self.stdscr.getmaxyx()
            usable_height = screen_height - 1

            def win_equal_rec(frame: Frame, available_height: int, 
                            available_width: int) -> bool:
                if frame.window:
                    return frame.frame_new_height(available_height, True, True) and \
                           frame.frame_new_width(available_width, True, True)

                if frame.split_type == SplitType.HORIZONTAL:
                    n_children = sum(1 for _ in (frame.left, frame.right))
                    if n_children == 0:
                        return True
                        
                    height_per_child = (available_height - (n_children - 1)) // n_children
                    remaining_height = available_height
                    
                    for child in (frame.left, frame.right):
                        if child is frame.right:
                            child_height = remaining_height
                        else:
                            child_height = height_per_child
                        if not win_equal_rec(child, child_height, available_width):
                            return False
                        remaining_height -= child_height
                else:
                    n_children = sum(1 for _ in (frame.left, frame.right))
                    if n_children == 0:
                        return True
                        
                    width_per_child = (available_width - (n_children - 1)) // n_children
                    remaining_width = available_width
                    
                    for child in (frame.left, frame.right):
                        if child is frame.right:
                            child_width = remaining_width
                        else:
                            child_width = width_per_child
                        if not win_equal_rec(child, available_height, child_width):
                            return False
                        remaining_width -= child_width

                return True

            if win_equal_rec(self.root_frame, usable_height, screen_width):
                self.win_comp_pos()
                self._redraw_gutters()
                return True

            self._restore_layout()
            return False

        except curses.error:
            self._restore_layout()
            return False

    def handle_resize(self) -> None:
        if not self.root_frame:
            return
            
        screen_height, screen_width = self.stdscr.getmaxyx()
        usable_height = screen_height - 1

        self.root_frame.frame_new_height(usable_height, True, False)
        if not self._check_frame_heights(self.root_frame, usable_height):
            self.root_frame.frame_new_height(usable_height, True, True)

        self.root_frame.frame_new_width(screen_width, True, False)
        if not self._check_frame_widths(self.root_frame, screen_width):
            self.root_frame.frame_new_width(screen_width, True, True)

        self.win_comp_pos()
        self._redraw_gutters()

    def win_comp_pos(self) -> None:
        y = 0
        x = 0
        self._frame_comp_pos(self.root_frame, y, x)

    def _frame_comp_pos(self, frame: Frame, y: int, x: int) -> tuple[int, int]:
        if frame.window:
            if frame.win_y != y or frame.win_x != x:
                frame.win_y = y
                frame.win_x = x
                frame.window.mvwin(y, x)
            return (y + frame.height, x + frame.width)

        start_y = y
        start_x = x
        next_y = y
        next_x = x
        
        for child in (frame.left, frame.right):
            if frame.split_type == SplitType.HORIZONTAL:
                next_y = y
            else:
                next_x = x
                
            child_y, child_x = self._frame_comp_pos(child, next_y, next_x)
            
            if frame.split_type == SplitType.HORIZONTAL:
                y = child_y
                next_y = y + 1
            else:
                x = child_x
                next_x = x + 1

        return y, x

    def _check_frame_heights(self, frame: Frame, height: int) -> bool:
        if frame.height != height:
            return False

        if frame.split_type == SplitType.HORIZONTAL:
            for child in (frame.left, frame.right):
                if child.height != height:
                    return False
        return True

    def _check_frame_widths(self, frame: Frame, width: int) -> bool:
        if frame.width != width:
            return False

        if frame.split_type == SplitType.VERTICAL:
            for child in (frame.left, frame.right):
                if child.width != width:
                    return False
        return True

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
        usable_height = screen_height - 1
        
        return self.root_frame.redistribute_space(0, 0, usable_height, screen_width)

    def _save_layout_state(self):
        if not self.root_frame:
            return
            
        def capture_frame_state(frame: Frame) -> dict:
            state = {
                'width': frame.width,
                'height': frame.height,
                'split_type': frame.split_type
            }
            if frame.window:
                y, x = frame.window.getbegyx()
                height, width = frame.window.getmaxyx()
                state['window'] = (y, x, height, width)
            if frame.left:
                state['left'] = capture_frame_state(frame.left)
            if frame.right:
                state['right'] = capture_frame_state(frame.right)
            return state
            
        self._last_layout = capture_frame_state(self.root_frame)

    def _restore_layout(self):
        if not self._last_layout:
            return False
            
        try:
            for window, y, x, height, width in self._last_layout:
                window.mvwin(y, x)
                
            for window, y, x, height, width in self._last_layout:
                window.resize(height, width)
                
            self._redraw_gutters()
            return True
            
        except curses.error:
            return False

    def _redraw_gutters(self):
        try:
            screen_height, screen_width = self.stdscr.getmaxyx()
            max_height = screen_height - 1
            
            for window in self.editor.windows:
                y, x = window.getbegyx()
                height, width = window.getmaxyx()
                
                is_rightmost = x + width >= screen_width - 1
                is_bottommost = y + height >= max_height
                
                if not is_rightmost:
                    gutter = curses.newwin(height, self.MIN_GUTTER, y, x + width)
                    gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                    gutter.refresh()
                    
                if not is_bottommost:
                    gutter = curses.newwin(self.MIN_GUTTER, width, y + height, x)
                    gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                    gutter.refresh()
            
            self.stdscr.refresh()
            
        except curses.error:
            pass

    def _update_layout_state(self):
        self._save_layout_state()
        if self.root_frame:
            self.root_frame.ensure_consistent_tree()

    def _update_current_cursor(self):
        if self.editor.windows:
            self.editor.current_cursor = self.editor.cursors[self.editor.focused_window]
            self.editor.dispatcher.dispatch(Event.WINDOW_CHANGED, None)

    def cycle_focus(self):
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
                usable_height = screen_height - 1
                siblings = self._collect_siblings(current_frame, dimension)

                if dimension == 'height':
                    for sibling, _ in siblings:
                        if sibling.window:
                            sibling.frame_new_height(self.MIN_SIZE, True, True)
                    current_frame.frame_new_height(
                        usable_height - (len(siblings) * (self.MIN_SIZE + 1)), 
                        True, True)
                else:
                    for sibling, _ in siblings:
                        if sibling.window:
                            sibling.frame_new_width(self.MIN_SIZE, True, True)
                    current_frame.frame_new_width(
                        screen_width - (len(siblings) * (self.MIN_SIZE + 1)), 
                        True, True)

                self.win_comp_pos()
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
                usable_height = screen_height - 1

                def win_equal_rec(frame: Frame, available_height: int, available_width: int) -> bool:
                    if frame.window:
                        return (frame.frame_new_height(available_height, True, True) and 
                            frame.frame_new_width(available_width, True, True))

                    if frame.split_type == SplitType.HORIZONTAL:
                        n_children = sum(1 for _ in (frame.left, frame.right))
                        if n_children == 0:
                            return True
                            
                        height_per_child = (available_height - (n_children - 1)) // n_children
                        remaining_height = available_height
                        
                        for child in (frame.left, frame.right):
                            if child is frame.right:
                                child_height = remaining_height
                            else:
                                child_height = height_per_child
                            if not win_equal_rec(child, child_height, available_width):
                                return False
                            remaining_height -= child_height
                    else:
                        n_children = sum(1 for _ in (frame.left, frame.right))
                        if n_children == 0:
                            return True
                            
                        width_per_child = (available_width - (n_children - 1)) // n_children
                        remaining_width = available_width
                        
                        for child in (frame.left, frame.right):
                            if child is frame.right:
                                child_width = remaining_width
                            else:
                                child_width = width_per_child
                            if not win_equal_rec(child, available_height, child_width):
                                return False
                            remaining_width -= child_width

                    return True

                if win_equal_rec(self.root_frame, usable_height, screen_width):
                    self.win_comp_pos()
                    self._redraw_gutters()
                    return True

                self._restore_layout()
                return False

            except curses.error:
                self._restore_layout()
                return False

        def handle_resize(self) -> None:
            if not self.root_frame:
                return
                
            screen_height, screen_width = self.stdscr.getmaxyx()
            usable_height = screen_height - 1

            self.root_frame.frame_new_height(usable_height, True, False)
            if not self._check_frame_heights(self.root_frame, usable_height):
                self.root_frame.frame_new_height(usable_height, True, True)

            self.root_frame.frame_new_width(screen_width, True, False)
            if not self._check_frame_widths(self.root_frame, screen_width):
                self.root_frame.frame_new_width(screen_width, True, True)

            self.win_comp_pos()
            self._redraw_gutters()

        def win_comp_pos(self) -> None:
            y = 0
            x = 0
            self._frame_comp_pos(self.root_frame, y, x)

        def _frame_comp_pos(self, frame: Frame, y: int, x: int) -> tuple[int, int]:
            if frame.window:
                if frame.win_y != y or frame.win_x != x:
                    frame.win_y = y
                    frame.win_x = x
                    frame.window.mvwin(y, x)
                return (y + frame.height, x + frame.width)

            start_y = y
            start_x = x
            next_y = y
            next_x = x
            
            for child in (frame.left, frame.right):
                if frame.split_type == SplitType.HORIZONTAL:
                    next_y = y
                else:
                    next_x = x
                    
                child_y, child_x = self._frame_comp_pos(child, next_y, next_x)
                
                if frame.split_type == SplitType.HORIZONTAL:
                    y = child_y
                    next_y = y + 1
                else:
                    x = child_x
                    next_x = x + 1

            return y, x

        def _check_frame_heights(self, frame: Frame, height: int) -> bool:
            if frame.height != height:
                return False

            if frame.split_type == SplitType.HORIZONTAL:
                for child in (frame.left, frame.right):
                    if child.height != height:
                        return False
            return True

        def _check_frame_widths(self, frame: Frame, width: int) -> bool:
            if frame.width != width:
                return False

            if frame.split_type == SplitType.VERTICAL:
                for child in (frame.left, frame.right):
                    if child.width != width:
                        return False
            return True

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

        def _save_layout_state(self):
            if not self.root_frame:
                return
                
            def capture_frame_state(frame: Frame) -> dict:
                state = {
                    'width': frame.width,
                    'height': frame.height,
                    'split_type': frame.split_type,
                    'win_x': frame.win_x,
                    'win_y': frame.win_y
                }
                if frame.window:
                    y, x = frame.window.getbegyx()
                    height, width = frame.window.getmaxyx()
                    state['window'] = (y, x, height, width)
                if frame.left:
                    state['left'] = capture_frame_state(frame.left)
                if frame.right:
                    state['right'] = capture_frame_state(frame.right)
                return state
                
            self._last_layout = capture_frame_state(self.root_frame)

        def _restore_layout(self) -> bool:
            if not self._last_layout:
                return False
                
            try:
                for window, y, x, height, width in self._last_layout:
                    window.mvwin(y, x)
                
                for window, y, x, height, width in self._last_layout:
                    window.resize(height, width)
                    
                self._redraw_gutters()
                return True
                
            except curses.error:
                return False

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
                        gutter = curses.newwin(height, 1, y, x + width)
                        gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                        gutter.refresh()
                        
                    if not is_bottommost:
                        gutter = curses.newwin(1, width, y + height, x)
                        gutter.bkgd(' ', curses.color_pair(GUTTER) | curses.A_REVERSE)
                        gutter.refresh()
                
                self.stdscr.refresh()
                
            except curses.error:
                pass