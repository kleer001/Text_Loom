# Text Loom

**Visual programming for LLM workflows. Node-based text processing in your terminal.**

Build complex text workflows by connecting nodes—no code required. Query LLMs, transform text, iterate over lists, and save results.

<img src="images/mainwin3_trim.gif" alt="Text Loom Demo" width="800">

---

## Quick Start

**Terminal UI:**
```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
python3 -m venv .venv
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pip install -e .
python3 src/TUI/tui_skeleton.py
```

**Python REPL (expert mode):**
```bash
./tloom                    # Interactive shell
./tloom workflow.json      # Load and explore
./tloom script.py          # Execute workflow script
```

**One-liner:**
```bash
curl -fsSL https://raw.githubusercontent.com/kleer001/Text_Loom/master/install.sh | bash && cd Text_Loom
```

**Docker:**
```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
python3 docker_wizard.py
```

---

## Interfaces

**Terminal UI** - Visual node editor with keyboard-driven workflow

**Python REPL** - Direct API access for scripting and debugging (inspired by Houdini's hython)

**REST API** - FastAPI backend for automation and integration

**Web GUI** - Modern browser interface (experimental)

---

## What Makes Text Loom Different

|  | Text Loom | n8n | LangChain |
|---|-----------|-----|-----------|
| **Architecture** | Text-first (lists of strings) | JSON objects | Python objects |
| **Interface** | Terminal UI + Web | Web only | Code only |
| **Text handling** | First-class citizen | Nested in JSON | Wrapped in objects |
| **Deployment** | Local, lightweight | Server required | Library dependency |
| **Learning curve** | Visual, immediate | Web automation focus | Programming required |
| **LLM focus** | Built for prompt engineering | General automation | Framework/abstraction |

**Text Loom treats text as the primary data type.** Everything is a list of strings flowing through nodes. No JSON wrappers, no object hierarchies—just text in, text out.

---

## What You Can Do

**Visual workflows** - Connect nodes instead of writing scripts

**Python scripting** - Full API access via tloom REPL for automation

**LLM integration** - Works with Ollama, OpenAI, Claude, Gemini, and more

**Batch processing** - Loop over lists, process files in bulk

**Multiple interfaces** - Terminal UI, Python REPL, REST API, Web GUI

---

## Core Nodes

Create text → Read files → Query LLMs → Split/merge lists → Loop operations → Save results

[Full documentation →](https://github.com/kleer001/Text_Loom/wiki)

---

## Why?

Visual programming exists for 3D, images, games, music, and audio. Text deserves the same treatment.

Text Loom makes procedural prompt engineering and text manipulation visual and intuitive—with text as the foundation, not an afterthought.

---

## Contributing

Issues and PRs welcome. MIT License.
