from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List
import importlib.util

@dataclass
class Theme:
    GLOBAL_WIN_BACKGROUND_COLOR: str
    GLOBAL_WIN_BORDER_COLOR: str
    GLOBAL_WIN_INPUT_COLOR: str
    GLOBAL_WIN_TABLE_COLOR: str
    GLOBAL_WIN_TEXT_COLOR: str
    HELP_WIN_BACKGROUND: str
    HELP_WIN_TEXT: str
    KEYMAPCONTENT_SCR_BACKGROUND: str
    KEYMAPCONTENT_SCR_TEXT: str
    KEYMAP_SCR_BACKGROUND: str
    KEYMAP_SCR_TEXT: str
    MAIN_WIN_BACKGROUND: str
    MAIN_WIN_TEXT: str
    MODELINE_BACKGROUND: str
    MODELINE_TEXT: str
    NODE_BORDER_FOCUS: str
    NODE_BORDER_MODAL: str
    NODE_BORDER_NORMAL: str
    NODE_INPUT_BACKGROUND: str
    NODE_INPUT_TEXT: str
    NODE_MODAL_BORDER: str
    NODE_MODAL_SURFACE: str
    NODE_MODAL_TEXT: str
    NODE_WIN_BACKGROUND: str
    NODE_WIN_BORDER: str
    NODE_WIN_BORDER_FOCUS: str
    OUTPUT_WIN_BACKGROUND: str
    OUTPUT_WIN_BORDER: str
    OUTPUT_WIN_BORDER_COLOR: str
    OUTPUT_WIN_TEXT: str
    PARAM_INPUT_BG: str
    PARAM_INPUT_COLOR: str
    PARAM_INPUT_SELECTED_BG: str
    PARAM_INPUT_SELECTED_BORDER: str
    PARAM_INPUT_SELECTED_COLOR: str
    PARAM_LABEL_BG: str
    PARAM_LABEL_COLOR: str
    PARAM_SET_BG: str
    PARAM_SET_BORDER: str
    PARAM_TITLE_COLOR: str
    PARAM_WINDOW_BG: str
    PARAM_WINDOW_BORDER: str
    PARAM_WINDOW_FOCUS_BORDER: str
    STATUS_WIN_BACKGROUND: str
    STATUS_WIN_BORDER: str
    STATUS_WIN_BORDER_COLOR: str
    STATUS_WIN_TEXT: str

def load_theme_module(path: Path):
   """Dynamically import theme module from path"""
   spec = importlib.util.spec_from_file_location(path.stem, path)
   module = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(module)
   return module

class ThemeManager:
   @staticmethod
   def get_available_themes() -> List[str]:
       """Get list of available theme names from themes directory"""
       theme_dir = Path(__file__).parent / "themes"
       return [p.stem.replace("_colors", "") for p in theme_dir.glob("*_colors.py")]
       
   @staticmethod
   def load_theme(theme_name: str) -> Theme:
       """Load theme by name from themes directory"""
       theme_path = Path(__file__).parent / "themes" / f"{theme_name}_colors.py"
       if not theme_path.exists():
           raise ValueError(f"Theme {theme_name} not found")
       
       theme_module = load_theme_module(theme_path)
       return Theme(**{var: getattr(theme_module, var) for var in Theme.__annotations__})

   @staticmethod
   def get_css(theme: Theme) -> Dict[str, str]:
       """Generate CSS for all components using theme"""
       return {
    'tui_skeleton': '''
    ClearAllConfirmation {{
        align: "center middle";
    }}
    Vertical {{
        width: 40;
        height: "auto";
        border: {pal.NODE_BORDER_MODAL} {pal.NODE_MODAL_BORDER};
        background: {pal.NODE_MODAL_SURFACE};
        color: {pal.NODE_MODAL_TEXT};
        padding: 1;
    }}
    Static {{
        text-align: "center";
        width: 100%;
    }}
    ''',
    'tui_skeleton': '''
    MainLayout {{
        height: 100%;
        width: 100%;
        grid-size: 3 1;
        grid-columns: 1fr 2fr 2fr;
        grid-rows: 1fr;
        grid-gutter: 0;
        background: {pal.MAIN_WIN_BACKGROUND};
        color: {pal.MAIN_WIN_TEXT};
    }}
    
    Vertical {{
        height: 100%;
        width: 100%;
    }}
    ''',
    'modeline': '''
    ModeLine {{
        width: 100%;
        height: 1;
        background: {pal.MODELINE_BACKGROUND};
        color: {pal.MODELINE_TEXT};
        padding: 0 1;
    }}
    ''',
    'global_window': '''
    GlobalWindow {{
        width: 100%;
        height: 20%;
        background: {pal.GLOBAL_WIN_BACKGROUND_COLOR};
        border: heavy {pal.GLOBAL_WIN_BORDER_COLOR};
        layout: "vertical";
    }}

    DataTable {{
        width: 100%;
        height: 1fr;
        background: {pal.GLOBAL_WIN_TABLE_COLOR};
        color: {pal.GLOBAL_WIN_TEXT_COLOR};
        overflow: auto scroll;
        scrollbar-gutter: stable;
    }}

    Input {{
        width: 100%;
        height: 3;
        dock: "top";
        background: {pal.GLOBAL_WIN_INPUT_COLOR};
        color: {pal.GLOBAL_WIN_TEXT_COLOR};
        border: solid {pal.GLOBAL_WIN_BORDER_COLOR};
    }}
    ''',
    'node_window': '''
    NodeTypeSelector {{
        align: "center middle";
    }}

    Vertical {{
        width: 40;
        height: "auto";
        border: {pal.NODE_BORDER_MODAL} {pal.NODE_MODAL_BORDER};
        background: {pal.NODE_MODAL_SURFACE};
        color: {pal.NODE_MODAL_TEXT};
    }}

    OptionList {{
        height: "auto";
        max-height: 20;
    }}
    ''',
    'node_window': '''
        NodeWindow {{
            width: 100%;
            height: 100%;
            background: {pal.NODE_WIN_BACKGROUND};
            border: {pal.NODE_BORDER_NORMAL} {pal.NODE_WIN_BORDER};
            color: {pal.NODE_MODAL_TEXT};
        }}

        NodeWindow:focus {{
            border: {pal.NODE_BORDER_FOCUS} {pal.NODE_WIN_BORDER_FOCUS};
        }}

        NodeContent {{
            width: 100%;
            padding: 0 1;
        }}
        ''',
    'node_window': '''
    DeleteConfirmation {{
        align: "center middle";
    }}

    Vertical {{
        width: 40;
        height: "auto";
        border: {pal.NODE_BORDER_MODAL} {pal.NODE_MODAL_BORDER};
        background: {pal.NODE_MODAL_SURFACE};
        color: {pal.NODE_MODAL_TEXT};
        padding: 1;
    }}

    Static {{
        text-align: "center";
        width: 100%;
    }}
    ''',
    'node_window': '''
    RenameInput {{
        height: 3;
        background: {pal.NODE_INPUT_BACKGROUND};
        color: {pal.NODE_INPUT_TEXT}
        border: none;
        padding: 0;
    }}
    ''',
    'file_screen': '''
    FileMode {
        height: "auto";
        dock: "bottom";
        padding: 0 1;
    }
    
    Input {
        width: 100%;
        border: solid $primary;
    }
    ''',
    'file_screen': '''
    FileScreen {
        align: "center middle";
        width: 100%;
        height: 100%;
    }
    
    DirectoryTree {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }
    ''',
    'help_window': '''
    HelpWindow {{
        width: 100%;
        height: 12.5%;
        background: {pal.HELP_WIN_BACKGROUND};
    }}
    
    DataTable {{
        height: 100%;
        border: none;
        background: {pal.HELP_WIN_BACKGROUND};
        color: {pal.HELP_WIN_TEXT};
    }}

    DataTable > .datatable--cell {{
        background: {pal.HELP_WIN_BACKGROUND};
    }}
    
    DataTable > .datatable--header-cell {{
        background: {pal.HELP_WIN_BACKGROUND};
    }}
    ''',
    'parameter_window': '''
    ParameterSet {{
        width: 100%;
        background: {pal.PARAM_SET_BG};
        border-bottom: solid {pal.PARAM_SET_BORDER};
        padding: 0 1;
        height: "auto";
    }}
    
    ParameterSet .title {{
        color: {pal.PARAM_TITLE_COLOR};
        text-style: bold;
        padding: 1 0;
    }}
    ''',
    'parameter_window': '''
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
    ''',
    'parameter_window': '''
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
        height: "auto";
    }}
    ''',
    'status_window': '''
    StatusWindow {{
        width: 100%;
        height: 30%;
        background: {pal.STATUS_WIN_BACKGROUND};
        border: {pal.STATUS_WIN_BORDER} {pal.STATUS_WIN_BORDER_COLOR};
        color: {pal.STATUS_WIN_TEXT};
        padding: 0 1;
        overflow-y: scroll;
    }}
    ''',
    'keymap_screen': '''
    KeymapScreen {{
        align: "center middle";
        background: {pal.KEYMAP_SCR_BACKGROUND};
        color: {pal.KEYMAP_SCR_TEXT};
        width: 100%;
        height: 100%;
    }}

    .keymap-content {{
        width: 100%;
        height: 100%;
        content-align: "center middle";
        background: {pal.KEYMAPCONTENT_SCR_BACKGROUND};
        color: {pal.KEYMAPCONTENT_SCR_TEXT}; 
    }}
    ''',
    'output_window': '''
    OutputWindow {{
        width: 100%;
        height: 50%;
        background: {pal.OUTPUT_WIN_BACKGROUND};
        border: {pal.OUTPUT_WIN_BORDER} {pal.OUTPUT_WIN_BORDER_COLOR};
        color: {pal.OUTPUT_WIN_TEXT};
        padding: 1;
    }}
    ''',
       }
