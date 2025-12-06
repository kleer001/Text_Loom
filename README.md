# Text Loom

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/kleer001/Text_Loom)](https://github.com/kleer001/Text_Loom/releases)
[![Issues](https://img.shields.io/github/issues/kleer001/Text_Loom)](https://github.com/kleer001/Text_Loom/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Node-based text processing. Visual programming exists for images, audio, 3D, and games—now it exists for text.**

**Can't pick an interface? Neither could we—so here's five.**

Node-based text processing for everyone: terminal nerds (TUI), browser people (GUI), Python enthusiasts (REPL), automation addicts (API), and server minimalists (batch). Build workflows by connecting nodes, no code required.*

<sub>*Except in REPL mode. Obviously.</sub>

<img src="images/mainwin3_trim.gif" alt="Text Loom Demo" width="800">

---

## Quick Start

```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom

# Python setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# GUI setup (requires Node.js 18+)
npm install              # Root dependencies
cd src/GUI && npm install && npm run build && cd ../..

./text_loom              # Start GUI (default)
./text_loom -t           # Terminal UI
./text_loom -r           # Python REPL
./text_loom -b -f work.json  # Batch execute
```

**Prerequisites:**
- Python 3.8+
- Node.js 18+ and npm (for GUI mode)

**One-liner:**
```bash
curl -fsSL https://raw.githubusercontent.com/kleer001/Text_Loom/master/install.sh | bash && cd Text_Loom
```

**Docker:**
```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
python3 docker/docker_wizard.py
```

---

## Interfaces

Choose your workflow—all use the same core:

```bash
./text_loom -r           # REPL: Interactive Python shell (hython-style)
./text_loom -t           # TUI: Terminal UI (keyboard-driven)
./text_loom -a           # API: FastAPI server (automation)
./text_loom -g           # GUI: Web interface (visual)
./text_loom -b           # Batch: Non-interactive execution
```

---

## LLM Integration (MCP)

**Let AI assistants build workflows for you!**

Text Loom includes an MCP (Model Context Protocol) server that enables LLM tools to create workflows programmatically:

```bash
# Configure your MCP-compatible LLM tool with Text Loom
# Example configuration:
{
  "mcpServers": {
    "text-loom": {
      "command": "/path/to/Text_Loom/mcp_server"
    }
  }
}
```

Then ask your LLM assistant:
> "Using Text Loom, create a workflow that reads article.txt, summarizes it, and saves to summary.txt"

Your assistant will:
- ✅ Create the workflow
- ✅ Execute it
- ✅ Give you the JSON to save and reuse

**Learn more:** [`/docs/MCP_INTEGRATION.md`](docs/MCP_INTEGRATION.md)

---

## Key Features

**Text-First Design** — Strings and lists are the foundation. No JSON wrappers or object hierarchies.

**Multiple Interfaces** — Terminal UI, Web GUI, Python REPL, REST API, or batch mode—use what fits your workflow.

**LLM Integration** — Native support for major LLM providers and local models.

**Lightweight & Offline** — <50MB footprint, runs entirely self-hosted without internet dependency.

**MCP-Enabled** — Integrate with LLM tools to build workflows conversationally.

---

## What Makes Text Loom Different

| Feature | Text Loom | n8n | LangChain | ComfyUI | Zapier | Node-RED |
|---------|-----------|-----|-----------|---------|--------|----------|
| **Open Source** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Runs Offline** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Terminal UI** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Web UI** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Code Interface** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Visual Programming** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Text-First Data** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **LLM-Focused** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **No Programming Required** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Lightweight (<50MB)** | ✅ | ❌ | ✅ | ❌ | N/A | ✅ |
| **Batch Processing** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Self-Hosted** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

**Text Loom treats text as the primary data type.** Everything is a list of strings flowing through nodes. No JSON wrappers, no object hierarchies—just text in, text out.

---

## What You Can Do

**Visual workflows** - Connect nodes, not code

**LLM integration** - Support for major API providers and local models

**Batch processing** - Loop over lists, transform files in bulk

**Multiple interfaces** - TUI, GUI, REPL, API, batch—choose your style

**Scriptable** - Full Python API access for automation

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

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Real-World Examples

### Customer Service - Ticket Triage
```
File In node (support_tickets.txt)
→ Split node (split by ticket)
→ Looper node (process each ticket)
  → Query node (classify: bug/feature/question/complaint)
  → Query node (generate appropriate response template)
→ Merge node (group by category)
→ File Out node (sorted_tickets.txt)
```
*Auto-classify and generate response templates for support tickets.*

### Data Entry - Contact List Normalization
```
File In node (messy_contacts.csv)
→ Split node (split by line)
→ Looper node (process each contact)
  → Section node (extract phone numbers using @phone pattern)
  → Query node (standardize format to (XXX) XXX-XXXX)
  → Text node (reconstruct clean entry)
→ Merge node (combine cleaned contacts)
→ File Out node (clean_contacts.csv)
```
*Clean and standardize thousands of inconsistent contact records.*

### DevOps/IT - Log Analysis
```
Folder node (175 log files)
→ Looper node (process each file)
  → Search node (find "Warning|Memory Corruption|Syntax|Decoupling")
  → Text node (add filename prefix)
→ Merge node (collate all errors)
→ File Out node (errors_summary.txt)
```
*Find specific errors across hundreds of log files in seconds.*

### Legal/Compliance - Contract Clause Extraction
```
Folder node (200 vendor contracts)
→ Looper node (process each contract)
  → Search node (find "indemnification|liability|termination")
  → Query node (extract full clause context)
  → Text node (add contract filename and page)
→ Merge node (compile all clauses)
→ File Out node (clause_comparison.csv)
```
*Extract and compare specific clauses across hundreds of contracts.*

---

## License

MIT License - see [LICENSE](LICENSE) for details.
