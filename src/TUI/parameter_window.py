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
from TUI.logging_config import get_logger
from TUI.messages import ParameterChanged, ScrollMessage, NodeSelected, NodeTypeSelected
import TUI.palette as pal

logger = get_logger('parameter')


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
        background: {pal.PARAM_LABEL_BG};
        color: {pal.PARAM_LABEL_COLOR};
        padding: 0 1;
    }}
    
    ParameterRow > Input {{
        width: 1fr;
        background: {pal.PARAM_INPUT_BG};
        color: {pal.PARAM_INPUT_COLOR};
        border: none;
        padding: 0 1;
    }}
    
    ParameterRow > Input:focus {{
        background: {pal.PARAM_INPUT_SELECTED_BG};
        color: {pal.PARAM_INPUT_SELECTED_COLOR};
        border: tall {pal.PARAM_INPUT_SELECTED_BORDER};
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
        self._original_value = str(value)  
        self.value = str(value)            
        self._editing = False              
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
        input_widget.styles.background = pal.PARAM_INPUT_SELECTED_BG if selected else pal.PARAM_INPUT_BG
        input_widget.styles.color = pal.PARAM_INPUT_SELECTED_COLOR if selected else pal.PARAM_INPUT_COLOR

class ParameterSet(Vertical):
    """A container for a node's parameters with title and parameter rows."""
    
    DEFAULT_CSS = f"""
    ParameterSet {{
        width: 100%;
        background: {pal.PARAM_SET_BG};
        border-bottom: solid {pal.PARAM_SET_BORDER};
        padding: 0 1;
        height: auto;
    }}
    
    ParameterSet .title {{
        color: {pal.PARAM_TITLE_COLOR};
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
        def handle_change(new_value: str) -> None:
            try:
                parm = self.node._parms[parm_name]
                parm.set(self._convert_value(new_value, parm._type))
                self.post_message(ParameterChanged(
                    self.node.path(),
                    parm_name,
                    new_value,
                    parm._type
                ))
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
            
        if self.current_index is not None:
            self.parameter_rows[self.current_index].is_selected = False
            
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
        background: {pal.PARAM_WINDOW_BG};
        border: solid {pal.PARAM_WINDOW_BORDER};
    }}
    
    ParameterWindow:focus {{
        border: double {pal.PARAM_WINDOW_FOCUS_BORDER};
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
        self.border_title = "Parameter"

    def on_focus(self) -> None:
        if self.parameter_sets and not self.is_editing:
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
            current_row = current_set.parameter_rows[current_set.current_index]
            input_widget = current_row.query_one(Input)
            input_widget.focus()

    def action_cancel_edit(self) -> None:
        if self.is_editing:
            self.is_editing = False
            self.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.is_editing = False
        self.focus()

    def action_scroll_up(self) -> None:
        self.scroll_up()

    def action_scroll_down(self) -> None:
        self.scroll_down()