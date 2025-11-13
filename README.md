# Text Loom

**Node-based visual programming for LLM workflows and text processing**

Text Loom is a terminal-based and web-based node editor that enables procedural text manipulation through visual programming. Build complex LLM workflows by connecting nodes that read, transform, query, and output text—without writing code.

---

## Features

- **Visual Node Editor** - Create text processing workflows with an intuitive node-based interface
- **LLM Integration** - Native support for 10+ LLM platforms (Ollama, OpenAI, Claude, Gemini, local models)
- **Iterative Processing** - Looper nodes enable batch processing and recursive workflows
- **File Operations** - Read/write files, manage workspaces, and persist results
- **Terminal UI** - Textual-based TUI with keyboard-driven navigation
- **REST API** - FastAPI backend for programmatic access and web integration
- **Docker Ready** - Containerized deployment with interactive setup wizard
- **Session Management** - Save/load workspaces with full state preservation

---

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
python3 docker_wizard.py
```

The wizard handles Docker setup, LLM detection, and configuration automatically.

### Native Installation

```bash
curl -fsSL https://raw.githubusercontent.com/kleer001/Text_Loom/master/install.sh | bash
cd Text_Loom
python3 src/TUI/tui_skeleton.py
```

---

## Architecture

Text Loom uses a **list-based text processing model** where data flows through connected nodes:

```
[Text] → [Split] → [Query LLM] → [Merge] → [FileOut]
```

### Core Node Types

| Node | Purpose | Example Use Case |
|------|---------|------------------|
| **Text** | Create static text | Prompts, templates |
| **FileIn/FileOut** | Read/write files | Load documents, save results |
| **Query** | LLM interaction | Text generation, analysis |
| **Split/Merge** | List manipulation | Batch processing, aggregation |
| **Section** | Text extraction | Parse structured data |
| **Looper** | Iteration container | Process lists, recursive operations |
| **MakeList** | List construction | Combine multiple inputs |

[Full node documentation →](https://github.com/kleer001/Text_Loom/wiki/Nodes,-nodes,-nodes)

### Technology Stack

- **Frontend**: React + TypeScript + XYFlow (web), Textual (TUI)
- **Backend**: Python 3.8+ with FastAPI
- **Storage**: JSON-based workspace persistence
- **Deployment**: Docker + docker-compose

---

## Installation

<details>
<summary><b>🐳 Docker Installation</b> (recommended for cross-platform deployment)</summary>

### Interactive Setup Wizard

```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
python3 docker_wizard.py
```

The wizard:
- Checks prerequisites (Docker, Docker Compose)
- Detects LLM platforms from `src/core/settings.cfg`
- Guides environment configuration
- Launches containers automatically

### Manual Docker Setup

```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
cp .env.example .env        # Configure API keys
docker-compose up -d
```

**Access points:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs
- Frontend: http://localhost:5173 (dev mode)

### Host LLM Configuration

For LLMs running on host machine, update `src/core/settings.cfg`:

```ini
[Ollama]
url = http://host.docker.internal:11434
```

Linux users can use `network_mode: host` in `docker-compose.yml` instead.

### Ollama in Docker

Uncomment the `ollama` service in `docker-compose.yml`:

```bash
docker-compose up -d
docker exec -it textloom-ollama ollama pull llama3
```

Update settings to use `http://ollama:11434`.

</details>

<details>
<summary><b>💻 Native Installation</b> (for local development)</summary>

### Automated

```bash
curl -fsSL https://raw.githubusercontent.com/kleer001/Text_Loom/master/install.sh | bash
cd Text_Loom
python3 src/TUI/tui_skeleton.py
```

### Manual

**Prerequisites:** Python 3.8+, git

```bash
git clone https://github.com/kleer001/Text_Loom
cd Text_Loom
python3 -m venv .venv
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pip install -e .
python3 src/TUI/tui_skeleton.py
```

**Windows:**
```cmd
.venv\Scripts\activate
set PYTHONPATH=%PYTHONPATH%;%cd%\src
```

</details>

---

## LLM Platform Support

Text Loom integrates with local and cloud LLM providers through a unified configuration system.

<details>
<summary><b>View supported platforms</b></summary>

Configure in `src/core/settings.cfg`:

| Platform | Default URL | Type |
|----------|-------------|------|
| Ollama | `localhost:11434` | Local |
| LM Studio | `localhost:1234` | Local |
| GPT4All | `localhost:4891` | Local |
| LocalAI | `localhost:8080` | Local |
| llama.cpp | `localhost:8080` | Local |
| oobabooga | `localhost:5000` | Local |
| OpenAI | `api.openai.com` | Cloud |
| Claude | `api.anthropic.com` | Cloud |
| Gemini | `generativelanguage.googleapis.com` | Cloud |
| Perplexity | `api.perplexity.ai` | Cloud |

Add custom endpoints by extending the configuration file.

</details>

---

## Usage

### Terminal UI

<img src="images/mainwin3_trim.gif" alt="Text Loom TUI Demo" width="800">

**Keyboard Navigation:**
- `Ctrl+N` - Node Network view
- `Ctrl+A` - Parameters panel
- `Ctrl+G` - Globals panel
- `Tab` - Cycle through windows
- `Enter` - Execute selected node

### Primary Workspace Components

| Component | Shortcut | Purpose |
|-----------|----------|---------|
| **Node Network** | `Ctrl+N` | Create and connect nodes |
| **Parameters** | `Ctrl+A` | Configure selected node properties |
| **Globals** | `Ctrl+G` | Manage workspace variables |
| **Output Display** | - | View node execution results |
| **Status Window** | - | Monitor system messages and errors |

### API Access

Start the API server:

```bash
uvicorn api.main:app --reload --port 8000
```

Example API call:

```python
import requests

response = requests.get("http://localhost:8000/api/v1/workspace")
nodes = response.json()["nodes"]
```

Full API documentation available at `/api/v1/docs` when server is running.

---

## Documentation

- **[Wiki](https://github.com/kleer001/Text_Loom/wiki)** - Comprehensive documentation
- **[Node Reference](https://github.com/kleer001/Text_Loom/wiki/Nodes,-nodes,-nodes)** - Detailed node documentation
- **[API Docs](http://localhost:8000/api/v1/docs)** - Interactive API documentation (when running)

---

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
Text_Loom/
├── src/
│   ├── TUI/              # Textual terminal interface
│   ├── GUI/              # React web frontend
│   ├── api/              # FastAPI backend
│   ├── core/             # Node engine and logic
│   └── tests/            # Test suite
├── Dockerfile
├── docker-compose.yml
└── docker_wizard.py      # Interactive Docker setup
```

---

## Contributing

Contributions welcome! Please:
1. Check existing issues or open a new one
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

Suggest additional LLM platforms by opening an issue with endpoint details.

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Related Projects

- [Nodysseus](https://nodysseus.io/) - Story-focused node editor
- [Nodes.io](https://nodes.io) - Web-based node programming

---

**Why Text Loom?**

Node-based editors exist for 3D (Houdini), images (Nuke), games (Unreal Blueprint), music (Reaktor), and audio (PureData). Text Loom brings visual programming to text processing and LLM workflows, enabling procedural approaches to prompt engineering and text manipulation.
