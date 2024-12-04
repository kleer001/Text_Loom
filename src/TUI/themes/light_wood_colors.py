from textual.theme import Theme

light_wood_theme = Theme(
    name="light_wood",
    dark=False,
    
    # Core colors
    background="#F0FFF0"    # High contrast bg",
    foreground="#006400"          # Medium contrast text",
    primary="#8FBC8F"        # Medium contrast border",
    secondary="#008000"  # High contrast border",
    accent="#DFFFDF"  # Medium contrast bg",
    error="#D93025"       # Keeping red for errors",
    success="#4CAF50
    warning="#FFA726
    surface="#E0FFE0"     # Low contrast bg",
    panel="#FFFFFF"   # Pure white",
    
    variables={
        "text-muted": "#228B22"           # Low contrast text",
        "text-on-primary": "#FFFFFF"          # Pure white",
        "text-on-secondary": "#FFFFFF"
        
        "border-primary": "solid $primary",
        "border-secondary": "solid $secondary",
        "border-focus": "double $secondary",
        "border-modal": "thick $primary",
        
        "background-input": "$panel",
        "background-input-selected": "$accent",
        "background-input-invalid": "rgba(217, 48, 37, 0.1)",
        "background-editing": "$primary 10%",
        "background-help": "#DFFFDF"         # Medium contrast bg",
        
        "modeline-bg": "$secondary",
        "modeline-fg": "$text-on-secondary",
        
        "node-selected-bg": "$accent",
        "node-selected-fg": "$foreground",
        
        "param-title": "$secondary",
        "param-label-bg": "$surface",
        "param-label-fg": "$text-muted",
        
        "input-border": "#9ACD32"      # Low contrast border",
        "input-border-focus": "$primary",
        "input-border-invalid": "$error",
        
        "window-border-normal": "$border-primary",
        "window-border-focus": "$border-focus",
        
        "table-border": "$primary",
        "table-header-bg": "$primary 15%",
        "table-alternate-bg": "$surface",
    }
)
