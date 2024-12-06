from textual.theme import Theme

def create_themes():
    return {
        "default": Theme(
            name="default",
            dark=False,
            background="#FAFAF8",
            foreground="#222222",
            primary="#486591",
            secondary="#2C4975",
            accent="#BBBBF7",
            error="#D93025",
            success="#4CAF50",
            warning="#FFA726",
            surface="#F5F5F2",
            panel="#FFFFFF",
        ),
        "light_fire": Theme(
            name="light_fire",
            dark=False,
            background="#FFFFFF",
            foreground="#B22222",
            primary="#FF4500",
            secondary="#FF0000",
            accent="#FFF0F5",
            error="#8B0000",
            success="#4CAF50",
            warning="#FFA726",
            surface="#FFFAFA",
            panel="#FFF0F5",
        ),
        "light_metal": Theme(
            name="light_metal",
            dark=False,
            background="#FFFFFF",
            foreground="#696969",
            primary="#D3D3D3",
            secondary="#C0C0C0",
            accent="#E0FFFF",
            error="#FFE4E1",
            success="#4CAF50",
            warning="#FFA726",
            surface="#F0F8FF",
            panel="#E0FFFF",
        ),
        "light_earth": Theme(
            name="light_earth",
            dark=False,
            background="#FFFFFF",
            foreground="#8B4513",
            primary="#CD853F",
            secondary="#D2691E",
            accent="#FFF5EE",
            error="#8B0000",
            success="#4CAF50",
            warning="#FFA726",
            surface="#FFF8DC",
            panel="#FFF5EE",
        ),
        "light_wood": Theme(
            name="light_wood",
            dark=False,
            background="#F0FFF0",
            foreground="#006400",
            primary="#8FBC8F",
            secondary="#008000",
            accent="#DFFFDF",
            error="#D93025",
            success="#4CAF50",
            warning="#FFA726",
            surface="#E0FFE0",
            panel="#FFFFFF",
        ),
        "light_water": Theme(
            name="light_water",
            dark=False,
            background="#FFFFFF",
            foreground="#00008B",
            primary="#00008B",
            secondary="#191970",
            accent="#ADD8E6",
            error="#FFE4E1",
            success="#4CAF50",
            warning="#FFA726",
            surface="#E0FFFF",
            panel="#ADD8E6",
        ),
        "dark_fire": Theme(
            name="dark_fire",
            dark=True,
            background="#191919",
            foreground="#FFA500",
            primary="#8B0000",
            secondary="#B22222",
            accent="#191919",
            error="#8B0000",
            success="#4CAF50",
            warning="#FFA726",
            surface="#222222",
            panel="#222222",
        ),
        "dark_metal": Theme(
            name="dark_metal",
            dark=True,
            background="#222222",
            foreground="#D3D3D3",
            primary="#708090",
            secondary="#696969",
            accent="#222222",
            error="#8B0000",
            success="#4CAF50",
            warning="#FFA726",
            surface="#191919",
            panel="#191919",
        ),
        "dark_earth": Theme(
            name="dark_earth",
            dark=True,
            background="#191919",
            foreground="#F5DEB3",
            primary="#8B4513",
            secondary="#CD853F",
            accent="#191919",
            error="#8B0000",
            success="#4CAF50",
            warning="#FFA726",
            surface="#222222",
            panel="#222222",
        ),
        "dark_wood": Theme(
            name="dark_wood",
            dark=True,
            background="#191919",
            foreground="#90EE90",  # Light green
            primary="#228B22",     # Forest green
            secondary="#006400",   # Dark green
            accent="#191919",
            error="#8B0000",
            success="#4CAF50",
            warning="#FFA726",
            surface="#222222",
            panel="#222222",
        ),
        "dark_water": Theme(
            name="dark_water",
            dark=True,
            background="#191919",
            foreground="#87CEFA",
            primary="#00008B",
            secondary="#0000CD",
            accent="#191919",
            error="#8B0000",
            success="#4CAF50",
            warning="#FFA726",
            surface="#222222",
            panel="#222222",
        ),

    "light_vata": Theme(
        name="light_vata",
        dark=False,
        background="#FFF8E7",  # Ethereal light
        foreground="#FF4D00",  # Bright fire
        primary="#FFB366",     # Warm orange
        secondary="#FF8533",   # Deep orange
        accent="#FFE6CC",      # Soft ether
        error="#D93025",
        success="#4CAF50",
        warning="#FFA726",
        surface="#FFF2D9",
        panel="#FFFFFF",
    ),

    "dark_vata": Theme(
        name="dark_vata",
        dark=True,
        background="#1A0F00",  # Dark ether
        foreground="#FF6600",  # Fire orange
        primary="#CC5200",     # Deep fire
        secondary="#FF8533",   # Bright fire
        accent="#1A0F00",
        error="#8B0000",
        success="#4CAF50",
        warning="#FFA726",
        surface="#261500",
        panel="#261500",
    ),

    "light_pitta": Theme(
        name="light_pitta",
        dark=False,
        background="#FFF0E6",  # Warm light
        foreground="#0066CC",  # Water blue
        primary="#FF3300",     # Fire red
        secondary="#0099FF",   # Bright water
        accent="#E6F7FF",      # Light water
        error="#D93025",
        success="#4CAF50",
        warning="#FFA726",
        surface="#FFE6D9",
        panel="#FFFFFF",
    ),

    "dark_pitta": Theme(
        name="dark_pitta",
        dark=True,
        background="#000D1A",  # Deep water
        foreground="#FF4D00",  # Fire orange
        primary="#0080FF",     # Water blue
        secondary="#FF3300",   # Fire red
        accent="#000D1A",
        error="#8B0000",
        success="#4CAF50",
        warning="#FFA726",
        surface="#001529",
        panel="#001529",
    ),

    "light_kapha": Theme(
        name="light_kapha",
        dark=False,
        background="#F0FFFF",  # Air light
        foreground="#006699",  # Water blue
        primary="#99CCFF",     # Air blue
        secondary="#0099CC",   # Water blue
        accent="#E6FFFF",      # Light air
        error="#D93025",
        success="#4CAF50",
        warning="#FFA726",
        surface="#E6FFFF",
        panel="#FFFFFF",
    ),

    "dark_kapha": Theme(
        name="dark_kapha",
        dark=True,
        background="#000033",  # Deep water
        foreground="#99CCFF",  # Air blue
        primary="#006699",     # Water blue
        secondary="#003366",   # Deep water
        accent="#000033",
        error="#8B0000",
        success="#4CAF50",
        warning="#FFA726",
        surface="#000047",
        panel="#000047",
    ),

    }