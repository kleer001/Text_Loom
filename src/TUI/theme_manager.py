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
    "Tui_Skeleton-0": """
            Tui_Skeleton {
            MainLayout {{
                    height: 100%;
                    width: 100%;
                    grid-size: 3 1;
                    grid-columns: 1fr 2fr 2fr;
                    grid-rows: 1fr;
                    grid-gutter: 0;
                    background: {theme.MAIN_WIN_BACKGROUND};
                    color: {theme.MAIN_WIN_TEXT};
                }}
                
                Vertical {{
                    height: 100%;
                    width: 100%;
                }}
            }
""",
    "Tui_Skeleton-1": """
            Tui_Skeleton {
            ClearAllConfirmation {{
                    align: center middle;
                }}
                Vertical {{
                    width: 40;
                    height: auto;
                    border: {theme.NODE_BORDER_MODAL} {theme.NODE_MODAL_BORDER};
                    background: {theme.NODE_MODAL_SURFACE};
                    color: {theme.NODE_MODAL_TEXT};
                    padding: 1;
                }}
                Static {{
                    text-align: center;
                    width: 100%;
                }}
            }
""",
    "ModeLine-0": """
            ModeLine {{
                    width: 100%;
                    height: 1;
                    background: {theme.MODELINE_BACKGROUND};
                    color: {theme.MODELINE_TEXT};
                    padding: 0 1;
                }}
""",
    "GlobalWindow-0": """
            GlobalWindow {{
                    width: 100%;
                    height: 20%;
                    background: {theme.GLOBAL_WIN_BACKGROUND_COLOR};
                    border: heavy {theme.GLOBAL_WIN_BORDER_COLOR};
                    layout: vertical;
                }}
            
                DataTable {{
                    width: 100%;
                    height: 1fr;
                    background: {theme.GLOBAL_WIN_TABLE_COLOR};
                    color: {theme.GLOBAL_WIN_TEXT_COLOR};
                    overflow: auto scroll;
                    scrollbar-gutter: stable;
                }}
            
                Input {{
                    width: 100%;
                    height: 3;
                    dock: top;
                    background: {theme.GLOBAL_WIN_INPUT_COLOR};
                    color: {theme.GLOBAL_WIN_TEXT_COLOR};
                    border: solid {theme.GLOBAL_WIN_BORDER_COLOR};
                }}
""",
    "NodeWindow-0": """
            NodeWindow {
            NodeTypeSelector {{
                    align: center middle;
                }}
            
                Vertical {{
                    width: 40;
                    height: auto;
                    border: {theme.NODE_BORDER_MODAL} {theme.NODE_MODAL_BORDER};
                    background: {theme.NODE_MODAL_SURFACE};
                    color: {theme.NODE_MODAL_TEXT};
                }}
            
                OptionList {{
                    height: auto;
                    max-height: 20;
                }}
            }
""",
    "NodeWindow-1": """
            NodeWindow {
            DeleteConfirmation {{
                    align: center middle;
                }}
            
                Vertical {{
                    width: 40;
                    height: auto;
                    border: {theme.NODE_BORDER_MODAL} {theme.NODE_MODAL_BORDER};
                    background: {theme.NODE_MODAL_SURFACE};
                    color: {theme.NODE_MODAL_TEXT};
                    padding: 1;
                }}
            
                Static {{
                    text-align: center;
                    width: 100%;
                }}
            }
""",
    "NodeWindow-2": """
            NodeWindow {
            RenameInput {{
                    height: 3;
                    background: {theme.NODE_INPUT_BACKGROUND};
                    color: {theme.NODE_INPUT_TEXT}
                    border: none;
                    padding: 0;
                }}
            }
""",
    "NodeWindow-3": """
            NodeWindow {{
                        width: 100%;
                        height: 100%;
                        background: {theme.NODE_WIN_BACKGROUND};
                        border: {theme.NODE_BORDER_NORMAL} {theme.NODE_WIN_BORDER};
                        color: {theme.NODE_MODAL_TEXT};
                    }}
            
                    NodeWindow:focus {{
                        border: {theme.NODE_BORDER_FOCUS} {theme.NODE_WIN_BORDER_FOCUS};
                    }}
            
                    NodeContent {{
                        width: 100%;
                        padding: 0 1;
                    }}
""",
    "FileScreen-0": """
            FileScreen {
            FileMode {
                    height: auto;
                    dock: bottom;
                    padding: 0 1;
                }
                
                Input {
                    width: 100%;
                    border: solid $primary;
                }
            }
""",
    "FileScreen-1": """
            FileScreen {
                    align: center middle;
                    width: 100%;
                    height: 100%;
                }
                
                DirectoryTree {
                    width: 100%;
                    height: 1fr;
                    border: solid $primary;
                }
""",
    "HelpWindow-0": """
            HelpWindow {{
                    width: 100%;
                    height: 12.5%;
                    background: {theme.HELP_WIN_BACKGROUND};
                }}
                
                DataTable {{
                    height: 100%;
                    border: none;
                    background: {theme.HELP_WIN_BACKGROUND};
                    color: {theme.HELP_WIN_TEXT};
                }}
            
                DataTable > .datatable--cell {{
                    background: {theme.HELP_WIN_BACKGROUND};
                }}
                
                DataTable > .datatable--header-cell {{
                    background: {theme.HELP_WIN_BACKGROUND};
                }}
""",
    "ParameterWindow-0": """
            ParameterWindow {
            ParameterRow {{
                    height: 2;
                    margin: 0;
                    padding: 0;
                    width: 100%;
                }}
                
                ParameterRow > Static {{
                    width: 20;
                    background: {theme.PARAM_LABEL_BG};
                    color: {theme.PARAM_LABEL_COLOR};
                    padding: 0 1;
                }}
                
                ParameterRow > Input {{
                    width: 1fr;
                    background: {theme.PARAM_INPUT_BG};
                    color: {theme.PARAM_INPUT_COLOR};
                    border: none;
                    padding: 0 1;
                }}
                
                ParameterRow > Input:focus {{
                    background: {theme.PARAM_INPUT_SELECTED_BG};
                    color: {theme.PARAM_INPUT_SELECTED_COLOR};
                    border: tall {theme.PARAM_INPUT_SELECTED_BORDER};
                }}
            }
""",
    "ParameterWindow-1": """
            ParameterWindow {
            ParameterSet {{
                    width: 100%;
                    background: {theme.PARAM_SET_BG};
                    border-bottom: solid {theme.PARAM_SET_BORDER};
                    padding: 0 1;
                    height: auto;
                }}
                
                ParameterSet .title {{
                    color: {theme.PARAM_TITLE_COLOR};
                    text-style: bold;
                    padding: 1 0;
                }}
            }
""",
    "ParameterWindow-2": """
            ParameterWindow {{
                    width: 100%;
                    height: 100%;
                    background: {theme.PARAM_WINDOW_BG};
                    border: solid {theme.PARAM_WINDOW_BORDER};
                }}
                
                ParameterWindow:focus {{
                    border: double {theme.PARAM_WINDOW_FOCUS_BORDER};
                }}
                
                ParameterWindow #parameter_stack {{
                    width: 100%;
                    height: auto;
                }}
""",
    "StatusWindow-0": """
            StatusWindow {{
                    width: 100%;
                    height: 30%;
                    background: {theme.STATUS_WIN_BACKGROUND};
                    border: {theme.STATUS_WIN_BORDER} {theme.STATUS_WIN_BORDER_COLOR};
                    color: {theme.STATUS_WIN_TEXT};
                    padding: 0 1;
                    overflow-y: scroll;
                }}
""",
    "KeymapScreen-0": """
            KeymapScreen {{
                    align: center middle;
                    background: {theme.KEYMAP_SCR_BACKGROUND};
                    color: {theme.KEYMAP_SCR_TEXT};
                    width: 100%;
                    height: 100%;
                }}
            
                .keymap-content {{
                    width: 100%;
                    height: 100%;
                    content-align: center middle;
                    background: {theme.KEYMAPCONTENT_SCR_BACKGROUND};
                    color: {theme.KEYMAPCONTENT_SCR_TEXT}; 
                }}
""",
    "OutputWindow-0": """
            OutputWindow {{
                    width: 100%;
                    height: 50%;
                    background: {theme.OUTPUT_WIN_BACKGROUND};
                    border: {theme.OUTPUT_WIN_BORDER} {theme.OUTPUT_WIN_BORDER_COLOR};
                    color: {theme.OUTPUT_WIN_TEXT};
                    padding: 1;
                }}
""",
        }
