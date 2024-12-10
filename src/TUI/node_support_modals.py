from typing import Optional
from textual.widgets import Static, OptionList, Input
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.containers import Vertical
from core.base_classes import NodeEnvironment, generate_node_types
from TUI.logging_config import get_logger
from TUI.messages import NodeTypeSelected
import os 

logger = get_logger('node_support')

class NodeTypeSelector(ModalScreen):
    DEFAULT_CSS = """
    NodeTypeSelector {
        align: center middle;
    }

    Vertical {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        color: $foreground;
    }

    OptionList {
        height: auto;
        max-height: 20;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.node_types = generate_node_types()
        logger.debug("NodeTypeSelector initialized")

    def compose(self):
        with Vertical():
            type_list = sorted(self.node_types.keys())
            type_list.remove('INPUT_NULL') #user won't ever need 
            type_list.remove('OUTPUT_NULL') #user won't ever need 
            logger.debug(f"Available node types: {type_list}")
            yield OptionList(*type_list)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        logger.debug(f"Option selected: {event.option.prompt}")
        self.app.pop_screen()
        logger.debug(f"Posting NodeTypeSelected message with type: {event.option.prompt}")
        self.app.query_one("NodeWindow").post_message(NodeTypeSelected(event.option.prompt))

    def action_cancel(self):
        logger.debug("Selection cancelled")
        self.app.pop_screen()

class DeleteConfirmation(ModalScreen[bool]):
    DEFAULT_CSS = """
    DeleteConfirmation {
        align: center middle;
    }

    Vertical {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        color: $foreground;
        padding: 1;
    }

    Static {
        text-align: center;
        width: 100%;
    }
    """

    def __init__(self, node_name: str):
        super().__init__()
        self.node_name = node_name

    def compose(self):
        with Vertical():
            yield Static(f"Delete node '{self.node_name}'?")
            yield Static("Y/N")

    def on_key(self, event):
        if event.key.lower() == "y":
            self.dismiss(True)
        elif event.key.lower() == "n" or event.key == "escape":
            self.dismiss(False)

class RenameInput(Input):
    DEFAULT_CSS = """
    RenameInput {
        height: 3;
        background: $panel;
        color: $foreground;
        border: none;
        padding: 0;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel rename")
    ]
    
    def __init__(self, original_node_path: str):
        super().__init__()
        self.original_node_path = original_node_path
    
    def action_cancel(self) -> None:
        self.remove()
            
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not self.value:
            self.remove()
            return

        try:
            old_node = NodeEnvironment.get_instance().node_from_name(self.original_node_path)
            if not old_node:
                self.remove()
                return
            
            old_path = old_node.path()
            old_name = os.path.basename(old_path)
            new_path = old_path.replace(old_name, self.value)

            if NodeEnvironment.get_instance().node_exists(new_path):
                logger.warning(f"Failed to rename node: name '{new_path}' already exists")
                self.remove()
                return
            
            logger.info(f"Renaming node from {old_path} to {new_path}")
            env = NodeEnvironment.get_instance()
            nodes_to_update = []
            
            for path, node in env.nodes.items():
                if path == old_path or path.startswith(f"{old_path}/"):
                    nodes_to_update.append(node)
                    logger.info(f"Will update node: {path}")
            
            for node in nodes_to_update:
                old_node_path = node.path()
                new_node_path = old_node_path.replace(old_path, new_path)
                logger.info(f"Updating node path from {old_node_path} to {new_node_path}")
                env.nodes[new_node_path] = node
                if old_node_path in env.nodes:
                    del env.nodes[old_node_path]
                if(node.rename(os.path.basename(new_node_path))):
                    logger.info(f"Successfully renamed node from {self.original_node_path} to {new_node_path}")
                else:
                    logger.warning(f"Failed to rename node: name '{self.value}' already exists") 

        except Exception as e:
            logger.error(f"Error renaming node: {str(e)}", exc_info=True)
        
        self.remove()
        self.app.query_one("NodeWindow")._refresh_layout()