from textual.theme import Theme

light_earth_theme = Theme(
    name="light_earth",
    dark=False,
    
    # Core colors
    background="#FFFFFF"    # High contrast bg",
    foreground="#8B4513"         # High contrast text",
    primary="#CD853F"       # Medium contrast border",
    secondary="#D2691E" # High contrast border",
    accent="#FFF5EE" # Medium contrast bg",
    error="#8B0000"     # Dark red for errors",
    success="#4CAF50
    warning="#FFA726
    surface="#FFF8DC"    # Low contrast bg",
    panel="#FFF5EE"  # Medium contrast bg",
    
    variables={
        "text-muted": "#A0522D"         # Low contrast text",
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
        "background-help": "#FFF5EE"       # Medium contrast bg",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "#CD853F"     # Medium contrast border",
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }
)
