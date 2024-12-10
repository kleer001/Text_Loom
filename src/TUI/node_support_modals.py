from typing import Optional
from textual.widgets import Static, OptionList, Input
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.containers import Vertical
from core.base_classes import NodeEnvironment, generate_node_types, NodeType
from TUI.logging_config import get_logger
from TUI.messages import NodeTypeSelected, NodeMoveDestinationSelected
import os 

from textual import on
from rich.text import Text



logger = get_logger('node_support')

from typing import Optional
from textual.widgets import Static, OptionList, Input
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.containers import Vertical
from core.base_classes import NodeEnvironment, generate_node_types, NodeType
from TUI.logging_config import get_logger
from TUI.messages import NodeTypeSelected, NodeMoveDestinationSelected
import os 
from textual import on
from rich.text import Text

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

    HOTKEYS = {
        'n': 'FILE_IN',
        'o': 'FILE_OUT',
        'l': 'LOOPER',
        'm': 'MAKE_LIST',
        'e': 'MERGE',
        'u': 'NULL',
        'q': 'QUERY',
        't': 'TEXT'
    }

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.node_types = generate_node_types()
        logger.debug("NodeTypeSelector initialized")
        self._create_reverse_hotkey_map()

    def _create_reverse_hotkey_map(self) -> None:
        self.reverse_hotkeys = {v: k for k, v in self.HOTKEYS.items()}
        logger.debug(f"Created reverse hotkey map: {self.reverse_hotkeys}")

    def compose(self):
        with Vertical():
            type_list = sorted(self.node_types.keys())
            type_list.remove('INPUT_NULL')
            type_list.remove('OUTPUT_NULL')
            logger.debug(f"Available node types: {type_list}")
            
            options = []
            for node_type in type_list:
                try:
                    display_text = Text()
                    display_text.append(node_type)
                    
                    if node_type in self.reverse_hotkeys:
                        hotkey = self.reverse_hotkeys[node_type]
                        display_text.append(f" [{hotkey}]", style="bold")
                        logger.debug(f"Created styled option for {node_type} with hotkey {hotkey}")
                    
                    options.append(display_text)
                except Exception as e:
                    logger.error(f"Error creating styled text for {node_type}: {str(e)}", exc_info=True)

            option_list = OptionList(*options)
            logger.debug(f"Created OptionList with {len(options)} styled options")
            yield option_list

    def on_key(self, event) -> None:
        key = event.key.lower()
        if key in self.HOTKEYS:
            selected_type = self.HOTKEYS[key]
            logger.debug(f"Hotkey {key} pressed, selecting node type: {selected_type}")
            self.app.pop_screen()
            self.app.query_one("NodeWindow").post_message(NodeTypeSelected(selected_type))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        try:
            selected_text = event.option.prompt
            logger.debug(f"Option selected via list: {selected_text}")
            
            node_type = str(selected_text).split()[0]
            logger.debug(f"Extracted node type: {node_type}")
            
            self.app.pop_screen()
            logger.debug(f"Posting NodeTypeSelected message with type: {node_type}")
            self.app.query_one("NodeWindow").post_message(NodeTypeSelected(node_type))
        except Exception as e:
            logger.error(f"Error processing option selection: {str(e)}", exc_info=True)

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


class NodeMoveSelector(ModalScreen):
    DEFAULT_CSS = """
    NodeMoveSelector {
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

    def __init__(self, current_node_path: str) -> None:
        super().__init__()
        self.current_node_path = current_node_path
        
    def _get_available_destinations(self) -> list[str]:
        env = NodeEnvironment.get_instance()
        destinations = ["/"]  # Root is always first
        
        # Get all looper nodes except current node and its children
        for path, node in env.nodes.items():
            if (node.type() == NodeType.LOOPER and 
                path != self.current_node_path and 
                not path.startswith(f"{self.current_node_path}/")):
                destinations.append(path)
                
        return destinations

    def compose(self):
        with Vertical():
            destinations = self._get_available_destinations()
            yield OptionList(*destinations)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        self.app.pop_screen()
        self.app.query_one("NodeWindow").post_message(NodeMoveDestinationSelected(event.option.prompt))

    def action_cancel(self):
        self.app.pop_screen()