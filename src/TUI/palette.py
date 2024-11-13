from textual.color import Color

class TUIColors:
    WHITE = Color.parse("white")
    BLACK = Color.parse("black")
    BLUE = Color.parse("blue")
    LIGHT_GRAY = Color.parse("#f8f8f2")
    DARK_GRAY = Color.parse("#303030")
    HIGHLIGHT = Color.parse("#44475a")
    
    MODELINE_FG = WHITE
    MODELINE_BG = BLUE
    
    ACTIVE_WINDOW_FG = BLACK
    ACTIVE_WINDOW_BG = Color.parse("#e6e6e6")  # Equivalent to 230
    
    INACTIVE_WINDOW_FG = Color.parse("#a8a8a8")  # Equivalent to 248
    INACTIVE_WINDOW_BG = Color.parse("#444444")  # Equivalent to 238
    
    CURSOR_FG = Color.parse("#f7f7f7")  # Equivalent to 231
    CURSOR_BG = BLACK
    
    GUTTER_FG = BLACK
    GUTTER_BG = BLACK