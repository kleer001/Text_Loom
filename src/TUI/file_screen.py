from textual.screen import Screen
from textual.widgets import DirectoryTree, Tree
from textual.widgets._tree import TreeNode

from textual.binding import Binding
from pathlib import Path
import os
from datetime import datetime
from typing import Optional

from TUI.logging_config import get_logger
import TUI.palette as pal


logger = get_logger('tui.file_screen')


FILE_SCREEN_BACKGROUND = "#1e1e2e"
FILE_SCREEN_TEXT = "#cdd6f4"
FILE_SCREEN_DIRECTORY = "#89b4fa"
FILE_SCREEN_FILE = "#a6e3a1"

from textual.widget import Widget
from textual.widgets import DataTable
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from datetime import datetime
import os
from pathlib import Path

class FileList(Widget):
    path = reactive(Path.cwd())
    
    class FileSelected(Message):
        def __init__(self, path: Path) -> None:
            self.path = path
            super().__init__()
    
    def __init__(self, path: Path | None = None):
        super().__init__()
        self.logger = get_logger('tui.file_screen.file_list')
        self._table = DataTable()
        self._focused_row = 0
        self.path = path or Path.cwd()
    
    def compose(self):
        self._table.cursor_type = "row"
        self._table.zebra_stripes = True
        yield self._table
    
    def _format_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"
    
    def watch_path(self) -> None:
        self.logger.debug(f"Path changed to: {self.path}")
        self.refresh_table()
        
    def refresh_table(self) -> None:
        self.logger.debug(f"Refreshing table for path: {self.path}")
        self._table.clear()
        self._table.add_columns("Name", "Size", "Modified")
        
        try:
            entries = []
            if self.path.parent != self.path:
                parent_stat = self.path.parent.stat()
                entries.append((
                    "..",
                    "",
                    datetime.fromtimestamp(parent_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    True,
                    self.path.parent
                ))
            
            for entry in sorted(self.path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if entry.name.startswith('.'):
                    continue
                    
                stats = entry.stat()
                size = self._format_size(stats.st_size) if not entry.is_dir() else ""
                mod_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                entries.append((
                    entry.name + ("/" if entry.is_dir() else ""),
                    size,
                    mod_time,
                    entry.is_dir(),
                    entry
                ))
            
            for name, size, mtime, is_dir, _ in entries:
                row_key = name
                row_data = (
                    Text(name, style=f"color({FILE_SCREEN_DIRECTORY if is_dir else FILE_SCREEN_FILE})"),
                    size,
                    mtime
                )
                self._table.add_row(*row_data, key=row_key)
                
            self.logger.debug(f"Added {len(entries)} entries to table")
            
        except Exception as e:
            self.logger.error(f"Error refreshing table: {str(e)}", exc_info=True)
            self._table.add_row("Error loading directory", "", "")
            
    def on_mount(self) -> None:
        self.refresh_table()
        
    def on_data_table_row_selected(self, event) -> None:
        try:
            row_key = event.row_key.value
            for entry in self.path.iterdir():
                if entry.name == row_key or (row_key == ".." and entry == self.path.parent):
                    if entry.is_dir():
                        self.path = entry
                    else:
                        self.post_message(self.FileSelected(entry))
                    break
        except Exception as e:
            self.logger.error(f"Error handling row selection: {str(e)}", exc_info=True)
class FileScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("enter", "select_file", "Select"),
        Binding("backspace", "parent_dir", "Parent Dir"),
    ]

    DEFAULT_CSS = f"""
    FileScreen {{
        align: center middle;
        background: {FILE_SCREEN_BACKGROUND};
        color: {FILE_SCREEN_TEXT};
        width: 100%;
        height: 100%;
    }}
    
    FileList {{
        width: 100%;
        height: 100%;
        background: {FILE_SCREEN_BACKGROUND};
        color: {FILE_SCREEN_TEXT};
    }}
    
    DataTable {{
        width: 100%;
        height: 100%;
        scrollbar-gutter: stable;
        overflow-y: scroll;
    }}
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.file_screen')
        self.logger.info("FileScreen initialized")

    def compose(self):
        try:
            path = Path.cwd()
            self.logger.debug(f"Creating FileList at path: {path}")
            file_list = FileList(path)
            self.logger.debug(f"Created FileList of type: {type(file_list)}")
            yield file_list
        except Exception as e:
            self.logger.error(f"Error in compose: {str(e)}", exc_info=True)

    def on_mount(self):
        self.logger.info("FileScreen mounted")
        try:
            file_list = self.query_one(FileList)
            file_list.focus()
        except Exception as e:
            self.logger.error(f"Error focusing FileList: {str(e)}", exc_info=True)

    def action_parent_dir(self):
        try:
            file_list = self.query_one(FileList)
            current_path = file_list.path
            if current_path.parent != current_path:
                self.logger.debug(f"Moving to parent directory: {current_path.parent}")
                file_list.path = current_path.parent
        except Exception as e:
            self.logger.error(f"Error navigating to parent: {str(e)}", exc_info=True)

    def action_select_file(self):
        try:
            file_list = self.query_one(FileList)
            if file_list._table.cursor_row is not None:
                row_key = file_list._table.get_row_at(file_list._table.cursor_row).key
                target_path = file_list.path / row_key if row_key != ".." else file_list.path.parent
                
                if target_path.is_dir():
                    self.logger.debug(f"Entering directory: {target_path}")
                    file_list.path = target_path
                else:
                    self.logger.debug(f"Selected file: {target_path}")
                    self.app.pop_screen()
        except Exception as e:
            self.logger.error(f"Error in select_file: {str(e)}", exc_info=True)