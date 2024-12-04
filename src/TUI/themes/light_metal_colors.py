from textual.theme import Theme

light_metal_theme = Theme(
    name="light_metal",
    dark=False,
    
    # Core colors
    background="#FFFFFF"    # High contrast bg",
    foreground="#696969"         # Medium contrast text",
    primary="#D3D3D3"       # Low contrast border",
    secondary="#C0C0C0" # High contrast border",
    accent="#E0FFFF" # Medium contrast bg",
    error="#FFE4E1"     # Light red for errors",
    success="#4CAF50
    warning="#FFA726
    surface="#F0F8FF"    # Low contrast bg",
    panel="#E0FFFF"  # Medium contrast bg",
    
    variables={
        "text-muted": "#708090"         # Low contrast text",
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
        "background-help": "#E0FFFF"       # Medium contrast bg",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "#D3D3D3"     # Low contrast border",
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }
)
