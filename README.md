# Text Loom

**Visual programming for LLM workflows. Node-based text processing in your terminal.**

Build complex text workflows by connecting nodes—no code required. Query LLMs, transform text, iterate over lists, and save results. Think Houdini for text, Nuke for prompts.

<img src="images/mainwin3_trim.gif" alt="Text Loom Demo" width="800">

---

## Quick Start

**Docker (recommended):**
```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
python3 docker_wizard.py
```

**Native:**
```bash
curl -fsSL https://raw.githubusercontent.com/kleer001/Text_Loom/master/install.sh | bash
cd Text_Loom
python3 src/TUI/tui_skeleton.py
```

---

## What You Can Do

- **Visual workflows** - Connect nodes instead of writing scripts
- **LLM integration** - Works with Ollama, OpenAI, Claude, Gemini, and more
- **Batch processing** - Loop over lists, process files in bulk
- **Terminal UI** - Keyboard-driven interface (TUI)
- **REST API** - FastAPI backend for automation

---

## Core Nodes

Create text → Read files → Query LLMs → Split/merge lists → Loop operations → Save results

[Full documentation →](https://github.com/kleer001/Text_Loom/wiki)

---

## Why?

Visual programming exists for 3D (Houdini), images (Nuke), games (Unreal), music (Reaktor), audio (PureData). Why not text?

Text Loom makes procedural prompt engineering and text manipulation visual and intuitive.

---

## Contributing

Issues and PRs welcome. MIT License.
