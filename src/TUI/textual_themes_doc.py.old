from textual.app import App, ComposeResult
from textual.containers import Container
from textual.theme import Theme
from textual.widgets import Button, Label

"""
Textual Theme Management Guide
-----------------------------

Theme Basics:
- Themes provide styling variables for your TUI
- Built-in themes: "textual-dark", "textual-light", "nord", "gruvbox"
- Runtime theme change: app.theme = "theme_name"
- Preview themes: run 'textual colors' in terminal

Required Theme Colors:
- primary: Main branding color
Optional Colors:
- secondary: Alternative branding color
- accent: Attention-grabbing color
- foreground: Default text color
- background: Base background color
- success: Positive action color
- warning: Cautionary color
- error: Error state color
- surface: Widget background color
- panel: UI section separator color

Theme Variables:
- text-*: Text styling ($text-primary, $text-secondary, etc.)
- color-*: Color variations (lighten/darken)
- component-*: Widget-specific styling
"""

arctic_theme = Theme(
    name="arctic",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#B48EAD",
    foreground="#D8DEE9",
    background="#2E3440",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)

warm_summer = Theme(
    name="warm-summer",
    primary="#FF7E67",
    secondary="#FFC15E",
    accent="#FFD93D",
    foreground="#4A4A4A",
    background="#FFF5E4",
    success="#95D1CC",
    warning="#FF9F29",
    error="#FF1E1E",
    surface="#FFFFD0",
    panel="#FFE6BC",
    dark=False,
    variables={
        "block-cursor-text-style": "bold",
        "footer-key-foreground": "#FF7E67",
        "input-selection-background": "#FFC15E 35%",
        "link-background-hover": "#FFD93D",
    },
)

class ThemeSwapper(App):
    CSS = """
    Container {
        layout: vertical;
        align: center middle;
        width: 100%;
        height: 100%;
    }
    
    Label {
        margin: 1;
        text-style: bold;
        color: $primary;
    }
    
    Button {
        margin: 1;
        width: 30;
    }

    #theme-info {
        margin: 2;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Current Theme Demo", id="theme-info"),
            Button("Arctic", id="arctic", variant="primary"),
            Button("Summer", id="warm-summer", variant="warning"),
            Button("Dark", id="textual-dark", variant="default"),
            Button("Light", id="textual-light", variant="success"),
        )

    def on_mount(self) -> None:
        self.register_theme(arctic_theme)
        self.register_theme(warm_summer)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.theme = event.button.id
        self.query_one("#theme-info").update(f"Current Theme: {event.button.id}")


if __name__ == "__main__":
    """
    Running this file directly will launch a theme demo application.
    Key Features:
    - Shows multiple theme implementations
    - Demonstrates theme switching
    - Includes both dark and light themes
    - Shows custom theme variables
    
    Try creating your own theme by:
    1. Define a new Theme object with your colors
    2. Register it in on_mount()
    3. Add a button with your theme's name as the id
    
    View built-in themes: Run 'textual colors' in terminal
    """
    app = ThemeSwapper()
    app.run()
