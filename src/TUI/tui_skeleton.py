from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Dict

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen

from core.base_classes import NodeEnvironment
from core.flowstate_manager import save_flowstate, load_flowstate
from core.global_store import GlobalStore
from core.undo_manager import UndoManager

from TUI.global_window import GlobalWindow
from TUI.help_window import HelpWindow
from TUI.node_window import NodeWindow
from TUI.output_window import OutputWindow
from TUI.parameter_window import ParameterWindow
from TUI.status_window import StatusWindow

from TUI.file_screen import FileScreen
from TUI.keymap_screen import KeymapScreen
from TUI.main_layout import MainLayout, MainContent
from TUI.clear_all_modal import ClearAllConfirmation

from TUI.theme_collection import create_themes
from TUI.theme_selector import ThemeSelector

from TUI.logging_config import get_logger
from TUI.modeline import ModeLine
from TUI.screens_registry import (
    Mode,
    get_screen_registry,
    MAIN_SCREEN,
    FILE_SCREEN,
    KEYMAP_SCREEN,
)

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
    ClearAll,
)

logger = get_logger('tui.main')


@dataclass
class ModeChanged(Message):
    mode: Mode

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
        Binding("ctrl+u", "switch_mode('OUTPUT')", "Output Mode"),
        Binding("ctrl+k", "switch_mode('KEYMAP')", "Keymap Mode"),
        Binding("ctrl+t", "switch_mode('STATUS')", "Status Mode"),
        Binding("ctrl+l", "select_theme", "Load Theme"),
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
        background: $panel;
        color: $accent;
    }

    ModeLine {
        height: 1;
        background: $primary;
        color: $background;
    }
    
    NodeWindow {
        width: 3fr;
        background: $surface;
        border: solid $primary;
        color: $foreground;
    }
    
    NodeWindow:focus {
        border: double $secondary;
    }
    
    ParameterWindow {
        width: 1fr;
        height: 50%;
        background: $surface;
        border: solid $primary;
        color: $foreground;
    }

    ParameterWindow:focus, ParameterWindow:focus-within  {
        border: double $secondary;
    }
    
    .middle-section {
        width: 2fr;
    }
    """

    mode_line: ClassVar[ModeLine]
    help_window: ClassVar[HelpWindow]
    current_mode: reactive[Mode] = reactive(Mode.NODE)
    current_file: reactive[str] = reactive("")
    #current_theme: Theme = create_themes()["light_fire"]  # Add this line
    AUTOSAVE_FILE: ClassVar[str] = "autosave.json"  

    async def action_select_theme(self) -> None:
        logger.info("Starting theme selection")
        theme = await self.push_screen(ThemeSelector())
        logger.info(f"Selected theme name: {theme}")
        if theme:
            self.theme = theme
            self._refresh_all_windows()
            mode_line = self.query_one(ModeLine)
            mode_line.debug_info = f"Applied theme: {theme}"
            logger.info(f"Theme {theme} applied with refresh")

    def __init__(self):
        try:
            super().__init__()
            self.logger = get_logger('tui.app', level=2)
            self.logger.info("Starting TUIApp initialization")
            self.current_mode = Mode.NODE
            self.current_theme_index = 0;
            self.themes = create_themes()
            self.logger.info("Theme gathering complete")

        except Exception as e:
            self.logger.error(f"Init failed: {str(e)}", exc_info=True)
            raise
            
    def compose(self) -> ComposeResult:
        yield MainContent()
        yield HelpWindow()
        yield ModeLine()

    def on_mount(self) -> None:
        try:
            self.logger.info("Starting application mount")
            self.mode_line = self.query_one(ModeLine)
            self.help_window = self.query_one(HelpWindow)
            self.mode_line.path = "untitled.json"
            self.current_file = "untitled.json"
            
            # Register themes before setting default
            self.logger.info("Starting theme registration")
            for theme_name, theme in self.themes.items():
                self.logger.info(f"Registering theme: {theme_name}")
                self.register_theme(theme)
            
            # Set default theme after registering all themes
            self.logger.info("Setting default theme")
            self.theme = list(self.themes.keys())[0]
            self.logger.error("Theme registration complete")

            main_content = self.query_one(MainContent)
            node_window = main_content.query_one(NodeWindow)
            node_window.focus()
            
            self._update_mode_display()
            self._check_autosave()
            self.logger.info("Application mount complete")
        except Exception as e:
            self.logger.error(f"Mount failed: {str(e)}", exc_info=True)
            raise

    def on_file_loaded(self, message: FileLoaded) -> None:
        self._env = NodeEnvironment.get_instance()
        self._initialized = True
        self._refresh_layout()

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
        if isinstance(self.screen, (FileScreen, ModalScreen)):
            return
            
        if hasattr(self, "mode_line"):
            key_display = []
            if event.control:
                key_display.append("ctrl")
                
            if event.key not in ["ctrl", "shift", "alt"]:
                key_display.append(event.key)
                
            self.mode_line.keypress = "+".join(key_display)

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
                self.post_message(FileLoaded(self.AUTOSAVE_FILE))
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
            self.logger.info("Clear all response received: %s", clear)
            if clear:
                try:
                    self.logger.debug("Starting clear all process")
                    self._perform_autosave()
                    undo_manager = UndoManager()
                    self.logger.debug("Disabling undo manager")
                    undo_manager.disable()
                    
                    self.logger.debug("Flushing nodes")
                    NodeEnvironment.flush_all_nodes()
                    self.logger.debug("Flushing globals")
                    GlobalStore().flush_all_globals()
                    
                    # Add debug logging for message posting
                    self.logger.debug("About to post ClearAll message")
                    main_content = self.query_one(MainContent)
                    param_window = main_content.query_one(ParameterWindow)
                                        
                    clear_msg = ClearAll()
                    param_window.post_message(clear_msg)
                    
                    self.post_message(clear_msg)
                    self.logger.debug("Posted ClearAll message")
                    
                    self.logger.debug("Re-enabling undo manager")
                    undo_manager.enable()
                    
                    self.logger.debug("Refreshing windows")
                    self._refresh_all_windows()
                    
                    self.mode_line.debug_info = "Cleared all nodes, globals, and history"
                    self.logger.info("Successfully cleared all")
                except Exception as e:
                    self.logger.error(f"Clear all failed: {str(e)}", exc_info=True)
                    self.mode_line.debug_info = "Clear all failed"

        try:
            self.logger.debug("Pushing confirmation screen")
            self.push_screen(ClearAllConfirmation(), handle_clear_response)
        except Exception as e:
            self.logger.error(f"Failed to show confirmation dialog: {str(e)}", exc_info=True)


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
    print("Starting main...")
    app = TUIApp()
    try:
        print("Running app...")
        app.run()
    except Exception as e:
        print(f"CRASH: {str(e)}")
        import traceback
        traceback.print_exc()
        raise