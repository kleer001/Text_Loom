from typing import ClassVar, Dict
from pathlib import Path
import logging
from datetime import datetime
import os 
from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen
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

from TUI.node_window import NodeWindow, NodeSelected
from TUI.parameter_window import ParameterWindow

from TUI.logging_config import get_logger

logger = get_logger('tui.main')

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

class FileScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.file_screen')

    DEFAULT_CSS = """
    FileScreen {
        align: center middle;
        background: $boost;
        width: 100%;
        height: 100%;
    }

    .file-content {
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: $panel;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(classes="file-content"):
            yield Static("File Browser (Placeholder)")

    def on_mount(self) -> None:
        self.logger.info("FileScreen mounted")



class KeymapScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.keymap_screen')

    DEFAULT_CSS = """
    KeymapScreen {
        align: center middle;
        background: $boost;
        width: 100%;
        height: 100%;
    }

    .keymap-content {
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: $panel;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(classes="keymap-content"):
            yield Static("Keymap Browser (Placeholder)")

    def on_mount(self) -> None:
        self.logger.info("KeymapScreen mounted")

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

    def on_node_selected(self, event: NodeSelected) -> None:
        self.query_one(ParameterWindow).on_node_selected(event)

class MainContent(Static):
    def compose(self) -> ComposeResult:
        yield MainLayout()

    def on_mount(self) -> None:
        self.query_one(NodeWindow).focus()


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
            help_path = Path("TUI/help_tui.md")
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
    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.app')
        self.current_mode = Mode.NODE

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

        #Binding("tab", "", ""),  #DISABLED

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
        self.logger.info("Application started")
        try:
            self.mode_line = self.query_one(ModeLine)
            self.help_window = self.query_one(HelpWindow)
            self.install_screen(FileScreen(), name="file")
            self.install_screen(KeymapScreen(), name="keymap")
        except NoMatches as e:
            error_msg = "Failed to initialize required components"
            self.logger.error(error_msg, exc_info=True)
            self.exit(message=error_msg)
        self._update_mode_display()

    def action_switch_mode(self, mode_name: str) -> None:
        try:
            new_mode = Mode[mode_name]
            if new_mode != self.current_mode:
                self.logger.info(f"Switching mode from {self.current_mode} to {new_mode}")
                self.current_mode = new_mode
                self._update_mode_display()
                self._handle_mode_focus(new_mode)
                self.post_message(self.ModeChanged(self.current_mode))
        except KeyError:
            error_msg = f"Invalid mode: {mode_name}"
            self.logger.error(error_msg)
            self.mode_line.debug_info = error_msg

    def _handle_mode_focus(self, mode: Mode) -> None:
        self.logger.info(f"Handling focus for mode: {mode}")
        
        try:
            if mode == Mode.FILE:
                self.push_screen("file")
                return
            elif mode == Mode.KEYMAP:
                self.push_screen("keymap")
                return

            widget_map = {
                Mode.NODE: NodeWindow,
                Mode.PARAMETER: ParameterWindow,
                Mode.GLOBAL: GlobalWindow,
                Mode.STATUS: StatusWindow,
                Mode.OUTPUT: OutputWindow,
            }

            if mode in widget_map:
                widget_class = widget_map[mode]
                try:
                    widget = self.query_one(widget_class)
                    self.logger.info(f"Focusing {widget_class.__name__}")
                    widget.focus()
                except NoMatches:
                    self.logger.error(f"Could not find widget for mode {mode}")

        except Exception as e:
            self.logger.error(f"Error in _handle_mode_focus: {str(e)}", exc_info=True)

    def _update_mode_display(self) -> None:
        self.mode_line.mode = self.current_mode
        self.mode_line.debug_info = f"Switched to {self.current_mode}"
        self.help_window.current_section = str(self.current_mode)
        self.logger.debug(f"Updated display for mode: {self.current_mode}")
 
if __name__ == "__main__":
    app = TUIApp()
    app.run()