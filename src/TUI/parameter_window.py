from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum

from textual.widgets import Static, Input
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.scroll_view import ScrollView
from textual.message import Message
from textual.binding import Binding
from textual.reactive import reactive
from textual.events import Focus, Blur, Key
from textual.validation import Validator, ValidationResult

from rich.text import Text
from rich.style import Style

from core.base_classes import NodeEnvironment, Node
from core.parm import ParameterType
from node_window import NodeSelected
from logging_config import get_logger

logger = get_logger('parameter')

# Base colors - Rich dark background with subtle warmth
PARAMETER_SET_BG = "#1A1816"         # Deep charcoal with a hint of warmth
PARAMETER_SET_BORDER = "#2D2520"     # Warm dark brown border
PARAMETER_WINDOW_BG = "#1A1816"      # Match the set background
PARAMETER_WINDOW_BORDER = "#2D2520"  # Match the set border

# Title and focus elements - Warm highlights
TITLE_COLOR = "#E8C5A5"              # Warm cream
PARAMETER_WINDOW_FOCUS_BORDER = "#D35F3C"  # Warm terracotta/orange - festive!

# Parameter labels - Muted but readable
PARAM_LABEL_BG = "#2D2520"           # Warm dark brown
PARAM_LABEL_COLOR = "#B5947A"        # Muted copper

# Input fields - Cool contrast to the warm backgrounds
PARAM_INPUT_BG = "#2B333B"           # Cool slate blue-grey
PARAM_INPUT_COLOR = "#D6E5F3"        # Ice blue text
PARAM_INPUT_BORDER = "#3D4D5C"       # Deeper slate blue

# Selected states - Festive highlights
PARAM_INPUT_SELECTED_BG = "#4A3B41"  # Muted burgundy
PARAM_INPUT_SELECTED_COLOR = "#F3D6D6"  # Soft pink
PARAM_INPUT_SELECTED_BORDER = "#8B4E55"  # Rich cranberry

# Editing states
PARAM_VALUE_EDITING_BG = "#2F3B35"   # Forest green undertones
PARAM_VALUE_EDITING_COLOR = "#C5E8D6"  # Mint green text

# Error states - Traditional but softer
PARAM_INPUT_INVALID_BG = "#5C3636"   # Muted red

# Legacy colors (if still needed)
PARAM_NAME_COLOR = "#B5947A"         # Muted copper (matching label color)
PARAM_VALUE_COLOR = "#D6E5F3"        # Ice blue (matching input color)
PARAM_VALUE_BG = "#2B333B"           # Slate blue-grey (matching input bg)
PARAM_VALUE_SELECTED_COLOR = "#F3D6D6"  # Soft pink (matching selected)
PARAM_VALUE_SELECTED_BG = "#4A3B41"    # Muted burgundy (matching selected)

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
    DEFAULT_CSS = f"""
    ParameterRow {{
        height: 2;
        margin: 0;
        padding: 0;
        width: 100%;
    }}
    
    ParameterRow > Static {{
        width: 20;
        background: {PARAM_LABEL_BG};
        color: {PARAM_LABEL_COLOR};
        padding: 0 1;
    }}
    
    ParameterRow > Input {{
        width: 1fr;
        background: {PARAM_INPUT_BG};
        color: {PARAM_INPUT_COLOR};
        border: none;
        padding: 0 1;
    }}
    
    ParameterRow > Input:focus {{
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
        param_type: ParameterType,
        on_change: Optional[Callable[[str], None]] = None
    ):
        super().__init__()
        self.name = name
        self._original_value = str(value)  # Keep the original value for escape
        self.value = str(value)            # Current accepted value
        self._editing = False              # Are we in edit mode?
        self.param_type = param_type.value
        self.on_change = on_change
        logger.info(f"ParameterRow.__init__: name={name}, value={value}")

    def compose(self):
        yield Static(f"{self.name}:", classes="label")
        input_widget = Input(value=self._original_value, id=f"input_{self.name}")
        input_widget.can_focus = True
        yield input_widget

    def on_focus(self, event: Focus) -> None:
        logger.info(f"ParameterRow.on_focus: {self.name}")
        if not self._editing:
            input_widget = self.query_one(Input)
            self._editing = True
            # Clear the input for new value
            input_widget.value = ""
            logger.info(f"Focus: Cleared input for editing. Original value: {self._original_value}")

    def on_blur(self, event: Blur) -> None:
        logger.info(f"ParameterRow.on_blur: {self.name}")
        input_widget = self.query_one(Input)
        if not input_widget.value:
            input_widget.value = self._original_value
        self._editing = False

    def key_escape(self) -> None:
        """Handle escape key"""
        logger.info(f"ParameterRow.key_escape: {self.name}")
        if self._editing:
            input_widget = self.query_one(Input)
            input_widget.value = self._original_value
            self._editing = False
            self.value = self._original_value
            if self.on_change:
                self.on_change(self._original_value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle the submit event (Enter key)"""
        logger.info(f"ParameterRow.on_input_submitted: value={event.value}")
        self._original_value = event.value  # Update original value for future escapes
        self.value = event.value
        self._editing = False
        if self.on_change:
            self.on_change(event.value)

    def watch_is_selected(self, selected: bool) -> None:
        input_widget = self.query_one(Input)
        input_widget.styles.background = PARAM_INPUT_SELECTED_BG if selected else PARAM_INPUT_BG
        input_widget.styles.color = PARAM_INPUT_SELECTED_COLOR if selected else PARAM_INPUT_COLOR

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
    
    ParameterSet .title {{
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
        yield Static(self.node.name(), classes="title")
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

    def _convert_value(self, value: str, param_type: ParameterType) -> any:
        if param_type == ParameterType.INT:
            return int(value)
        elif param_type == ParameterType.FLOAT:
            return float(value)
        elif param_type == ParameterType.TOGGLE:
            return value.lower() in ("true", "1", "yes", "y", "on", "t")
        elif param_type in (ParameterType.STRING, ParameterType.MENU, ParameterType.STRINGLIST):
            return value
        elif param_type == ParameterType.BUTTON:
            return None
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
        yield Vertical(id="parameter_stack")

    def on_mount(self) -> None:
        self.stack = self.query_one("#parameter_stack")
        logger.info("Parameter window mounted")

    def on_focus(self) -> None:
        if self.parameter_sets and not self.is_editing:
            # Select first parameter of first set if nothing is selected
            if self.current_set_index == -1:
                self.current_set_index = 0
                self.parameter_sets[0].select_parameter(0)

    def on_node_selected(self, event: NodeSelected) -> None:
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
        try:
            node_key = node.name()
            if node_key in self.node_to_param_set:
                old_param_set = self.node_to_param_set[node_key]
                self.parameter_sets.remove(old_param_set)
                old_param_set.remove()

            new_param_set = ParameterSet(node)
            self.parameter_sets.insert(0, new_param_set)
            self.stack.mount(new_param_set, before=0)
            self.node_to_param_set[node_key] = new_param_set
            self.current_set_index = 0
            new_param_set.select_parameter(0)

            # Ensure we're at the top when adding new parameter sets
            stack = self.query_one("#parameter_stack")
            stack.styles.offset = (0, 0)

            logger.info(f"Added/Updated parameter set for {node_key}, total sets: {len(self.parameter_sets)}")
        except Exception as e:
            logger.error(f"Error processing parameter set: {str(e)}")


    def action_move_up(self) -> None:
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
        if self.is_editing:
            self.is_editing = False
            self.focus()  # Return focus to window for navigation

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.is_editing = False
        self.focus()  # Return focus to window for navigation

    # def action_scroll_up(self) -> None:
    #     stack = self.query_one("#parameter_stack")
    #     current_offset = stack.styles.offset
    #     current_y_offset = current_offset.y if current_offset else 0
    #     new_y_offset = min(0, current_y_offset + 1)
    #     if new_y_offset != current_y_offset:
    #         stack.styles.offset = (current_offset.x if current_offset else 0, new_y_offset)

    # def action_scroll_down(self) -> None:
    #     stack = self.query_one("#parameter_stack")
    #     viewport_height = self.size.height
    #     content_height = sum(ps.size.height for ps in self.parameter_sets)
        
    #     if content_height <= viewport_height:
    #         return
            
    #     max_scroll = -(content_height - viewport_height)
    #     current_offset = stack.styles.offset
    #     current_y_offset = current_offset.y if current_offset else 0
    #     new_y_offset = max(max_scroll, current_y_offset - 1)
        
    #     if new_y_offset != current_y_offset:
    #         stack.styles.offset = (current_offset.x if current_offset else 0, new_y_offset)

    def action_scroll_up(self) -> None:
        self.scroll_up()

    def action_scroll_down(self) -> None:
        self.scroll_down()