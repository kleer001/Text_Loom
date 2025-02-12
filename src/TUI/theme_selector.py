from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal, Vertical
from collections import defaultdict
from TUI.logging_config import get_logger
from textual.theme import Theme

class ThemeSelector(ModalScreen[str]):
    DEFAULT_CSS = """
    ThemeSelector {
        align: center middle;
        background: transparent;
    }

    #dialog {
        width: 120;
        height: 75%;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }

    .theme-item {
        padding: 0 1;
        width: 100%;
    }

    .theme-item.--highlighted {
        background: $primary;
        color: $surface;
    }

    .column-title {
        text-align: left;
        background: $primary;
        color: $surface;
        width: 100%;
    }

    Vertical {
        width: 1fr;
        height: 100%;
    }
    """

    BINDINGS = [
        ("escape", "dismiss(None)", "Cancel"),
        ("enter", "select_theme", "Select"),
        ("left", "move_left", "Previous Column"),
        ("right", "move_right", "Next Column"),
        ("up", "move_up", "Previous Theme"),
        ("down", "move_down", "Next Theme"),
    ]

    def __init__(self):
        super().__init__()
        self.logger = get_logger('theme_selector')
        self.current_col = 0
        self.current_row = 0
        self.columns = []
        self.column_data = defaultdict(list)

    def _safe_id(self, name: str) -> str:
        return name.replace("_", "-")

    def organize_themes(self):
        themes = self.app.themes.keys()
        for theme_name in sorted(themes):
            leader, name = theme_name.split('_', 1)
            self.column_data[leader].append((theme_name, name))
        
        self.columns = sorted(self.column_data.keys())

    def compose(self) -> ComposeResult:
        self.organize_themes()
        
        with Horizontal(id="dialog"):
            for leader in self.columns:
                with Vertical():
                    yield Static(leader.title(), classes="column-title")
                    for full_name, display_name in self.column_data[leader]:
                        yield Static(display_name, classes="theme-item", id=self._safe_id(full_name))

    def on_mount(self):
        self.logger.debug("ThemeSelector mounted")
        current_theme = self.app.theme
        
        self.organize_themes()
        
        for col_idx, leader in enumerate(self.columns):
            theme_list = self.column_data[leader]
            for row_idx, (theme_name, _) in enumerate(theme_list):
                if theme_name == current_theme:
                    self.current_col = col_idx
                    self.current_row = row_idx
                    break
                    
        self._highlight_current()

    def preview_current_theme(self):
        current_items = self.column_data[self.columns[self.current_col]]
        theme_name, _ = current_items[self.current_row]
        self.app.theme = theme_name

    def _highlight_current(self):
        for item in self.query(".theme-item.--highlighted"):
            item.remove_class("--highlighted")
            
        current_items = self.column_data[self.columns[self.current_col]]
        full_name, _ = current_items[self.current_row]
        self.query_one(f"#{self._safe_id(full_name)}").add_class("--highlighted")
        self.preview_current_theme()

    def _move_to_column(self, new_col: int):
        new_col = new_col % len(self.columns)
        target_column = self.column_data[self.columns[new_col]]
        self.current_row = min(self.current_row, len(target_column) - 1)
        self.current_col = new_col
        self._highlight_current()

    def action_move_left(self):
        self._move_to_column(self.current_col - 1)

    def action_move_right(self):
        self._move_to_column(self.current_col + 1)

    def action_move_up(self):
        items = self.column_data[self.columns[self.current_col]]
        self.current_row = (self.current_row - 1) % len(items)
        self._highlight_current()

    def action_move_down(self):
        items = self.column_data[self.columns[self.current_col]]
        self.current_row = (self.current_row + 1) % len(items)
        self._highlight_current()

    def action_select_theme(self):
        current_items = self.column_data[self.columns[self.current_col]]
        selected_theme, _ = current_items[self.current_row]
        self.dismiss(selected_theme)