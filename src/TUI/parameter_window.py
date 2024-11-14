from typing import Optional, List, Dict
from dataclasses import dataclass
from textual.widgets import Static
from textual.containers import ScrollableContainer, Vertical
from textual.scroll_view import ScrollView
from textual.message import Message
from textual.binding import Binding
from textual.reactive import reactive

from rich.text import Text
from rich.style import Style

from core.base_classes import NodeEnvironment, Node
from node_window import NodeSelected
from logging_config import get_logger

logger = get_logger('parameter')

PARAMETER_SET_BG = "$boost"
PARAMETER_SET_BORDER = "$primary"
TITLE_COLOR = "white"
PARAM_NAME_COLOR = "red"
PARAM_VALUE_COLOR = "green"
PARAM_VALUE_BG = "silver"
PARAM_VALUE_SELECTED_COLOR = "blue"
PARAM_VALUE_SELECTED_BG = "#336666"
PARAM_VALUE_EDITING_BG = "$accent"
PARAM_VALUE_EDITING_COLOR = "$text"
PARAMETER_WINDOW_BG = "$boost"
PARAMETER_WINDOW_BORDER = "$background"
PARAMETER_WINDOW_FOCUS_BORDER = "$accent"

class ScrollMessage(Message):
    def __init__(self, direction: int):
        self.direction = direction
        super().__init__()

@dataclass
class Parameter:
    name: str
    value: str
    type: str

class ParameterSet(Static):
    DEFAULT_CSS = f"""
    ParameterSet {{
        width: 100%;
        background: {PARAMETER_SET_BG};
        border-bottom: solid {PARAMETER_SET_BORDER};
        padding: 0 1;
        height: auto;
    }}
    .title {{
        color: {TITLE_COLOR};
        text-style: bold;
        padding-bottom: 1;
    }}
    .param-name {{
        color: {PARAM_NAME_COLOR};
        background: {PARAM_VALUE_BG};
        text-style: bold;
    }}
    .param-value {{
        color: {PARAM_VALUE_COLOR};
    }}
    .param-value-selected {{
        color: {PARAM_VALUE_SELECTED_COLOR};
        background: {PARAM_VALUE_SELECTED_BG};
    }}
    .param-value-editing {{
        background: {PARAM_VALUE_EDITING_BG};
        color: {PARAM_VALUE_EDITING_COLOR};
    }}
    """

    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.parameters: List[Parameter] = []
        self.selected_index: Optional[int] = None
        self.is_editing: bool = False
        self.is_active: bool = False 
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
            logger.info(f"Error loading parameters: {str(e)}")

    def reset_selection(self) -> None:
        """Reset the selection state of this parameter set."""
        self.selected_index = -1  # No selection
        self.is_editing = False
        self._refresh_display()

    def _refresh_display(self) -> None:
        text = Text()
        text.append(f"{self.node.name()}\n", style=f"{TITLE_COLOR} bold")

        for i, param in enumerate(self.parameters):
            text.append(f"{param.name}: ", Style(color=PARAM_NAME_COLOR, bold=True))

            value_style = PARAM_VALUE_COLOR
            display_value = param.value

            if i == self.selected_index:
                if self.is_editing:
                    value_style = f"{PARAM_VALUE_EDITING_COLOR} on {PARAM_VALUE_EDITING_BG}"
                    parent_window = self.screen.query_one(ParameterWindow)
                    display_value = parent_window.editing_value if parent_window.editing_value != "" else "_"
                else:
                    value_style = f"{PARAM_VALUE_SELECTED_COLOR} on {PARAM_VALUE_SELECTED_BG}"

            text.append(f"{display_value}\n", style=value_style)

        self.update(text)

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self._refresh_display()

    def move_selection(self, direction: int) -> Optional[int]:
        if self.is_editing:
            self.is_editing = False
            self._refresh_display()
            return None

        new_index = (self.selected_index or 0) + direction
        if 0 <= new_index < len(self.parameters):
            self.selected_index = new_index
            self._refresh_display()
            return None
        return direction

    def reset_selection(self):
        self.selected_index = None
        self.is_editing = False
        self._refresh_display()

    def start_editing(self) -> None:
        self.is_editing = True
        self._refresh_display()

    def apply_edit(self, new_value: str) -> None:
        try:
            if self.selected_index is None:
                return
                
            param = self.parameters[self.selected_index]
            parm = self.node._parms[param.name]
            
            if not new_value and parm._type.lower() in ('string', 'stringlist', 'button'):
                typed_value = ""
            else:
                typed_value = self._convert_value(new_value, parm._type)
                
            if typed_value is not None:  # None indicates conversion failure
                parm.set(typed_value)
                param.value = str(typed_value)  # Update the displayed value
                logger.info(f"Successfully updated parameter {param.name} to {typed_value}")
            else:
                logger.warning(f"Failed to convert value {new_value} for parameter {param.name}")
        except Exception as e:
            logger.error(f"Error applying parameter edit: {str(e)}")


    def _convert_value(self, value: str, param_type: str) -> any:
        try:
            param_type = param_type.lower()
            if param_type == 'int':
                return int(value)
            elif param_type == 'float':
                return float(value)
            elif param_type == 'toggle':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif param_type in ('string', 'menu', 'stringlist'):
                return value
            elif param_type == 'button':
                return None  # Buttons don't have a value to set
            else:
                logger.warning(f"Unknown parameter type: {param_type}")
                return value
        except ValueError as e:
            logger.error(f"Error converting value: {str(e)}")
            return None
        
class ParameterWindow(ScrollableContainer):
    DEFAULT_CSS = f"""
    ParameterWindow {{
        width: 100%;
        height: 100%;
        background: {PARAMETER_WINDOW_BG};
        border: solid {PARAMETER_WINDOW_BORDER};
    }}
    ParameterWindow:focus {{
        border: double {PARAMETER_WINDOW_FOCUS_BORDER};
    }}
    """



    BINDINGS = [
        Binding("up", "move_up", "Move Up"),
        Binding("down", "move_down", "Move Down"),
        Binding("enter", "noop", "Edit Value"),
        Binding("escape", "noop", "Cancel Edit"),
        Binding("ctrl+enter", "noop", "Accept Edit"),
        Binding("pageup", "scroll_up", "Scroll Up"),
        Binding("pagedown", "scroll_down", "Scroll Down"),
    ]

    def __init__(self):
        super().__init__()
        self.parameter_sets: List[ParameterSet] = []
        self.current_set_index: int = -1
        self.editing_value: str = ""
        self.stack: Optional[Vertical] = None
        self.node_to_param_set: Dict[str, ParameterSet] = {}
        


    def compose(self):
        yield Vertical(id="parameter_stack")

    def on_focus(self) -> None:
        if self.parameter_sets and all(ps.selected_index is None for ps in self.parameter_sets):
            self.parameter_sets[0].selected_index = 0
            self.current_set_index = 0
            self.parameter_sets[0]._refresh_display()

    def on_mount(self) -> None:
        self.stack = self.query_one("#parameter_stack")
        logger.info("Parameter window mounted")

    def on_node_selected(self, event: NodeSelected) -> None:
        logger.info(f"Node selected event received: {event.node_path}")
        try:
            node = NodeEnvironment.get_instance().node_from_name(event.node_path)
            if node:
                logger.info(f"Processing parameter set for node: {node.name()}")
                self._process_parameter_set(node)
            else:
                logger.warning(f"No node found for path: {event.node_path}")
        except Exception as e:
            logger.error(f"Error handling node selection: {str(e)}")

    def _process_parameter_set(self, node: Node) -> None:
        node_key = node.name() 

        if node_key in self.node_to_param_set:
            old_param_set = self.node_to_param_set[node_key]
            self.parameter_sets.remove(old_param_set)
            old_param_set.remove()
            logger.info(f"Removed old parameter set for {node_key}")

        new_param_set = ParameterSet(node)
        
        self.parameter_sets.insert(0, new_param_set)
        self.stack.mount(new_param_set, before=0)
        self.node_to_param_set[node_key] = new_param_set
        self.current_set_index = 0

        logger.info(f"Added/Updated parameter set for {node_key}, total sets: {len(self.parameter_sets)}")

    def _add_parameter_set(self, node: Node) -> None:
        param_set = ParameterSet(node)
        
        for ps in self.parameter_sets:
            ps.reset_selection()

        self.parameter_sets.insert(0, param_set)
        self.stack.mount(param_set, before=0)
        self.current_set_index = 0
        
        param_set.selected_index = 0
        param_set._refresh_display()

        logger.info(f"Added parameter set for {node.name()}, total sets: {len(self.parameter_sets)}")

    def on_key(self, event) -> None:
        if not self.parameter_sets or self.current_set_index < 0:
            return
            
        current_set = self.parameter_sets[self.current_set_index]
        if current_set.selected_index is None:
            return
            
        param = current_set.parameters[current_set.selected_index]
        
        if current_set.is_editing:
            if event.key == "escape":
                current_set.is_editing = False
                self.editing_value = ""
                current_set._refresh_display()
                return
                
            if event.key == "enter" and event.control:
                if self._validate_input(self.editing_value, param.type):
                    current_set.apply_edit(self.editing_value)
                    self.editing_value = ""
                    current_set.is_editing = False
                    current_set._refresh_display()
                else:
                    # Optionally add error feedback here
                    logger.warning(f"Invalid input for parameter type {param.type}: {self.editing_value}")
                return
                
            if event.is_printable:
                self.editing_value += event.character
                current_set._refresh_display()
            elif event.key == "backspace":
                self.editing_value = self.editing_value[:-1]
                current_set._refresh_display()
        elif event.key == "enter":
            current_set.is_editing = True
            self.editing_value = param.value  # Initialize with current value
            current_set._refresh_display()

    def _validate_input(self, value: str, param_type: str) -> bool:
        if not value and param_type.lower() not in ('string', 'stringlist', 'button'):
            return False
            
        try:
            param_type = param_type.lower()
            if param_type == "int":
                int(value)
            elif param_type == "float":
                float(value)
            elif param_type == "toggle":
                return value.lower() in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off')
            elif param_type in ('string', 'stringlist', 'menu'):
                return True
            elif param_type == "button":
                return True
            return True
        except ValueError:
            return False

    def action_move_up(self) -> None:
        if not self.parameter_sets:
            return
        current_set = self.parameter_sets[self.current_set_index]
        if current_set.is_editing:
            return
        result = current_set.move_selection(-1)
        if result is not None and self.current_set_index > 0:
            current_set.reset_selection()
            self.current_set_index -= 1
            new_set = self.parameter_sets[self.current_set_index]
            new_set.selected_index = len(new_set.parameters) - 1
            new_set._refresh_display()

    def action_move_down(self) -> None:
        if not self.parameter_sets:
            return
        current_set = self.parameter_sets[self.current_set_index]
        if current_set.is_editing:
            return
        result = current_set.move_selection(1)
        if result is not None and self.current_set_index < len(self.parameter_sets) - 1:
            current_set.reset_selection()
            self.current_set_index += 1
            new_set = self.parameter_sets[self.current_set_index]
            new_set.selected_index = 0
            new_set._refresh_display()

    def action_scroll_up(self) -> None:
        stack = self.query_one("#parameter_stack")
        current_offset = stack.styles.offset.y.value if stack.styles.offset.y else 0
        new_offset = min(0, current_offset + 1)  # Add 1 to move up
        logger.info(f"Scrolling up: current offset={current_offset}, new offset={new_offset}")
        stack.styles.offset = (0, int(new_offset))

    def action_scroll_down(self) -> None:
        stack = self.query_one("#parameter_stack")
        viewport_height = self.size.height
        content_height = self.get_total_content_height()
        max_scroll = -(content_height - viewport_height)  # Negative because we're moving up
        
        current_offset = stack.styles.offset.y.value if stack.styles.offset.y else 0
        new_offset = max(max_scroll, current_offset - 1)  # Subtract 1 to move down
        logger.info(f"Scrolling down: current offset={current_offset}, new offset={new_offset}, max_scroll={max_scroll}")
        stack.styles.offset = (0, int(new_offset))

    def get_total_content_height(self) -> int:
        total_height = 0
        for ps in self.parameter_sets:
            total_height += ps.size.height
            logger.info(f"Parameter set {ps.node.name()} height: {ps.size.height}")
        return total_height


    