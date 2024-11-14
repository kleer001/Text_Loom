from typing import Optional, List, Dict
from dataclasses import dataclass
from textual.widgets import Static
from textual.containers import ScrollableContainer, Vertical
from textual.message import Message
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style

from core.base_classes import NodeEnvironment, Node
from node_window import NodeSelected
from logging_config import get_logger

logger = get_logger('tui.parameter')

@dataclass
class Parameter:
    name: str
    value: str
    type: str

class ParameterSet(Static):
    DEFAULT_CSS = """
    ParameterSet {
        width: 100%;
        background: $boost;
        border-bottom: solid $primary;
        padding: 0 1;
        height: auto;
    }
    
    .title {
        color: white;
        text-style: bold;
        padding-bottom: 1;
    }
    
    .param-name {
        color: red;
        text-style: bold;
    }
    
    .param-value {
        color: silver;
    }
    
    .param-value-selected {
        color: blue;
        background: $accent;
    }
    
    .param-value-editing {
        background: $accent;
        color: $text;
    }
    """

    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.parameters: List[Parameter] = []
        self.selected_index: int = 0
        self.is_editing: bool = False
        self._load_parameters()

    def _load_parameters(self) -> None:
        try:
            self.parameters = []
            for parm_name, parm in self.node._parms.items():
                self.parameters.append(Parameter(
                    name=parm_name,
                    value=str(parm._value),
                    type=parm._type
                ))
            self._refresh_display()
        except Exception as e:
            logger.error(f"Error loading parameters: {str(e)}")


    def _refresh_display(self) -> None:
        text = Text()
        # Add title
        text.append(f"{self.node.name()}\n", style="white bold")

        # Add parameters
        for i, param in enumerate(self.parameters):
            # Parameter name
            text.append(f"{param.name}: ", Style(color="red", bold=True))
            
            # Parameter value
            value_style = ""
            if i == self.selected_index:
                value_style = "blue on #336666" if self.is_editing else "white"
            else:
                value_style = "silver"
            
            text.append(f"{param.value}\n", style=value_style)

        self.update(text)

    def move_selection(self, direction: int) -> Optional[int]:
        if self.is_editing:
            self.is_editing = False
            self._refresh_display()
            return None

        new_index = self.selected_index + direction
        if 0 <= new_index < len(self.parameters):
            self.selected_index = new_index
            self._refresh_display()
            return None
        return direction  # Return direction if we need to move to another widget

    def start_editing(self) -> None:
        self.is_editing = True
        self._refresh_display()

    def apply_edit(self, new_value: str) -> None:
        try:
            param = self.parameters[self.selected_index]
            # Use dictionary access for parms
            parm = self.node._parms[param.name]
            
            # Convert string value to appropriate type
            typed_value = self._convert_value(new_value, parm._type)
            parm.set(typed_value)
            
            param.value = new_value
            self.is_editing = False
            self._refresh_display()
        except Exception as e:
            logger.error(f"Error applying parameter edit: {str(e)}")


    def _convert_value(self, value: str, param_type: str) -> any:
        try:
            if param_type == 'int':
                return int(value)
            elif param_type == 'float':
                return float(value)
            elif param_type == 'toggle':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif param_type in ('string', 'menu', 'stringList'):
                return value
            elif param_type == 'button':
                return None  # Buttons don't have a value to set
            else:
                logger.warning(f"Unknown parameter type: {param_type}")
                return value
        except ValueError as e:
            logger.error(f"Error converting value: {str(e)}")
            return value

class ParameterWindow(ScrollableContainer):
    DEFAULT_CSS = """
    ParameterWindow {
        width: 100%;
        height: 100%;
        background: $boost;
        border: solid $background;
    }
    
    ParameterWindow:focus {
        border: double $accent;
    }
    """

    BINDINGS = [
        Binding("up", "move_up", "Move Up"),
        Binding("down", "move_down", "Move Down"),
        Binding("enter", "toggle_edit", "Edit/Apply Value"),
    ]

    def __init__(self):
        super().__init__()
        self.parameter_sets: List[ParameterSet] = []
        self.current_set_index: int = -1
        self.editing_value: str = ""
        self.stack: Optional[Vertical] = None

    def compose(self):
        yield Vertical(id="parameter_stack")

    def on_mount(self) -> None:
        self.stack = self.query_one("#parameter_stack")
        logger.info("Parameter window mounted")

    def watch_current_set_index(self, value: int) -> None:
        logger.debug(f"Current set index changed to {value}")

    def on_node_selected(self, event: NodeSelected) -> None:
        logger.info(f"Node selected event received: {event.node_path}")
        try:
            node = NodeEnvironment.get_instance().node_from_name(event.node_path)
            if node:
                logger.info(f"Adding parameter set for node: {node.name()}")
                self._add_parameter_set(node)
            else:
                logger.warning(f"No node found for path: {event.node_path}")
        except Exception as e:
            logger.error(f"Error handling node selection: {str(e)}")

    def _add_parameter_set(self, node: Node) -> None:
        param_set = ParameterSet(node)
        
        # Remove oldest set if we're at capacity
        while len(self.parameter_sets) >= 6:
            oldest_set = self.parameter_sets.pop()
            oldest_set.remove()

        # Add new set at the top
        self.parameter_sets.insert(0, param_set)
        self.stack.mount(param_set, before=0)
        self.current_set_index = 0
        logger.info(f"Added parameter set for {node.name()}, total sets: {len(self.parameter_sets)}")

    def action_move_up(self) -> None:
        if not self.parameter_sets:
            return
            
        current_set = self.parameter_sets[self.current_set_index]
        result = current_set.move_selection(-1)
        
        if result is not None and self.current_set_index > 0:
            self.current_set_index -= 1
            self.parameter_sets[self.current_set_index].selected_index = \
                len(self.parameter_sets[self.current_set_index].parameters) - 1
            self.parameter_sets[self.current_set_index]._refresh_display()

    def action_move_down(self) -> None:
        if not self.parameter_sets:
            return
            
        current_set = self.parameter_sets[self.current_set_index]
        result = current_set.move_selection(1)
        
        if result is not None and self.current_set_index < len(self.parameter_sets) - 1:
            self.current_set_index += 1
            self.parameter_sets[self.current_set_index].selected_index = 0
            self.parameter_sets[self.current_set_index]._refresh_display()

    def action_toggle_edit(self) -> None:
        if not self.parameter_sets:
            return
            
        current_set = self.parameter_sets[self.current_set_index]
        if current_set.is_editing:
            param = current_set.parameters[current_set.selected_index]
            current_set.apply_edit(self.editing_value)
            self.editing_value = ""
        else:
            current_set.start_editing()
            param = current_set.parameters[current_set.selected_index]
            self.editing_value = param.value