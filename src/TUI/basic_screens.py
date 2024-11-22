from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding

class ScreenA(Screen):
    BINDINGS = [
        Binding("ctrl+a", "app.push_screen('screen_a')", "Screen A"),
        Binding("ctrl+b", "app.push_screen('screen_b')", "Screen B"),
        Binding("ctrl+c", "app.push_screen('screen_c')", "Screen C"),
        Binding("escape", "app.push_screen('screen_a')", "Return to A"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("A", id="screen-content"),
            id="screen-container"
        )

class ScreenB(Screen):
    BINDINGS = [
        Binding("ctrl+a", "app.push_screen('screen_a')", "Screen A"),
        Binding("ctrl+b", "app.push_screen('screen_b')", "Screen B"),
        Binding("ctrl+c", "app.push_screen('screen_c')", "Screen C"),
        Binding("escape", "app.push_screen('screen_a')", "Return to A"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("B", id="screen-content"),
            id="screen-container"
        )

class ScreenC(Screen):
    BINDINGS = [
        Binding("ctrl+a", "app.push_screen('screen_a')", "Screen A"),
        Binding("ctrl+b", "app.push_screen('screen_b')", "Screen B"),
        Binding("ctrl+c", "app.push_screen('screen_c')", "Screen C"),
        Binding("escape", "app.push_screen('screen_a')", "Return to A"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("C", id="screen-content"),
            id="screen-container"
        )

class ThreeScreenApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #screen-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    ScreenA #screen-container {
        background: red;
    }

    ScreenB #screen-container {
        background: green;
    }

    ScreenC #screen-container {
        background: blue;
    }

    #screen-content {
        text-align: center;
        content-align: center middle;
        width: 100%;
        height: 100%;
        color: white;
        text-style: bold;
    }
    """

    SCREENS = {
        "screen_a": ScreenA,
        "screen_b": ScreenB,
        "screen_c": ScreenC,
    }

    BINDINGS = [
        Binding("ctrl+a", "push_screen('screen_a')", "Screen A"),
        Binding("ctrl+b", "push_screen('screen_b')", "Screen B"),
        Binding("ctrl+c", "push_screen('screen_c')", "Screen C"),
        Binding("escape", "push_screen('screen_a')", "Return to A"),
    ]

    def on_mount(self) -> None:
        self.push_screen("screen_a")

if __name__ == "__main__":
    app = ThreeScreenApp()
    app.run()