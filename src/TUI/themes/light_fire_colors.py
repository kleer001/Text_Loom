from textual.theme import Theme

light_fire_theme = Theme(
    name="light_fire",
    dark=False,
    
    # Core colors
    background="#FFFFFF"    # High contrast bg",
    foreground="#B22222"         # Medium contrast text",
    primary="#FF4500"       # Low contrast border",
    secondary="#FF0000" # Medium contrast border",
    accent="#FFF0F5" # Medium contrast bg",
    error="#8B0000"     # High contrast text for errors",
    success="#4CAF50"
    warning="#FFA726"
    surface="#FFFAFA"    # Low contrast bg",
    panel="#FFF0F5"  # Medium contrast bg",
    
    variables={
        "text-muted": "#DC143C"         # Low contrast text",
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
        "background-help": "#FFF0F5"       # Medium contrast bg",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "#FF4500"     # Low contrast border",
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }
)
