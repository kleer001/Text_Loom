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
from TUI.messages import ParameterChanged, ScrollMessage, NodeSelected, NodeTypeSelected, ClearAll, NodeDeleted
import TUI.palette as pal

logger = get_logger('parameter')

"""Parameter window module for TUI node parameter management.

This module provides a textual-based UI for managing node parameters in a scrollable window.
The interface allows for viewing and editing parameters for multiple nodes simultaneously,
with keyboard-based navigation and editing capabilities.

Classes:
    Parameter: Data class representing a single parameter with name, value, and type.
    
    ParameterRow: UI component representing a single parameter with label and input field.
    Handles focus, editing, and value update events.
    
    ParameterSet: Container for a node's parameters, including title and parameter rows.
    Manages parameter selection and value conversion.
    
    ParameterWindow: Main scrollable container managing multiple ParameterSets.
    Provides keyboard navigation (up/down/enter), editing capabilities,
    and parameter set management (ctrl+x to remove, ctrl+c to clear all).
"""


@dataclass
class Parameter:
    name: str
    value: str
    type: str


class ParameterRow(Horizontal):
    DEFAULT_CSS = """
        ParameterRow {
            height: 3;
            margin: 0;
            padding: 0;
            width: 100%;
        }
        
        ParameterRow > Static {
            width: 20;
            background: $surface;
            color: $text-muted;
            padding: 0 1;
        }
        
        ParameterRow Input.-text-input {
            width: 1fr;
            background: $surface-darken-1;
            color: $text;
            border: none;
            padding: 0 1;
        }
        
        ParameterRow Input.-text-input:hover {
            background: $surface;
            border: tall $primary-darken-2;
        }
        
        ParameterRow Input.-text-input:focus {
            background: $surface-lighten-1;
            color: $text;
            border: tall $primary;
        }

        ParameterRow Input.-text-input.-invalid {
            background: $error-darken-2;
            color: $text-error;
            border: tall $error;
        }

        ParameterRow Input.-text-input:disabled {
            background: $surface-darken-2;
            color: $text-disabled;
        }
        
        Input {
            background: $surface-darken-1;
            color: $text;
        }

        ParameterRow.-selected > Input {
            background: $primary-muted;
            color: $text-primary;
        }
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
        #logger.info(f"ParameterRow.__init__: name={name}, value={value}")

    def compose(self):
        yield Static(f"{self.name}:", classes="label")
        input_widget = Input(value=self._original_value, id=f"input_{self.name}")
        input_widget.can_focus = True
        yield input_widget


    def watch_is_selected(self, selected: bool) -> None:
        self.set_class(selected, "-selected")

    def on_focus(self, event: Focus) -> None:
        logger.info(f"ParameterRow.on_focus: {self.name}")
        try:
            if not self._editing:
                input_widget = self.query_one(Input)
                self._editing = True
                input_widget.value = ""
                # Find parent ParameterWindow and update its border
                param_window = self.ancestors_with_type(ParameterWindow)[0]
                param_window.border = "double"
                logger.info(f"Focus: Updated ParameterWindow border, cleared input for editing. Original value: {self._original_value}")
        except IndexError as e:
            logger.error(f"Could not find parent ParameterWindow: {str(e)}")
        except Exception as e:
            logger.error(f"Error in ParameterRow.on_focus: {str(e)}")

    def on_blur(self, event: Blur) -> None:
        logger.info(f"ParameterRow.on_blur: {self.name}")
        try:
            input_widget = self.query_one(Input)
            if not input_widget.value:
                input_widget.value = self._original_value
            self._editing = False
            # Find parent ParameterWindow and update its border
            param_window = self.ancestors_with_type(ParameterWindow)[0]
            param_window.border = "solid"
        except IndexError as e:
            logger.error(f"Could not find parent ParameterWindow: {str(e)}")
        except Exception as e:
            logger.error(f"Error in ParameterRow.on_blur: {str(e)}")

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

    def update_value(self, new_value: str) -> None:
        self._original_value = str(new_value)
        self.value = str(new_value)
        input_widget = self.query_one(Input)
        input_widget.value = str(new_value)

    # def watch_is_selected(self, selected: bool) -> None:
    #     input_widget = self.query_one(Input)
    #     input_widget.styles.background = pal.PARAM_INPUT_SELECTED_BG if selected else pal.PARAM_INPUT_BG
    #     input_widget.styles.color = pal.PARAM_INPUT_SELECTED_COLOR if selected else pal.PARAM_INPUT_COLOR

class ParameterSet(Vertical):
    """A container for a node's parameters with title and parameter rows."""
    
    DEFAULT_CSS = """
    ParameterSet {
        width: 100%;
        background: $background;
        border-bottom: solid $primary;
        padding: 0 1;
        height: auto;
    }
    
    ParameterSet .title {
        color: $secondary;
        text-style: bold;
        padding: 1 0;
    }
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
                for row in self.parameter_rows:
                    if row.name == parm_name:
                        row.update_value(new_value)
                        break
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
    DEFAULT_CSS = """
    ParameterWindow {
        width: 100%;
        height: 100%;
        background: $background;
    }
    
    ParameterWindow #parameter_stack {
        width: 100%;
        height: auto;
    }

    """

    BINDINGS = [
        Binding("up", "move_up", "Move Up"),
        Binding("down", "move_down", "Move Down"),
        Binding("enter", "edit_value", "Edit Value"),
        Binding("escape", "cancel_edit", "Cancel Edit"),
        Binding("pageup", "scroll_up", "Scroll Up"),
        Binding("pagedown", "scroll_down", "Scroll Down"),
        Binding("ctrl+x", "remove_current_set", "Remove Current Set"),
        Binding("ctrl+f", "clear_all_sets", "Clear All Sets"),
    ]
    
    can_focus = True

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
        logger.debug(f"ParameterWindow gained focus (is_editing: {self.is_editing}, has_focus: {self.has_focus})")
        if self.parameter_sets and not self.is_editing:
            if self.current_set_index == -1:
                self.current_set_index = 0
                self.parameter_sets[0].select_parameter(0)

    def on_blur(self, event: Blur) -> None:
        logger.debug(f"ParameterWindow lost focus (is_editing: {self.is_editing}, has_focus: {self.has_focus}, focused: {self.screen.focused})")


    def parm_refresh(self) -> None:
        if not self.parameter_sets:
            return
            
        for param_set in self.parameter_sets:
            node = param_set.node
            for row in param_set.parameter_rows:
                if parm := node._parms.get(row.name):
                    row.update_value(str(parm._value))

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
            stack = self.query_one("#parameter_stack")
            # Use full path instead of just name
            node_key = node.path()  # Changed from node.name()
            if node_key in self.node_to_param_set:
                old_param_set = self.node_to_param_set[node_key]
                self.parameter_sets.remove(old_param_set)
                old_param_set.remove()

            new_param_set = ParameterSet(node)
            self.parameter_sets.insert(0, new_param_set)
            self.stack.mount(new_param_set, before=0)
            self.node_to_param_set[node_key] = new_param_set  # Using full path here too
            self.current_set_index = 0
            new_param_set.select_parameter(0)
            
            stack.styles.offset = (0, 0)

            logger.info(f"Added/Updated parameter set for {node_key}, total sets: {len(self.parameter_sets)}")
        except Exception as e:
            logger.error(f"Error processing parameter set: {str(e)}")

    def remove_named_set(self, node_path: str) -> None:
        logger.debug(f"Attempting to remove parameter set for node: {node_path}")
        
        try:
            if node_path in self.node_to_param_set:
                param_set = self.node_to_param_set[node_path]
                set_index = self.parameter_sets.index(param_set)
                param_set.remove()
                self.parameter_sets.pop(set_index)
                self.node_to_param_set.pop(node_path)
                
                # Update selection
                if not self.parameter_sets:
                    self.current_set_index = -1
                    self.is_editing = False
                elif set_index <= self.current_set_index:
                    self.current_set_index = max(0, min(self.current_set_index - 1, len(self.parameter_sets) - 1))
                    
            else:
                logger.debug(f"No parameter set found for node path: {node_path}")
                
        except Exception as e:
            logger.error(f"Error removing parameter set: {str(e)}", exc_info=True)

    def clear_all_sets(self) -> None:
        if self.is_editing:
            return
            
        stack = self.query_one("#parameter_stack")
        
        for param_set in self.parameter_sets:
            param_set.remove()
            
        self.parameter_sets = []
        self.current_set_index = -1
        self.node_to_param_set = {}
        self.is_editing = False
        
        stack.styles.offset = (0, 0)

    def action_remove_current_set(self) -> None:
        if not self.parameter_sets or self.is_editing:
            return

        current_set = self.parameter_sets[self.current_set_index]
        self.remove_named_set(current_set.node.name())

    def action_clear_all_sets(self) -> None:
        self.clear_all_sets()

    def on_node_deleted(self, message: NodeDeleted) -> None:
        logger.debug(f"NodeDeleted message received for node: {message.node_path}")
        try:

            self.remove_named_set(message.node_path)
        except Exception as e:
            logger.error(f"Error in on_node_deleted: {str(e)}", exc_info=True)

    def on_clear_all(self, message: ClearAll) -> None:
        logger.debug("ClearAll message gotten")
        self.clear_all_sets()


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
        logger.debug(f"ParameterWindow entering edit mode (current classes: {self.classes})")
        if not self.parameter_sets or self.is_editing:
            return

        current_set = self.parameter_sets[self.current_set_index]
        if current_set.current_index is not None:
            self.is_editing = True
            current_row = current_set.parameter_rows[current_set.current_index]
            input_widget = current_row.query_one(Input)
            logger.debug("Focusing input widget")
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