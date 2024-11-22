from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DirectoryTree
from textual.binding import Binding
from pathlib import Path
from TUI.logging_config import get_logger
from core.base_classes import NodeEnvironment
from TUI.network_visualizer import load_flowstate
from core.global_store import GlobalStore
from TUI.screens_registry import MAIN_SCREEN, ACTION_SWITCH_TO_MAIN, ModeChanged, Mode

FILE_SCREEN_BACKGROUND = "#1e1e2e"
FILE_SCREEN_TEXT = "#cdd6f4"
FILE_SCREEN_DIRECTORY = "#89b4fa"
FILE_SCREEN_FILE = "#a6e3a1"

class FileScreen(Screen):
    BINDINGS = [
        Binding("escape", "switch_to_main", "Back"),
        Binding("enter", "select_file", "Select"),
    ]

    DEFAULT_CSS = f"""
    FileScreen {{
        align: center middle;
        background: {FILE_SCREEN_BACKGROUND};
        color: {FILE_SCREEN_TEXT};
        width: 100%;
        height: 100%;
    }}
    
    DirectoryTree {{
        width: 100%;
        height: 100%;
        background: {FILE_SCREEN_BACKGROUND};
        color: {FILE_SCREEN_TEXT};
    }}
    
    DirectoryTree > .tree--guides {{
        color: {FILE_SCREEN_DIRECTORY};
    }}
    
    DirectoryTree > .tree--cursor {{
        background: {FILE_SCREEN_DIRECTORY};
        color: {FILE_SCREEN_BACKGROUND};
    }}
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger('tui.file_screen')
        self.logger.info("FileScreen initialized")

    def compose(self) -> ComposeResult:
        self.logger.debug("Starting FileScreen compose")
        try:
            tree = DirectoryTree(".")
            self.logger.debug("DirectoryTree created successfully")
            yield tree
        except Exception as e:
            self.logger.error(f"Error in compose: {str(e)}", exc_info=True)
        self.logger.debug("Finished FileScreen compose")

    def on_mount(self):
        self.logger.info("FileScreen on_mount started")
        try:
            tree = self.query_one(DirectoryTree)
            self.logger.debug("DirectoryTree queried successfully")
            tree.focus()
            self.logger.debug("DirectoryTree focused")
        except Exception as e:
            self.logger.error(f"Error in on_mount: {str(e)}", exc_info=True)
        self.logger.info("FileScreen on_mount completed")

    def action_switch_to_main(self) -> None:
        self.logger.info("Switching to main screen")
        self.app.post_message(ModeChanged(Mode.NODE))  # Add this
        self.app.pop_screen()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self.logger.info(f"File selected: {event.path}")
        try:
            if not str(event.path).endswith('.json'):
                self.logger.warning(f"Selected file {event.path} is not a JSON file")
                return
            NodeEnvironment.flush_all_nodes()
            GlobalStore().flush_all_globals()
            load_flowstate(str(event.path))
            self.logger.info("Flowstate loaded successfully")
            self.app.post_message(ModeChanged(Mode.NODE))  # Add this
            self.app.pop_screen()
        except Exception as e:
            self.logger.error(f"Error processing selected file: {str(e)}", exc_info=True)
