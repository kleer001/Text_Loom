from pathlib import Path
import re

def extract_colors(content: str) -> tuple[str, dict]:
    hex_pattern = r'#[0-9A-Fa-f]{6}'
    colors = re.findall(hex_pattern, content)
    name_pattern = r'name="([^"]+)"'
    name = re.search(name_pattern, content)
    return name.group(1) if name else "default", colors[:11]

def write_themes():
    template = '''
        "{name}": Theme(
            name="{name}",
            background="{bg}",
            foreground="{fg}",
            primary="{pri}",
            secondary="{sec}",
            accent="{acc}",
            error="{err}",
            success="{suc}",
            warning="{warn}",
            surface="{sur}",
            panel="{pan}",
        ),'''
    
    themes = []
    for file in Path('.').glob('*_colors.py'):
        with open(file) as f:
            name, colors = extract_colors(f.read())
            if len(colors) == 11:
                themes.append(template.format(
                    name=name, bg=colors[0], fg=colors[1], 
                    pri=colors[2], sec=colors[3], acc=colors[4],
                    err=colors[5], suc=colors[6], warn=colors[7],
                    sur=colors[8], pan=colors[9]
                ))

    output = "from textual.theme import Theme\n\ndef create_themes():\n    return {"
    output += "".join(themes)
    output += "\n    }\n"
    
    with open('theme_collection.py', 'w') as f:
        f.write(output)

if __name__ == '__main__':
    write_themes()