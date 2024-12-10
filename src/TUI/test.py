# Python standard library imports
from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto
import logging
import os
from pathlib import Path
from typing import ClassVar, Dict

# Textual core imports
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Grid, Horizontal, ScrollableContainer, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
from textual.theme import Theme
from textual.widgets import Static, OptionList

# Core application imports
from core.base_classes import NodeEnvironment
from core.flowstate_manager import save_flowstate, load_flowstate
from core.global_store import GlobalStore
from core.undo_manager import UndoManager

# TUI window components
from TUI.global_window import GlobalWindow
from TUI.help_window import HelpWindow
from TUI.node_window import NodeWindow, NodeSelected, Node
from TUI.output_window import OutputWindow
from TUI.parameter_window import ParameterWindow
from TUI.status_window import StatusWindow

# TUI screens and layouts
from TUI.file_screen import FileScreen
from TUI.keymap_screen import KeymapScreen
from TUI.main_layout import MainLayout, MainContent
from TUI.clear_all_modal import ClearAllConfirmation

# TUI theme related
from TUI.theme_collection import create_themes
from TUI.theme_manager import ThemeManager
from TUI.theme_selector import ThemeSelector

# TUI utilities and configuration
from TUI.logging_config import get_logger
from TUI.modeline import ModeLine
from TUI.screens_registry import (
    Mode,
    get_screen_registry,
    MAIN_SCREEN,
    FILE_SCREEN,
    KEYMAP_SCREEN,
)

# TUI messages
from TUI.messages import (
    OutputMessage,
    NodeAdded,
    NodeDeleted,
    ConnectionAdded,
    ConnectionDeleted,
    ParameterChanged,
    GlobalAdded,
    GlobalChanged,
    GlobalDeleted,
    NodeSelected,
    FileLoaded,
)