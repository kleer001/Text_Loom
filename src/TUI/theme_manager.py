from dataclasses import dataclass
from pathlib import Path
import importlib.util
from typing import List, Optional
from textual.theme import Theme
from TUI.logging_config import get_logger

class ThemeManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = get_logger("theme_manager")
            cls._instance.theme_base_path = Path(__file__).parent / "theme_base.css"
            cls._instance._load_themes()
        return cls._instance

    def _load_themes(self) -> None:
        self.themes = {}
        theme_dir = Path(__file__).parent / "themes"
        
        self.logger.debug(f"Loading themes from directory: {theme_dir}")
        
        if not theme_dir.exists():
            self.logger.error(f"Theme directory not found: {theme_dir}")
            return

        # Create theme_base.css if it doesn't exist
        if not self.theme_base_path.exists():
            self._create_theme_base()

        for theme_file in theme_dir.glob("*_colors.py"):
            try:
                if not theme_file.is_file():
                    continue
                    
                theme_name = theme_file.stem.replace("_colors", "")
                self.logger.debug(f"Processing theme: {theme_name}")
                
                spec = importlib.util.spec_from_file_location(theme_name, theme_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    theme_var = f"{theme_name}_theme"
                    if hasattr(module, theme_var):
                        theme = getattr(module, theme_var)
                        # Add the base theme path to every theme
                        theme.paths.append(str(self.theme_base_path))
                        # Explicitly store the theme
                        self.themes[theme_name] = theme
                        self.logger.debug(f"Successfully stored theme: {theme_name}")
                        
            except Exception as e:
                self.logger.warning(f"Error loading theme {theme_file}: {e}", exc_info=True)
                continue  # Continue to next theme file

        self.logger.debug(f"Themes loaded: {list(self.themes.keys())}")

    def load_theme(self, theme_name: str) -> Optional[Theme]:
        self.logger.debug(f"Attempting to load theme: {theme_name}")
        self.logger.debug(f"Available themes: {list(self.themes.keys())}")
        
        if theme_name not in self.themes:
            self.logger.error(f"Theme {theme_name} not found in available themes: {list(self.themes.keys())}")
            return None
            
        theme = self.themes[theme_name]
        self.logger.debug(f"Loaded theme object: {theme}")
        return theme

    def _create_theme_base(self) -> None:
        theme_base_content = """
$text-on-primary: "#FFFFFF"
$text-on-secondary: "#FFFFFF"
$text-muted: "#444444"

$border-primary: "solid $primary"
$border-secondary: "solid $secondary"
$border-focus: "double $secondary"
$border-modal: "thick $primary"

$background-input: "$panel"
$background-input-selected: "$accent"
$background-input-invalid: "rgba(217, 48, 37, 0.1)"
$background-editing: "$primary 10%"
$background-help: "$primary 5%"

$modeline-bg: "$secondary"
$modeline-fg: "$text-on-secondary"

$node-selected-bg: "$accent"
$node-selected-fg: "$foreground"

$param-title: "$secondary"
$param-label-bg: "$surface"
$param-label-fg: "$text-muted"

$input-border: "#D0D0D0"
$input-border-focus: "$primary"
$input-border-invalid: "$error"

$window-border-normal: "$border-primary"
$window-border-focus: "$border-focus"

$table-border: "$primary"
$table-header-bg: "$primary 15%"
$table-alternate-bg: "$surface"
"""
        with open(self.theme_base_path, 'w') as f:
            f.write(theme_base_content.strip())
        self.logger.info(f"Created theme base file at {self.theme_base_path}")

    def get_available_themes(self) -> List[str]:
        return sorted(self.themes.keys())




from textual.screen import ModalScreen
from textual.widgets import OptionList, Static
from textual.containers import Container
from textual.app import ComposeResult

class ThemeSelector(ModalScreen[str]):
    CSS = """
    ThemeSelector {
        align: center middle;
    }

    #theme-selector-container {
        width: 40;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #theme-title {
        text-align: center;
        height: 3;
        margin: 0 0 1 0;
    }

    #theme-list {
        height: auto;
        max-height: 16;
        border: none;
        padding: 0;
    }

    #theme-list > ListItem {
        padding: 0 1;
    }

    #theme-list > ListItem:hover {
        background: $accent;
        color: $text;
    }
    """

    def compose(self) -> ComposeResult:
        theme_manager = ThemeManager.get_instance()
        available_themes = theme_manager.get_available_themes()
        
        with Container(id="theme-selector-container"):
            yield Static("🎨 Select Theme", id="theme-title")
            yield OptionList(*sorted(available_themes), id="theme-list")
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.prompt)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)