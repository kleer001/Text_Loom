from textual.theme import Theme

dark_water_theme = Theme(
    name="dark_water",
    dark=False,
    
    # Core colors
    background="#191919"    # Medium contrast bg",
    foreground="#87CEFA"         # Medium contrast text",
    primary="#00008B"       # Low contrast border",
    secondary="#0000CD" # Medium contrast border",
    accent="#191919" # Medium contrast bg",
    error="#8B0000"     # Dark red for errors",
    success="#4CAF50
    warning="#FFA726
    surface="#222222"    # Low contrast bg",
    panel="#222222"  # Low contrast bg",
    
    variables={
        "text-muted": "#ADD8E6"         # Low contrast text",
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
        "background-help": "#191919"       # Medium contrast bg",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "#00008B"     # Low contrast border",
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }
)
