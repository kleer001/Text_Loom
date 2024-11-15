from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum

from textual.widgets import Static, Input
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.scroll_view import ScrollView
from textual.message import Message
from textual.binding import Binding
from textual.reactive import reactive
from textual.events import Focus, Blur

from rich.text import Text
from rich.style import Style

from core.base_classes import NodeEnvironment, Node
from core.parm import ParameterType
from node_window import NodeSelected
from logging_config import get_logger

logger = get_logger('parameter')

PARAMETER_SET_BG = "#1E1E1E"  # Dark background
PARAMETER_SET_BORDER = "#4A4A4A"  # Subtle border color
TITLE_COLOR = "white"
PARAM_NAME_COLOR = "red"
PARAM_VALUE_COLOR = "green"
PARAM_VALUE_BG = "silver"
PARAM_VALUE_SELECTED_COLOR = "blue"
PARAM_VALUE_SELECTED_BG = "#336666"
PARAM_VALUE_EDITING_BG = "#2C2C2C"  # Slightly lighter than background
PARAM_VALUE_EDITING_COLOR = "#E0E0E0"  # Light grey text
PARAMETER_WINDOW_BG = "#1E1E1E"  # Dark background
PARAMETER_WINDOW_BORDER = "#2C2C2C"  # Slightly lighter than background
PARAMETER_WINDOW_FOCUS_BORDER = "#5294E2"  # Bright blue for focus
PARAM_LABEL_BG = "grey"
PARAM_LABEL_COLOR = "#B0B0B0"  # Light grey for labels
PARAM_INPUT_BG = "#2C2C2C"  # Slightly lighter than background
PARAM_INPUT_COLOR = "#E0E0E0"  # Light grey text
PARAM_INPUT_SELECTED_BG = "#3A3A3A"  # Lighter than normal input background
PARAM_INPUT_SELECTED_COLOR = "white"
PARAM_INPUT_INVALID_BG = "#8B0000"  # Dark red for errors
PARAM_INPUT_BORDER = "#4A4A4A"  # Subtle border color
PARAM_INPUT_SELECTED_BORDER = "#5294E2"  # Bright blue for selected input

class ScrollMessage(Message):
    def __init__(self, direction: int):
        self.direction = direction
        super().__init__()

@dataclass
class Parameter:
    name: str
    value: str
    type: str

class ParameterRow(Horizontal):
    """A row containing a parameter label and input field."""
    
    DEFAULT_CSS = f"""
    ParameterRow {{
        height: 3;
        margin: 0;
        padding: 0;
        width: 100%;
    }}
    
    ParameterRow Label {{
        padding: 1 1;
        background: {PARAM_LABEL_BG};
        color: {PARAM_LABEL_COLOR};
        min-width: 20;
    }}
    
    ParameterRow Input {{
        padding: 0 1;
        background: {PARAM_INPUT_BG};
        color: {PARAM_INPUT_COLOR};
        border: none;
        width: 100%;
    }}
    
    ParameterRow Input:focus {{
        background: {PARAM_INPUT_SELECTED_BG};
        color: {PARAM_INPUT_SELECTED_COLOR};
        border: tall {PARAM_INPUT_SELECTED_BORDER};
    }}
    """

    is_selected = reactive(False)
    name = reactive("")
    value = reactive("")
    param_type = reactive("")
    
    def __init__(
        self,
        name: str,
        value: str,
        param_type: ParameterType,  # Changed to accept ParameterType
        on_change: Optional[Callable[[str], None]] = None
    ):
        super().__init__()
        self.name = name
        self.value = value
        self.param_type = param_type.value  # Store the string value
        self.on_change = on_change
        self._previous_value = value

    def compose(self):
        yield Static(f"{self.name}:", classes="label")
        yield Input(
            value=self.value,
            id=f"input_{self.name}"
        )

    def _get_validator(self) -> str:
        """Return regex pattern for input validation based on parameter type."""
        if self.param_type == ParameterType.INT.value:
            return r"-?\d*"
        elif self.param_type == ParameterType.FLOAT.value:
            return r"-?\d*\.?\d*"
        elif self.param_type == ParameterType.TOGGLE.value:
            return r"[TtFfYyNn]|true|false|yes|no|0|1"
        # String and menu types accept any input
        return None

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes and validate the new value."""
        if not self._validate_input(event.value):
            # Revert to previous valid value
            input_widget = self.query_one(Input)
            input_widget.value = self._previous_value
            return
            
        self._previous_value = event.value
        if self.on_change:
            self.on_change(event.value)

    def _validate_input(self, value: str) -> bool:
        """Validate the input value based on parameter type."""
        if not value:
            return True
            
        try:
            if self.param_type == ParameterType.INT.value:
                if value != "-":  # Allow minus sign for negative numbers
                    int(value)
            elif self.param_type == ParameterType.FLOAT.value:
                if value not in ("-", "."):  # Allow minus sign and decimal point
                    float(value)
            elif self.param_type == ParameterType.TOGGLE.value:
                return value.lower() in ("true", "false", "1", "0", "yes", "no", "t", "f", "y", "n")
            return True
        except ValueError:
            return False

    def watch_is_selected(self, selected: bool) -> None:
        """Handle selection state changes."""
        input_widget = self.query_one(Input)
        if selected:
            input_widget.styles.background = PARAM_INPUT_SELECTED_BG
            input_widget.styles.color = PARAM_INPUT_SELECTED_COLOR
        else:
            input_widget.styles.background = PARAM_INPUT_BG
            input_widget.styles.color = PARAM_INPUT_COLOR

class ParameterSet(Vertical):
    """A container for a node's parameters with title and parameter rows."""
    
    DEFAULT_CSS = f"""
    ParameterSet {{
        width: 100%;
        background: {PARAMETER_SET_BG};
        border-bottom: solid {PARAMETER_SET_BORDER};
        padding: 0 1;
        height: auto;
    }}
    
    ParameterSet Title {{
        color: {TITLE_COLOR};
        text-style: bold;
        padding: 1 0;
    }}
    """

    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.current_index: Optional[int] = None
        self.parameter_rows: List[ParameterRow] = []

    def compose(self):
        """Create the title and parameter rows."""
        yield Static(self.node.name(), classes="title")
        
        # Create parameter rows
        for parm_name, parm in self.node._parms.items():
            row = ParameterRow(
                name=parm_name,
                value=str(parm._value),
                param_type=parm._type,
                on_change=self._create_change_handler(parm_name)
            )
            self.parameter_rows.append(row)
            yield row

    def _create_change_handler(self, parm_name: str) -> Callable[[str], None]:
        """Create a change handler for a specific parameter."""
        def handle_change(new_value: str) -> None:
            try:
                parm = self.node._parms[parm_name]
                parm.set(self._convert_value(new_value, parm._type))
                logger.info(f"Parameter {parm_name} updated to {new_value}")
            except Exception as e:
                logger.error(f"Error updating parameter {parm_name}: {str(e)}")
        return handle_change

    def _convert_value(self, value: str, param_type: str) -> any:
        """Convert string value to appropriate type."""
        param_type = param_type.lower()
        if param_type == "int":
            return int(value)
        elif param_type == "float":
            return float(value)
        elif param_type == "toggle":
            return value.lower() in ("true", "1", "yes", "y", "on", "t")
        elif param_type in ("string", "menu", "stringlist"):
            return value
        elif param_type == "button":
            return None
        logger.warning(f"Unknown parameter type: {param_type}")
        return value

    def select_parameter(self, index: int) -> None:
        """Select a parameter row and ensure only one is selected."""
        if not (0 <= index < len(self.parameter_rows)):
            return
            
        # Deselect current parameter if any
        if self.current_index is not None:
            self.parameter_rows[self.current_index].is_selected = False
            
        # Select new parameter
        self.current_index = index
        self.parameter_rows[index].is_selected = True
        
    def select_next(self) -> Optional[int]:
        """Select next parameter, return overflow if beyond last parameter."""
        if self.current_index is None:
            self.select_parameter(0)
            return None
            
        next_index = self.current_index + 1
        if next_index < len(self.parameter_rows):
            self.select_parameter(next_index)
            return None
        return 1  # Indicate overflow
        
    def select_previous(self) -> Optional[int]:
        """Select previous parameter, return overflow if beyond first parameter."""
        if self.current_index is None:
            self.select_parameter(0)
            return None
            
        prev_index = self.current_index - 1
        if prev_index >= 0:
            self.select_parameter(prev_index)
            return None
        return -1  # Indicate underflow

    def reset_selection(self) -> None:
        """Clear all parameter selections."""
        if self.current_index is not None:
            self.parameter_rows[self.current_index].is_selected = False
        self.current_index = None

class ParameterWindow(ScrollableContainer):
    """Main container for parameter sets with keyboard navigation."""

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
    
    ParameterWindow #parameter_stack {{
        width: 100%;
        height: auto;
    }}
    """

    BINDINGS = [
        Binding("up", "move_up", "Move Up"),
        Binding("down", "move_down", "Move Down"),
        Binding("enter", "edit_value", "Edit Value"),
        Binding("escape", "cancel_edit", "Cancel Edit"),
        Binding("pageup", "scroll_up", "Scroll Up"),
        Binding("pagedown", "scroll_down", "Scroll Down"),
    ]

    def __init__(self):
        super().__init__()
        self.parameter_sets: List[ParameterSet] = []
        self.current_set_index: int = -1
        self.node_to_param_set: Dict[str, ParameterSet] = {}
        self.is_editing: bool = False

    def compose(self):
        """Create the main vertical stack for parameter sets."""
        yield Vertical(id="parameter_stack")

    def on_mount(self) -> None:
        """Handle component mounting."""
        self.stack = self.query_one("#parameter_stack")
        logger.info("Parameter window mounted")

    def on_focus(self) -> None:
        """Handle window receiving focus."""
        if self.parameter_sets and not self.is_editing:
            # Select first parameter of first set if nothing is selected
            if self.current_set_index == -1:
                self.current_set_index = 0
                self.parameter_sets[0].select_parameter(0)

    def on_node_selected(self, event: NodeSelected) -> None:
        """Handle node selection events."""
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
        """Process a node and create or update its parameter set."""
        node_key = node.name()

        # Remove existing parameter set if it exists
        if node_key in self.node_to_param_set:
            old_param_set = self.node_to_param_set[node_key]
            self.parameter_sets.remove(old_param_set)
            old_param_set.remove()
            logger.info(f"Removed old parameter set for {node_key}")

        # Create new parameter set
        new_param_set = ParameterSet(node)
        self.parameter_sets.insert(0, new_param_set)
        self.stack.mount(new_param_set, before=0)
        self.node_to_param_set[node_key] = new_param_set
        
        # Update selection
        self.current_set_index = 0
        new_param_set.select_parameter(0)
        self.focus()  # Ensure window has focus for navigation

        logger.info(f"Added/Updated parameter set for {node_key}, total sets: {len(self.parameter_sets)}")

    def action_move_up(self) -> None:
        """Handle up arrow key."""
        if not self.parameter_sets or self.is_editing:
            return

        current_set = self.parameter_sets[self.current_set_index]
        result = current_set.select_previous()
        
        if result is not None and self.current_set_index > 0:
            # Move to previous parameter set
            current_set.reset_selection()
            self.current_set_index -= 1
            new_set = self.parameter_sets[self.current_set_index]
            new_set.select_parameter(len(new_set.parameter_rows) - 1)

    def action_move_down(self) -> None:
        """Handle down arrow key."""
        if not self.parameter_sets or self.is_editing:
            return

        current_set = self.parameter_sets[self.current_set_index]
        result = current_set.select_next()
        
        if result is not None and self.current_set_index < len(self.parameter_sets) - 1:
            # Move to next parameter set
            current_set.reset_selection()
            self.current_set_index += 1
            new_set = self.parameter_sets[self.current_set_index]
            new_set.select_parameter(0)

    def action_edit_value(self) -> None:
        """Start editing the selected parameter value."""
        if not self.parameter_sets or self.is_editing:
            return

        current_set = self.parameter_sets[self.current_set_index]
        if current_set.current_index is not None:
            self.is_editing = True
            # Focus the input widget of the selected parameter row
            current_row = current_set.parameter_rows[current_set.current_index]
            input_widget = current_row.query_one(Input)
            input_widget.focus()

    def action_cancel_edit(self) -> None:
        """Cancel editing and return focus to navigation."""
        if self.is_editing:
            self.is_editing = False
            self.focus()  # Return focus to window for navigation

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter pressed while editing)."""
        self.is_editing = False
        self.focus()  # Return focus to window for navigation

    def action_scroll_up(self) -> None:
        """Handle page up scrolling."""
        stack = self.query_one("#parameter_stack")
        current_offset = stack.styles.offset.y or 0
        new_offset = min(0, current_offset + self.size.height // 2)
        stack.styles.offset = (0, new_offset)

    def action_scroll_down(self) -> None:
        """Handle page down scrolling."""
        stack = self.query_one("#parameter_stack")
        viewport_height = self.size.height
        content_height = sum(ps.size.height for ps in self.parameter_sets)
        max_scroll = -(content_height - viewport_height)
        
        current_offset = stack.styles.offset.y or 0
        new_offset = max(max_scroll, current_offset - self.size.height // 2)
        stack.styles.offset = (0, new_offset)