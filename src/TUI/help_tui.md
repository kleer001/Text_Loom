[NODE]
↑/↓: Navigate nodes
Enter: Select/Connect node
p: Select node parameters
Space: Expand/collapse node
a: Add node
d: Delete node
r: Rename node
x: Delete connection
i: Start input connection
o: Start output connection
Esc: Cancel connection
e: Get node output
m: Move node path
shift-c: Cook node
ctrl+o: Open File
ctrl+s: Quick Save
ctrl+d: Save As
ctrl+z: Undo
ctrl+y: Redo
ctrl+q: Quit
ctrl+w: Clear All
ctrl+l: Load Theme

[PARAMETER]
j/k: Navigate parameters
Enter: Edit parameter
Esc: Exit edit mode
Tab: Next field
ctrl+x: Remove Current Set
ctrl+f: Clear All Sets

[GLOBAL]
j/k: Navigate variables
Enter: Edit value
cut <KEY>: Delete variable
cut all globals: Delete all variables
n: New variable

[FILE]
j/k: Navigate files
Enter: Select
q: Exit to previous mode
s: Save
S: Save As

[HELP]
This IS the help system.
Ctrl + n: Node
Ctrl + p: Parameter
Ctrl + g: Global
Ctrl + f: File
Ctrl + h: Help
Ctrl + k: Keymap

[KEYMAP]
j/k: Navigate bindings
Enter: Edit binding
d: Delete binding
n: New binding
q: Exit to previous mode

[STATUS]
j/k: Scroll output
G: Jump to bottom
gg: Jump to top
n: Next match
N: Previous match

[OUTPUT]
j/k: Scroll output
G: Jump to bottom
gg: Jump to top
c: Clear output

[MODELINE]
The modeline displays at the bottom of the screen showing current state and token usage.

Display Format:
📝🧵 [MODE] filename | debug_info | Keys: keypress   🪙 token_info

Components:
📝🧵: Mode indicator showing current screen (NODE, PARAMETER, GLOBAL, etc.)
filename: Current workspace file path (shows "untitled" if not saved)
debug_info: Optional debug information when available
Keys: keypress: Shows last keypress sequence when available
🪙: Token usage from LLM queries (right side)

Token Tracking Keybindings:
t: Toggle token view (session ↔ node)
shift+x: Reset all token data (requires confirmation)

Token Display Modes:
Session mode: Shows session-wide totals
  Format: "🪙 in:X out:Y total:Z"
  Example: "🪙 in:1,250 out:3,400 total:4,650"

Node mode: Shows per-node totals for selected node
  Format: "🪙 NodeName: in:X out:Y total:Z"
  Example: "🪙 QueryNode_1: in:450 out:890 total:1,340"
  Shows "(none selected)" if no node is selected

Token Updates:
- Automatically updates when nodes are cooked/executed
- Updates when workspace file is loaded
- Updates when toggling between modes
- Updates when selecting different nodes (in node mode)