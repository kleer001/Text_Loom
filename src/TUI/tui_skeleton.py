from typing import ClassVar, Dict
from pathlib import Path
import logging
from datetime import datetime

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static
from textual.css.query import NoMatches
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Static

from dataclasses import dataclass
from enum import Enum, auto

logging.basicConfig(
    filename=f"logs/tui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class Mode(Enum):
    NODE = auto()
    PARAMETER = auto()
    GLOBAL = auto()
    FILE = auto()
    HELP = auto()
    KEYMAP = auto()
    STATUS = auto()
    OUTPUT = auto()

    def __str__(self) -> str:
        return self.name.title()


class NodeWindow(Static):
    DEFAULT_CSS = """
    NodeWindow {
        width: 100%;
        height: 100%;
        background: white;
        border: solid $background;
    }
    """

class ParameterWindow(Static):
    DEFAULT_CSS = """
    ParameterWindow {
        width: 100%;
        height: 100%;
        background: cornsilk;
        border: solid $background;
    }
    """

class StatusWindow(Static):
    DEFAULT_CSS = """
    StatusWindow {
        width: 100%;
        height: 50%;
        background: gainsboro;
        border: solid $background;
    }
    """

class OutputWindow(Static):
    DEFAULT_CSS = """
    OutputWindow {
        width: 100%;
        height: 37.5%;
        background: azure;
        border: solid $background;
    }
    """

class GlobalWindow(Static):
    DEFAULT_CSS = """
    GlobalWindow {
        width: 100%;
        height: 12.5%;
        background: honeydew;
        border: solid $background;
    }
    """

class MainLayout(Grid):
    DEFAULT_CSS = """
    MainLayout {
        height: 100%;
        width: 100%;
        grid-size: 3 1;
        grid-columns: 1fr 2fr 2fr;
        grid-rows: 1fr;
        grid-gutter: 1;
        background: $surface;
    }
    
    Vertical {
        height: 100%;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield NodeWindow()
        
        with Vertical():
            yield StatusWindow()
            yield OutputWindow()
            yield GlobalWindow()
            
        yield ParameterWindow()

class MainContent(Static):
    DEFAULT_CSS = """
    MainContent {
        width: 100%;
        height: 87.5%;
        background: $surface;
        padding: 0;
    }
    
    StatusWindow {
        height: 50%;
    }
    
    OutputWindow {
        height: 37.5%;
    }
    
    GlobalWindow {
        height: 12.5%;
    }
    """

    def compose(self) -> ComposeResult:
        yield MainLayout()


class HelpWindow(Static):
    DEFAULT_CSS = """
    HelpWindow {
        width: 100%;
        height: 12.5%;
        color: white;
        padding: 0 1;
        background: #4B0082;
        overflow-y: scroll;
    }
    """

    help_sections: Dict[str, str] = {}
    current_section = reactive("")

    def on_mount(self) -> None:
        self._load_help_text()
        
    def _load_help_text(self) -> None:
        try:
            help_path = Path("help_tui.md")
            if not help_path.exists():
                error_msg = f"Help file not found at {help_path.absolute()}"
                logger.error(error_msg)
                self.update(f"[Error: {error_msg}]")
                return

            current_section = ""
            current_content = []
            
            with help_path.open() as f:
                logger.info(f"Loading help text from {help_path.absolute()}")
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        if current_section:
                            logger.debug(f"Adding section {current_section} with {len(current_content)} lines")
                            self.help_sections[current_section] = "\n".join(current_content)
                        current_section = line[1:-1].upper()
                        current_content = []
                        logger.debug(f"Found new section {current_section} at line {line_num}")
                    elif current_section:
                        current_content.append(line)

            if current_section and current_content:
                logger.debug(f"Adding final section {current_section} with {len(current_content)} lines")
                self.help_sections[current_section] = "\n".join(current_content)

            logger.info(f"Loaded {len(self.help_sections)} help sections: {list(self.help_sections.keys())}")

        except Exception as e:
            error_msg = f"Error loading help: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.update(f"[Error: {error_msg}]")

    def watch_current_section(self) -> None:
        section = self.current_section.upper()
        content = self.help_sections.get(section, "")
        if not content:
            logger.warning(f"No help content found for section: {section}")
            content = f"No help available for {section}"
        self.update(content)

class ModeLine(Static):
    DEFAULT_CSS = """
    ModeLine {
        width: 100%;
        height: 1;
        background: blue;
        color: white;
        padding: 0 1;
    }
    """

    mode = reactive(Mode.NODE)
    path = reactive("untitled")
    debug_info = reactive("")

    def watch_mode(self) -> None:
        self._refresh_display()

    def watch_path(self) -> None:
        self._refresh_display()
        
    def watch_debug_info(self) -> None:
        self._refresh_display()

    def _refresh_display(self) -> None:
        self.update(f"[{self.mode}] {self.path} | {self.debug_info}")

class TUIApp(App[None]):
    CSS = """
    Screen {
        layout: vertical;
    }

    MainContent {
        height: 7fr;
    }

    HelpWindow {
        height: 1fr;
    }

    ModeLine {
        height: 1;
    }
    
    NodeWindow {
        width: 1fr;
    }
    
    ParameterWindow {
        width: 2fr;
    }
    
    .middle-section {
        width: 2fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+n", "switch_mode('NODE')", "Node Mode"),
        Binding("ctrl+a", "switch_mode('PARAMETER')", "Parameter Mode"),
        Binding("ctrl+g", "switch_mode('GLOBAL')", "Global Mode"),
        Binding("ctrl+f", "switch_mode('FILE')", "File Mode"),
        Binding("ctrl+e", "switch_mode('HELP')", "Help Mode"),
        Binding("ctrl+k", "switch_mode('KEYMAP')", "Keymap Mode"),
        Binding("ctrl+t", "switch_mode('STATUS')", "Status Mode"),
        Binding("ctrl+o", "switch_mode('OUTPUT')", "Output Mode"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    mode_line: ClassVar[ModeLine]
    help_window: ClassVar[HelpWindow]
    current_mode: reactive[Mode] = reactive(Mode.NODE)

    @dataclass
    class ModeChanged(Message):
        mode: Mode
        
    def compose(self) -> ComposeResult:
        yield MainContent()
        yield HelpWindow()
        yield ModeLine()

    def on_mount(self) -> None:
        logger.info("Starting TUI application")
        try:
            self.mode_line = self.query_one(ModeLine)
            self.help_window = self.query_one(HelpWindow)
        except NoMatches as e:
            error_msg = "Failed to initialize required components"
            logger.error(error_msg, exc_info=True)
            self.exit(message=error_msg)
        self._update_mode_display()

    def _update_mode_display(self) -> None:
        self.mode_line.mode = self.current_mode
        self.mode_line.debug_info = f"Switched to {self.current_mode}"
        self.help_window.current_section = str(self.current_mode)
        logger.debug(f"Updated display for mode: {self.current_mode}")

    def action_switch_mode(self, mode_name: str) -> None:
        try:
            new_mode = Mode[mode_name]
            if new_mode != self.current_mode:
                logger.info(f"Switching mode from {self.current_mode} to {new_mode}")
                self.current_mode = new_mode
                self._update_mode_display()
                self.post_message(self.ModeChanged(self.current_mode))
        except KeyError:
            error_msg = f"Invalid mode: {mode_name}"
            logger.error(error_msg)
            self.mode_line.debug_info = error_msg

if __name__ == "__main__":
    app = TUIApp()
    app.run()