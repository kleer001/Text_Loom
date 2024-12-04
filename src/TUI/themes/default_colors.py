from textual.theme import Theme

default_theme = Theme(
    name="default",
    dark=False,
    
    # Core colors
    background="#FAFAF8
    foreground="#222222
    primary="#486591
    secondary="#2C4975
    accent="#EDF2F7
    error="#D93025
    success="#4CAF50
    warning="#FFA726
    surface="#F5F5F2
    panel="#FFFFFF
    
    variables={
        "text-muted": "#444444
        "text-on-primary": "#FFFFFF"
        "text-on-secondary": "#FFFFFF"
        
        "border-primary": "solid $primary",
        "border-secondary": "solid $secondary",
        "border-focus": "double $secondary",
        "border-modal": "thick $primary",
        
        "background-input": "$panel",
        "background-input-selected": "$accent",
        "background-input-invalid": "rgba(217, 48, 37, 0.1)",
        "background-editing": "$primary 10%",
        "background-help": "$primary 5%",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "#D0D0D0
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }
)
