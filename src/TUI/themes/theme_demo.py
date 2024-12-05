from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.widgets import Header, Button, Input, DataTable, Label, Static
from textual.binding import Binding
from textual.reactive import reactive
from textual.theme import Theme

from textual.screen import ModalScreen
from textual.widgets import OptionList, Button
from textual.containers import Vertical, Horizontal
from textual.message import Message

from TUI.themes.theme_demo_themes import create_themes, get_theme_variable_defaults

class ThemeSelector(ModalScreen[str]):
    DEFAULT_CSS = """
    ThemeSelector {
        align: center middle;
        background: transparent;
        opacity: 255;
    }
    
    #dialog {
        width: 40;
        height: 15;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }
    """

    BINDINGS = [
        ("escape", "dismiss(None)", "Cancel"),
        ("enter", "select_theme", "Select"),
    ]

    def compose(self) -> ComposeResult:
        yield OptionList(*self.app.themes.keys(), id="dialog")

    def on_option_list_option_highlighted(self, event: Message) -> None:
        self.app.theme = event.option.prompt

    def action_select_theme(self) -> None:
        self.dismiss(self.query_one(OptionList).highlighted)

class ThemeDemo(Static):
    DEFAULT_CSS = """
    ThemeDemo {
        height: auto;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }
    
    ThemeDemo > Container {
        background: $surface;
        margin: 1;
        padding: 1;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Primary Color", classes="color-primary")
            yield Label("Secondary Color", classes="color-secondary")
            yield Label("Muted Text", classes="text-muted")
            yield Input(placeholder="Input field")
            yield Button("Normal Button")
            yield Button("Focused Button", classes="focused")
        
        with Container():
            table = DataTable()
            table.add_column("ID")
            table.add_column("Name")
            table.add_row("1", "Sample Row 1")
            table.add_row("2", "Sample Row 2")
            yield table

class ModeLine(Static):
    DEFAULT_CSS = """
    ModeLine {
        width: 100%;
        height: 3;
        background: $secondary;
        color: $text-on-secondary;
        content-align: center middle;
    }
    """

class ThemeDemoApp(App):
    CSS = """
    .color-primary {
        background: $primary;
        color: $text-on-primary;
    }
    .color-secondary {
        background: $secondary;
        color: $text-on-secondary;
    }
    .text-muted {
        color: $text-muted;
    }
    Input {
        margin: 1;
        border: solid $primary;
    }
    """

    BINDINGS = [
        Binding("ctrl+t", "select_theme", "Select Theme"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    async def action_select_theme(self) -> None:
        theme = await self.push_screen(ThemeSelector())
        if theme:
            self.theme = theme
            
    def __init__(self):
        super().__init__()
        self.current_theme_index = 0
        self.themes = create_themes()
        
    def get_theme_variable_defaults(self):
        return {
            "text-on-primary": "auto",
            "text-on-secondary": "auto",
            "text-on-accent": "auto",
            "background-input": "$panel",
            "background-input-selected": "$accent"
        }

    def compose(self) -> ComposeResult:
        yield Header()
        yield ModeLine()
        yield ScrollableContainer(ThemeDemo())

    def on_mount(self) -> None:
        for theme in self.themes.values():
            self.register_theme(theme)
        self.theme = list(self.themes.keys())[0]

    def action_next_theme(self) -> None:
        theme_names = list(self.themes.keys())
        self.current_theme_index = (self.current_theme_index + 1) % len(theme_names)
        self.theme = theme_names[self.current_theme_index]

if __name__ == "__main__":
    app = ThemeDemoApp()
    app.run()