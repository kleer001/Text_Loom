NODE_TYPE_EMOJIS = {
    'QUERY': '⌘',      # Command symbol - represents interface/control
    'NULL': '∅',       # Empty set - perfect for null
    'LOOPER': '⟲',     # Clockwise loop arrow
    'FILE_IN': '⤵',    # Incoming arrow
    'FILE_OUT': '⤴',   # Outgoing arrow
    'TEXT': '¶',       # Pilcrow/paragraph mark for text
    'SPLIT': '⋔',      # Fork symbol
    'SECTION': '§',    # Section symbol
    'MAKE_LIST': '≣',  # Triple line equals for list
    'MERGE': '⋈'       # Join symbol from set theory
}

def get_node_emoji(node_type: str) -> str:
    return NODE_TYPE_EMOJIS.get(node_type, '')