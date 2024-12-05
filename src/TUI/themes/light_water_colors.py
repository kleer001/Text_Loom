from textual.theme import Theme

light_water_theme = Theme(
    name="light_water",
    dark=False,
    
    # Core colors
    background="#FFFFFF"    # High contrast bg",
    foreground="#00008B"         # High contrast text",
    primary="#00008B"       # High contrast border",
    secondary="#191970" # High contrast border",
    accent="#ADD8E6" # Medium contrast bg",
    error="#FFE4E1"     # Light red for errors",
    success="#4CAF50"
    warning="#FFA726"
    surface="#E0FFFF"    # Low contrast bg",
    panel="#ADD8E6"  # Medium contrast bg",
    
    variables={
        "text-muted": "#0000CD"         # Medium contrast text",
        "text-on-primary": "#FFFFFF"         # Pure white",
        "text-on-secondary": "#FFFFFF"
        
        "border-primary": "solid $primary",
        "border-secondary": "solid $secondary",
        "border-focus": "double $secondary",
        "border-modal": "thick $primary",
        
        "background-input": "$panel",
        "background-input-selected": "$accent",
        "background-input-invalid": "rgba(217, 48, 37, 0.1)",
        "background-editing": "$primary 10%",
        "background-help": "#ADD8E6"       # Medium contrast bg",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "#00008B"     # High contrast border",
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }
)
