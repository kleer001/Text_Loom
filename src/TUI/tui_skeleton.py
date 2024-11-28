from typing import ClassVar, Dict
from pathlib import Path
import logging
from datetime import datetime
import os 
from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.binding import Binding, BindingType
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
from TUI.messages import (
    OutputMessage,
    NodeAdded,
    NodeDeleted,
    ConnectionAdded,
    ConnectionDeleted,
    ParameterChanged,
    GlobalAdded,
    GlobalChanged,
    GlobalDeleted,
    NodeSelected,
    FileLoaded,
)

from TUI.output_window import OutputWindow
from TUI.status_window import StatusWindow
from TUI.global_window import GlobalWindow
from TUI.help_window import HelpWindow
from TUI.file_screen import FileScreen
from TUI.keymap_screen import KeymapScreen 
import TUI.palette as pal

from core.base_classes import NodeEnvironment
from core.flowstate_manager import save_flowstate, load_flowstate
from core.global_store import GlobalStore
from core.undo_manager import UndoManager

from TUI.screens_registry import (
    Mode, 
    get_screen_registry,
    MAIN_SCREEN,
    FILE_SCREEN,
    KEYMAP_SCREEN,
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
    keypress = reactive("")

    def watch_mode(self) -> None:
        self._refresh_display()

    def watch_path(self) -> None:
        self._refresh_display()
        
    def watch_debug_info(self) -> None:
        self._refresh_display()

    def watch_keypress(self) -> None:
        self._refresh_display()

    def _refresh_display(self) -> None:
        display_text = f"[{self.mode}] {self.path}"
        if self.debug_info:
            display_text += f" | {self.debug_info}"
        if self.keypress:
            display_text += f" | Keys: {self.keypress}"
        self.update(display_text)

class ClearAllConfirmation(ModalScreen[bool]):
    DEFAULT_CSS = f"""
    ClearAllConfirmation {{
        align: center middle;
    }}
    Vertical {{
        width: 40;
        height: auto;
        border: {pal.NODE_BORDER_MODAL} {pal.NODE_MODAL_BORDER};
        background: {pal.NODE_MODAL_SURFACE};
        color: {pal.NODE_MODAL_TEXT};
        padding: 1;
    }}
    Static {{
        text-align: center;
        width: 100%;
    }}
    """
    
    def compose(self):
        with Vertical():
            yield Static("Clear all nodes and globals?")
            yield Static("This action cannot be undone")
            yield Static("Y/N")
            
    def on_key(self, event):
        if event.key.lower() == "y":
            self.dismiss(True)
        elif event.key.lower() == "n" or event.key == "escape":
            self.dismiss(False)

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
        Binding("ctrl+z", "undo", "Undo"),
        Binding("ctrl+y", "redo", "Redo"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+w", "clear_all", "Clear All"),
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
    AUTOSAVE_FILE: ClassVar[str] = "autosave.json"  # Added class variable


    def __init__(self):
        self.logger = get_logger('tui.app')
        self.logger.info("Starting TUIApp initialization")
        try:
            super().__init__()
            self.logger.debug("Super initialization complete")
            self.current_mode = Mode.NODE
            self.logger.debug("Mode set to NODE")
            self._check_autosave()
            self.logger.info("TUIApp initialization complete")
        except Exception as e:
            self.logger.error(f"Failed during TUIApp initialization: {str(e)}", exc_info=True)
            raise

    def compose(self) -> ComposeResult:
        yield MainContent()
        yield HelpWindow()
        yield ModeLine()


    def on_mount(self) -> None:
        super().on_mount()
        self.logger.info("Application started")

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
        self._check_autosave()

    def _refresh_all_windows(self) -> None:
        main_layout = self.query_one(MainLayout)
        for window in main_layout.walk_children():
            if hasattr(window, 'refresh'):
                window.refresh()
            if hasattr(window, 'refresh_table'):
                window.refresh_table()
            if hasattr(window, 'parm_refresh'):
                window.parm_refresh()
            if hasattr(window, '_refresh_layout'):
                window._refresh_layout()

    def on_key(self, event) -> None:
        #I don't know why but we can't capture the alt key press :(
        try:
            if isinstance(self.screen, FileScreen):
                return
            mode_line = self.query_one(ModeLine)
            key_display = []
            
            if event.control:
                key_display.append("ctrl")
            self.logger.debug(f"Key event details - key: {event.key}, name: {event.name}, control: {event.control}")
                
            if event.key not in ["ctrl", "shift", "alt"]:
                key_display.append(event.key)
                
            mode_line.keypress = "+".join(key_display)
            self.logger.debug(f"Updated modeline keypress to: {mode_line.keypress}")
        except Exception as e:
            self.logger.error(f"Error handling key event: {str(e)}", exc_info=True)

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
            #self._refresh_all_windows()
        except Exception as e:
            self.logger.error(f"Failed to open file screen: {str(e)}", exc_info=True)
            raise

    def action_quick_save(self) -> None:
        self.logger.info("action_quick_save called")
        self.logger.debug(f"Current file path: {self.current_file}")
        
        if self.current_file:
            try:
                self.logger.debug(f"Quick saving to: {self.current_file}")
                save_flowstate(self.current_file)
                self.logger.info("Quick save successful")
            except Exception as e:
                self.logger.error(f"Quick save failed: {str(e)}", exc_info=True)
                self.action_save_as()
        else:
            self.logger.info("No current file path, redirecting to save_as")
            self.action_save_as()

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

    def on_file_loaded(self, message: FileLoaded) -> None:
        try:
            self.current_file = message.file_path
            self.mode_line.path = message.file_path
            self._refresh_all_windows()
            self.logger.info(f"Successfully refreshed all windows after loading {message.file_path}")
        except Exception as e:
            self.logger.error(f"Error refreshing after file load: {str(e)}", exc_info=True)


    def _check_autosave(self) -> None:
        return #temporary disable
        from core.undo_manager import UndoManager
        self.logger.info("Starting autosave check")
        try:
            autosave_path = Path(self.AUTOSAVE_FILE)
            self.logger.debug(f"Checking for autosave at: {autosave_path.absolute()}")
            
            if autosave_path.exists():
                self.logger.info(f"Found autosave file: {self.AUTOSAVE_FILE}")
                self.logger.debug("Flushing existing nodes")
                NodeEnvironment.flush_all_nodes()
                self.logger.debug("Flushing existing globals")
                GlobalStore().flush_all_globals()
                self.logger.debug("Flushing UndoManager")
                UndoManager().flush_all_undos()
                self.logger.debug("Freezing UndoManager")
                UndoManager().undo_active = False
                self.logger.debug("Loading flowstate from autosave")
                load_flowstate(self.AUTOSAVE_FILE)
                self.logger.info("Successfully loaded autosave")
                self.logger.debug("Unfreezing UndoManager")
                UndoManager().undo_active = True
            else:
                self.logger.info("No autosave file found")
        except Exception as e:
            self.logger.error(f"Failed to check/load autosave: {str(e)}", exc_info=True)
            raise

    def _perform_autosave(self) -> None:
        """Perform autosave operation."""
        self.logger.info("Performing autosave")
        try:
            save_flowstate(self.AUTOSAVE_FILE)
            self.logger.info("Autosave successful")
        except Exception as e:
            self.logger.error(f"Autosave failed: {str(e)}", exc_info=True)


    def action_clear_all(self) -> None:
        self.logger.info("Clear all action triggered")
        def handle_clear_response(clear: bool) -> None:
            if clear:
                try:
                    NodeEnvironment.flush_all_nodes()
                    GlobalStore().flush_all_globals()
                    self.undo_manager = UndoManager()
                    self._perform_autosave()
                    self._refresh_all_windows()
                    self.mode_line.debug_info = "Cleared all nodes, globals, and history"
                    self.logger.info("Successfully cleared all")
                except Exception as e:
                    self.logger.error(f"Clear all failed: {str(e)}", exc_info=True)
                    self.mode_line.debug_info = "Clear all failed"

        self.push_screen(ClearAllConfirmation(), handle_clear_response)
        self._refresh_all_windows()


    def action_undo(self) -> None:
        self.logger.info("Undo action triggered")
        undo_manager = UndoManager()
        
        self.logger.debug(f"Current undo stack size: {len(undo_manager.undo_stack)}")
        if undo_manager.undo_stack:
            self.logger.debug(f"Top of undo stack: {undo_manager.undo_stack[-1]}")
        
        if not undo_manager.undo_stack:
            self.mode_line.debug_info = "Nothing to undo"
            return

        try:
            undo_manager.undo()
            self._perform_autosave()
            self._refresh_all_windows()
            self.mode_line.debug_info = f"Undo: {undo_manager.get_undo_text()}"
        except Exception as e:
            self.logger.error(f"Undo failed: {str(e)}", exc_info=True)
            self.mode_line.debug_info = "Undo failed"

    def action_redo(self) -> None:
        self.logger.info("Redo action triggered")
        undo_manager = UndoManager()
        
        if not undo_manager.redo_stack:
            self.mode_line.debug_info = "Nothing to redo"
            return

        try:
            undo_manager.redo()
            self._perform_autosave()
            self._refresh_all_windows()
            self.mode_line.debug_info = f"Redo: {undo_manager.get_redo_text()}"
        except Exception as e:
            self.logger.error(f"Redo failed: {str(e)}", exc_info=True)
            self.mode_line.debug_info = "Redo failed"

    def _handle_network_change(self, message_type: str) -> None:
        self.logger.info(f"Network change detected: {message_type}")
        self._perform_autosave()
        self._refresh_all_windows()

    def on_parameter_changed(self, message: ParameterChanged) -> None:
        self.logger.debug(f"Parameter changed: {message.node_path}.{message.param_name} = {message.new_value}")
        self._handle_network_change("parameter_change")

    def on_node_added(self, message: NodeAdded) -> None:
        self.logger.debug(f"Node added: {message.node_path} of type {message.node_type}")
        self._handle_network_change("node_added")

    def on_node_deleted(self, message: NodeDeleted) -> None:
        self.logger.debug(f"Node deleted: {message.node_path}")
        self._handle_network_change("node_deleted")

    def on_connection_added(self, message: ConnectionAdded) -> None:
        self.logger.debug(f"Connection added: {message.from_node} -> {message.to_node}")
        self._handle_network_change("connection_added")

    def on_connection_deleted(self, message: ConnectionDeleted) -> None:
        self.logger.debug(f"Connection deleted: {message.from_node} -> {message.to_node}")
        self._handle_network_change("connection_deleted")

    def on_global_added(self, message: GlobalAdded) -> None:
        self.logger.debug(f"Global added: {message.key} = {message.value}")
        self._handle_network_change("global_added")

    def on_global_changed(self, message: GlobalChanged) -> None:
        self.logger.debug(f"Global changed: {message.key} = {message.value}")
        self._handle_network_change("global_changed")

    def on_global_deleted(self, message: GlobalDeleted) -> None:
        self.logger.debug(f"Global deleted: {message.key}")
        self._handle_network_change("global_deleted")

if __name__ == "__main__":
    app = TUIApp()
    app.run()