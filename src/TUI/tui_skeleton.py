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
from TUI.messages import OutputMessage
from TUI.output_window import OutputWindow
from TUI.status_window import StatusWindow
from TUI.global_window import GlobalWindow
from TUI.help_window import HelpWindow
from TUI.file_screen import FileScreen
from TUI.keymap_screen import KeymapScreen 
import TUI.palette as pal
from core.flowstate_manager import save_flowstate

from TUI.screens_registry import (
    Mode, 
    get_screen_registry,
    MAIN_SCREEN,
    FILE_SCREEN,
    KEYMAP_SCREEN,
    ModeChanged
)

from TUI.logging_config import get_logger

logger = get_logger('tui.main')


@dataclass
class ModeChanged(Message):
    mode: Mode

class MainLayout(Grid):
    DEFAULT_CSS = f"""
    MainLayout {{
        height: 100%;
        width: 100%;
        grid-size: 3 1;
        grid-columns: 1fr 2fr 2fr;
        grid-rows: 1fr;
        grid-gutter: 0;
        background: {pal.MAIN_WIN_BACKGROUND};
        color: {pal.MAIN_WIN_TEXT};
    }}
    
    Vertical {{
        height: 100%;
        width: 100%;
    }}
    """

    def compose(self) -> ComposeResult:
        yield NodeWindow()
        yield ParameterWindow()
        with Vertical():
            yield GlobalWindow()
            yield OutputWindow()
            yield StatusWindow()
            
        

    def on_node_selected(self, event: NodeSelected) -> None:
        self.query_one(ParameterWindow).on_node_selected(event)

    def on_output_message(self, message: OutputMessage) -> None:
        logger.debug("MainLayout received output message")
        output_window = self.query_one(OutputWindow)
        output_window.on_output_message(message)

class MainContent(Static):
    def compose(self) -> ComposeResult:
        yield MainLayout()

    def on_mount(self) -> None:
        self.query_one(NodeWindow).focus()

class ModeLine(Static):
    DEFAULT_CSS = f"""
    ModeLine {{
        width: 100%;
        height: 1;
        background: {pal.MODELINE_BACKGROUND};
        color: {pal.MODELINE_TEXT};
        padding: 0 1;
    }}
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

    SCREENS = get_screen_registry(FileScreen, KeymapScreen)

    BINDINGS = [
        Binding("ctrl+n", "switch_mode('NODE')", "Node Mode"),
        Binding("ctrl+a", "switch_mode('PARAMETER')", "Parameter Mode"),
        Binding("ctrl+g", "switch_mode('GLOBAL')", "Global Mode"),
        Binding("ctrl+o", "open_file", "Open File"),
        Binding("ctrl+s", "quick_save", "Quick Save"),
        Binding("ctrl+d", "save_as", "Save As"),
        Binding("ctrl+e", "switch_mode('HELP')", "Help Mode"),
        Binding("ctrl+k", "switch_mode('KEYMAP')", "Keymap Mode"),
        Binding("ctrl+t", "switch_mode('STATUS')", "Status Mode"),
        Binding("ctrl+l", "switch_mode('OUTPUT')", "Output Mode"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

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

    mode_line: ClassVar[ModeLine]
    help_window: ClassVar[HelpWindow]
    current_mode: reactive[Mode] = reactive(Mode.NODE)
    current_file: reactive[str] = reactive("")

    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.app')
        self.current_mode = Mode.NODE

    def compose(self) -> ComposeResult:
        yield MainContent()
        yield HelpWindow()
        yield ModeLine()

    def on_mount(self) -> None:
        self.logger.info("Application started")
        try:
            self.mode_line = self.query_one(ModeLine)
            self.help_window = self.query_one(HelpWindow)
            self.mode_line.path = "untitled.json"
            self.current_file = "untitled.json"
        except NoMatches as e:
            self.logger.error("Failed to initialize components", exc_info=True)
            self.exit(message="Failed to initialize components")
        self._update_mode_display()

    def _handle_mode_focus(self, mode: Mode) -> None:
        self.logger.info(f"Handling focus for mode: {mode}")
        try:
            if mode == Mode.KEYMAP:
                self.logger.debug("Handling KEYMAP mode")
                if isinstance(self.screen, Screen) and not isinstance(self.screen, KeymapScreen):
                    self.logger.debug("Pushing KeymapScreen")
                    self.push_screen(KeymapScreen())
                return

            self.logger.debug(f"Current screen type: {type(self.screen)}")
            if isinstance(self.screen, (FileScreen, KeymapScreen)):
                self.logger.debug("Popping special screen")
                self.pop_screen()

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
                    self.logger.debug(f"Attempting to focus {widget_class.__name__}")
                    widget = self.query_one(widget_class)
                    widget.focus()
                    self.logger.info(f"Successfully focused {widget_class.__name__}")
                except NoMatches:
                    self.logger.error(f"Could not find widget for mode {mode}")
        except Exception as e:
            self.logger.error(f"Error in _handle_mode_focus: {str(e)}", exc_info=True)
            raise


    def action_switch_mode(self, mode_name: str) -> None:
        try:
            new_mode = Mode[mode_name]
            self.logger.info(f"Attempting to switch mode from {self.current_mode} to {new_mode}")
            
            self.current_mode = new_mode
            self._update_mode_display()
            self._handle_mode_focus(new_mode)
            self.post_message(ModeChanged(self.current_mode))
            
            self.logger.info(f"Mode switched successfully to {new_mode}")
        except KeyError:
            error_msg = f"Invalid mode: {mode_name}"
            self.logger.error(error_msg)
            self.mode_line.debug_info = error_msg
        except Exception as e:
            self.logger.error(f"Unexpected error in action_switch_mode: {str(e)}", exc_info=True) 

    def _update_mode_display(self) -> None:
        self.mode_line.mode = self.current_mode
        self.mode_line.debug_info = f"Switched to {self.current_mode}"
        self.help_window.current_section = str(self.current_mode)
        self.logger.debug(f"Updated display for mode: {self.current_mode}")
    
    def action_open_file(self) -> None:
        self.logger.info("action_open_file called")
        try:
            self.logger.debug("Creating new FileScreen instance with save_mode=False")
            file_screen = FileScreen(save_mode=False)
            self.logger.debug("Pushing FileScreen to screen stack")
            self.push_screen(file_screen)
            self.logger.info("FileScreen successfully pushed")
        except Exception as e:
            self.logger.error(f"Failed to open file screen: {str(e)}", exc_info=True)
            raise

    def action_quick_save(self) -> None:
        self.logger.info("action_quick_save called")
        try:
            save_flowstate(self.current_file)
            self.mode_line.path = self.current_file
            self.logger.info(f"Quick saved to: {self.current_file}")
        except Exception as e:
            self.logger.error(f"Quick save failed: {str(e)}", exc_info=True)

    def action_save_as(self) -> None:
        self.logger.info("action_save_as called")
        try:
            self.logger.debug("Creating new FileScreen instance with save_mode=True")
            file_screen = FileScreen(save_mode=True)
            if self.current_file:
                file_screen.current_path = self.current_file
            self.logger.debug("Pushing FileScreen to screen stack")
            self.push_screen(file_screen)
            self.logger.info("FileScreen successfully pushed")
        except Exception as e:
            self.logger.error(f"Failed to open save as screen: {str(e)}", exc_info=True)
            raise


    def _handle_load(self, path: Path) -> None:
            self.logger.info(f"Handling load from: {path}")
            try:
                if not str(path).endswith('.json'):
                    self.logger.debug("Not a JSON file, ignoring")
                    return
                NodeEnvironment.flush_all_nodes()
                GlobalStore().flush_all_globals()
                load_flowstate(str(path))
                self.current_path = str(path)
                self.app.current_file = str(path)  # Add this line to track the file in TUIApp
                self.app.post_message(ModeChanged(Mode.NODE))
                self.app.pop_screen()
            except Exception as e:
                self.logger.error(f"Failed to load file", exc_info=True)
                raise


if __name__ == "__main__":
    app = TUIApp()
    app.run()