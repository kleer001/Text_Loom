from textual.color import Color

class TUIPalette:
    BACKGROUND_BASE = "#1c1c1c"
    BACKGROUND_LIGHT = "#303030"
    FOREGROUND = "#d7d7d7"
    HIGHLIGHT = "#444444"
    BLUE = "#5f87af"
    WHITE = "#d7d7d7"
    BLACK = "#121212"
    GRAY = "#444444"

STYLES = {
    "app": {
        "background": TUIPalette.BLACK,
        "border_title_align": "left",
    },
    
    "Window": {
        "border": f"round {TUIPalette.GRAY}",
        "background": TUIPalette.BACKGROUND_BASE,
    },
    
    "Window.active": {
        "border": f"round {TUIPalette.BLUE}",
        "background": TUIPalette.BACKGROUND_LIGHT,
    },
    
    "ModeLine": {
        "dock": "bottom",
        "height": 1,
        "background": TUIPalette.BLUE,
        "color": TUIPalette.WHITE,
        "padding": (0, 1),
    },
    
    "HelpMode": {
        "dock": "bottom",
        "height": "12%",
        "border": f"round {TUIPalette.GRAY}",
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "padding": (0, 1),
    },
    
    "NodeMode": {
        "width": "20%",
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
    },
    
    "ParameterMode": {
        "dock": "right",
        "width": "40%",
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
    },
    
    "StatusMode": {
        "height": "50%",
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
    },
    
    "OutputMode": {
        "height": "25%",
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
    },
    
    "GlobalMode": {
        "height": "25%",
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
    },
    
    "FileMode": {
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
    },
    
    "KeymapMode": {
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
    },
    
    "ParameterWidget": {
        "height": "auto",
        "background": TUIPalette.BACKGROUND_BASE,
        "color": TUIPalette.FOREGROUND,
        "border": f"round {TUIPalette.GRAY}",
        "margin": (0, 0, 1, 0),
    },
    
    "ParameterWidget.active": {
        "border": f"round {TUIPalette.BLUE}",
        "background": TUIPalette.BACKGROUND_LIGHT,
    },
    
    "ScrollableContainer": {
        "height": "100%",
        "border": f"round {TUIPalette.GRAY}",
        "background": TUIPalette.BACKGROUND_BASE,
    }
}