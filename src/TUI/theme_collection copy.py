from textual.theme import Theme

"""
    Huge pile of semi-sorted color palettes for Text_Loom. 
    Probably too many and in a weird organization. 
    They're not saved with the file.
    Which ever one is first in the list is the one that's loaded.
"""

def create_themes():
    return {
        "default_powder": Theme(
            name="default_powder",
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

        "default_slate": Theme(
            name="default_slate",
            dark=True,
            background="#1A1C1E",
            foreground="#D8E1E6",
            primary="#4A6B8C",
            secondary="#2C4C6F",
            accent="#1A1C1E",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#22262A",
            panel="#2A2E32",
        ),

        "default_parchment": Theme(
            name="default_parchment",
            dark=False,
            background="#F5ECD8",      # More yellow undertone
            foreground="#2C2826",
            primary="#A38B66",         # Warmer brown
            secondary="#8B735A",       # Warmer secondary
            accent="#FFF6E6",         # Warmer accent
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#EDE4D0",        # More yellow undertone
            panel="#FFF9EA",          # Warmer panel
        ),

        "default_ivory": Theme(
            name="default_ivory",
            dark=False,
            background="#F8F6F4",     # Desaturated white
            foreground="#2D2A26",
            primary="#9E958A",        # Desaturated brown
            secondary="#847E76",      # Desaturated secondary
            accent="#FFFDFC",        # Very slightly warm white
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#F0EEEC",       # Desaturated surface
            panel="#FFFFFF",
        ),

        "default_graphite": Theme(
            name="default_graphite",
            dark=True,
            background="#232326",
            foreground="#E0E0E2",
            primary="#667799",
            secondary="#445577",
            accent="#232326",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#2A2A2E",
            panel="#303034",
        ),

        "default_pearl": Theme(
            name="default_pearl",
            dark=False,
            background="#F8F0F0",
            foreground="#2C2D30",
            primary="#90BCBF",
            secondary="#4E5B6B",
            accent="#FFF0F0",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#F0F2F4",
            panel="#FFFFFF",
        ),

        "default_obsidian": Theme(
            name="default_obsidian",
            dark=True,
            background="#161618",
            foreground="#E6E6E8",
            primary="#665C7A",
            secondary="#4A4359",
            accent="#161618",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#1E1E21",
            panel="#252528",
        ),

        "default_charcoal": Theme(
            name="default_charcoal",
            dark=True,
            background="#1D1F1E",
            foreground="#E2E3E3",
            primary="#6B7272",
            secondary="#4E5353",
            accent="#1D1F1E",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#252827",
            panel="#2D302F",
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
            primary="#7777EB",
            secondary="#0000CD",
            accent="#1966AB",
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

        "fruit_strawberry": Theme(
            name="fruit_strawberry",
            dark=False,
            background="#FFF5F5",
            foreground="#8B1D1D",
            primary="#E14343",
            secondary="#C13030",
            accent="#FFE5E5",
            error="#D93025",
            success="#4CAF50",
            warning="#FFA726",
            surface="#FFF0F0",
            panel="#FFFFFF",
        ),

        "fruit_blueberry": Theme(
            name="fruit_blueberry",
            dark=True,
            background="#1A1B2E",
            foreground="#E6E7FF",
            primary="#4A4E8C",
            secondary="#363A77",
            accent="#1A1B2E",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#222438",
            panel="#2A2C42",
        ),

        "fruit_dragonfruit": Theme(
            name="fruit_dragonfruit",
            dark=False,
            background="#FFF5F9",
            foreground="#4A2037",
            primary="#E875B0",
            secondary="#C45C8F",
            accent="#FFE5F2",
            error="#D93025",
            success="#4CAF50",
            warning="#FFA726",
            surface="#FFF0F5",
            panel="#FFFFFF",
        ),

        "fruit_blackberry": Theme(
            name="fruit_blackberry",
            dark=True,
            background="#1A1522",
            foreground="#E6D9F2",
            primary="#614875",
            secondary="#4A3459",
            accent="#1A1522",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#221B2E",
            panel="#2A2238",
        ),

        "fruit_blood_orange": Theme(
            name="fruit_blood_orange",
            dark=False,
            background="#FFF5F5",
            foreground="#8B1D1D",
            primary="#C41E3A",
            secondary="#A01830",
            accent="#FFE5E5",
            error="#D93025",
            success="#4CAF50",
            warning="#FFA726",
            surface="#FFF0F0",
            panel="#FFFFFF",
        ),

        "fruit_avocado": Theme(
            name="fruit_avocado",
            dark=False,
            background="#F5FAF5",
            foreground="#2C4A2C",
            primary="#567C56",
            secondary="#445E44",
            accent="#E5FFE5",
            error="#D93025",
            success="#4CAF50",
            warning="#FFA726",
            surface="#F0FFF0",
            panel="#FFFFFF",
        ),

        "fruit_mango": Theme(
            name="fruit_mango",
            dark=False,
            background="#FFF9F5",
            foreground="#8B4513",
            primary="#FF9B4D",
            secondary="#E68A44",
            accent="#FFE5D9",
            error="#D93025",
            success="#4CAF50",
            warning="#FFA726",
            surface="#FFF4F0",
            panel="#FFFFFF",
        ),

        "fruit_plum": Theme(
            name="fruit_plum",
            dark=True,
            background="#1A151A",
            foreground="#E6D9E6",
            primary="#8B4B8B",
            secondary="#6E3C6E",
            accent="#1A151A",
            error="#963B3B",
            success="#4CAF50",
            warning="#C7A850",
            surface="#221B22",
            panel="#2A222A",
        ),
    }
