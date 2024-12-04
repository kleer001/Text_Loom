# src/TUI/theme_loader.py
from pathlib import Path
from typing import List, Dict
import importlib.util
import logging
from dataclasses import dataclass

logger = logging.getLogger('tui.themes')

@dataclass
class ThemeInfo:
    name: str  # Theme name (filename without _colors.py)
    path: Path  # Full path to theme file
    module: object  # The imported module containing colors

class ThemeLoader:
    def __init__(self):
        self.themes_dir = Path(__file__).parent / "themes"
        self.themes: Dict[str, ThemeInfo] = {}
        
    def scan_themes(self) -> List[str]:
        """Scan themes directory for *_colors.py files and load them"""
        self.themes.clear()
        logger.debug(f"Scanning for themes in {self.themes_dir}")
        
        try:
            # Create themes directory if it doesn't exist
            self.themes_dir.mkdir(exist_ok=True)
            
            # Find all *_colors.py files
            for theme_file in self.themes_dir.glob("*_colors.py"):
                theme_name = theme_file.stem.replace('_colors', '')
                logger.debug(f"Found theme file: {theme_file}")
                
                try:
                    # Import the theme module
                    spec = importlib.util.spec_from_file_location(
                        f"TUI.themes.{theme_name}", 
                        theme_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Store theme info
                    self.themes[theme_name] = ThemeInfo(
                        name=theme_name,
                        path=theme_file,
                        module=module
                    )
                    logger.info(f"Successfully loaded theme: {theme_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load theme {theme_name}: {str(e)}")
                    continue
                    
            return list(self.themes.keys())
            
        except Exception as e:
            logger.error(f"Error scanning themes directory: {str(e)}")
            return []
            
    def get_theme(self, theme_name: str) -> ThemeInfo:
        """Get a specific theme by name"""
        return self.themes.get(theme_name)