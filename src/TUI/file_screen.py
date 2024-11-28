from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DirectoryTree, Input, Static
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from pathlib import Path
from TUI.logging_config import get_logger
from core.base_classes import NodeEnvironment
from TUI.network_visualizer import load_flowstate
from core.flowstate_manager import save_flowstate
from core.global_store import GlobalStore
from TUI.screens_registry import MAIN_SCREEN, Mode, ModeChanged
from TUI.messages import FileLoaded

class FileMode(Container):
    DEFAULT_CSS = """
    FileMode {
        height: auto;
        dock: bottom;
        padding: 0 1;
    }
    
    Input {
        width: 100%;
        border: solid $primary;
    }
    """
    
    def compose(self) -> ComposeResult:
        self.logger = get_logger('tui.file_mode')
        self.logger.debug("Composing FileMode")
        yield Input(placeholder="Enter file path to save...", id="file_path")

class FileScreen(Screen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("enter", "handle_action", "Select/Save"),
    ]

    DEFAULT_CSS = """
    FileScreen {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    
    DirectoryTree {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }
    """

    is_save_mode = reactive(False)
    current_path = reactive("")

    def __init__(self, save_mode: bool = False):
        self.logger = get_logger('tui.file_screen')
        self.logger.info(f"Initializing FileScreen with save_mode={save_mode}")
        try:
            super().__init__()
            self.is_save_mode = save_mode
            self.current_path = str(Path.cwd())
            self._tree_view = None  # Changed from self.tree
            self.logger.debug(f"Set current path to: {self.current_path}")
        except Exception as e:
            self.logger.error("Failed to initialize FileScreen", exc_info=True)
            raise

    def compose(self) -> ComposeResult:
        self.logger.info("Starting compose")
        try:
            self.logger.debug("Creating DirectoryTree")
            yield DirectoryTree(".")
            if self.is_save_mode:
                self.logger.debug("Save mode active, creating FileMode")
                file_mode = FileMode()
                yield file_mode
                self.logger.debug("FileMode yielded")
        except Exception as e:
            self.logger.error("Failed during compose", exc_info=True)
            raise

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.logger.info("Input submitted")
        try:
            path_value = event.value.strip()
            if path_value:
                self.logger.debug(f"Input submitted with value: {path_value}")
                self._handle_save(Path(path_value))
        except Exception as e:
            self.logger.error("Failed handling input submission", exc_info=True)
            raise

    def on_mount(self):
        self.logger.info("Starting on_mount")
        try:
            self.logger.debug("Querying for DirectoryTree")
            self._tree_view = self.query_one(DirectoryTree)  # Changed from self.tree
            self.logger.debug("Focusing DirectoryTree")
            self._tree_view.focus()
            
            if self.is_save_mode:
                self.logger.debug("Setting up save mode components")
                path_input = self.query_one(Input)
                if self.current_path:
                    path_input.value = self.current_path
            self.logger.info("Mount completed successfully")
        except Exception as e:
            self.logger.error("Failed during mount", exc_info=True)
            raise

    def action_handle_action(self) -> None:
        self.logger.info("Handle action called")
        try:
            if self.is_save_mode:
                path_input = self.query_one(Input)
                path_value = path_input.value.strip()
                if path_value:
                    self.logger.debug(f"About to call _handle_save with path: {path_value}")
                    self._handle_save(Path(path_value))
                    self.logger.debug("Returned from _handle_save")
                    return
                
            selected_node = self._tree_view.cursor_node
            if selected_node and selected_node.data.is_file:
                if self.is_save_mode:
                    self._handle_save(selected_node.data.path)
                else:
                    self._handle_load(selected_node.data.path)
        except Exception as e:
            self.logger.error("Failed during action handling", exc_info=True)
            raise

    def _handle_save(self, path: Path) -> None:
        self.logger.info(f"Handling save to: {path}")
        try:
            self.logger.debug("About to call save_flowstate")
            save_flowstate(str(path))
            self.logger.debug("save_flowstate completed")
            self.app.current_file = str(path)
            self.app.mode_line.path = str(path)
            self.logger.debug("About to post ModeChanged message")
            self.app.post_message(ModeChanged(Mode.NODE))
            self.logger.debug("About to pop screen")
            self.app.pop_screen()
            self.logger.debug("Screen popped")
        except Exception as e:
            self.logger.error(f"Failed to save file", exc_info=True)
            raise

    def _handle_load(self, path: Path) -> None:
        from core.undo_manager import UndoManager
        from TUI.node_window import NodeWindow
        self.logger.info(f"Handling load from: {path}")
        try:
            NodeEnvironment.flush_all_nodes()
            GlobalStore().flush_all_globals()
            UndoManager().flush_all_undos()
            UndoManager().undo_active = False
            load_flowstate(str(path))
            self.app.current_file = str(path)
            self.app.mode_line.path = str(path)
            self.app.pop_screen()
            node_window = self.app.query_one(NodeWindow)
            node_window._refresh_layout
            self.app._refresh_all_windows()
            self.app.post_message(FileLoaded(str(path)))
            self.app.post_message(ModeChanged(Mode.NODE))
            UndoManager().undo_active = True
        except Exception as e:
            self.logger.error(f"Failed to load file", exc_info=True)
            raise



    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.logger.info(f"File selected: {event.path}")
        try:
            if self.is_save_mode:
                path_input = self.query_one(Input)
                path_input.value = str(event.path)
                path_input.focus()
            else:
                self._handle_load(event.path)
        except Exception as e:
            self.logger.error("Failed during file selection", exc_info=True)
            raise