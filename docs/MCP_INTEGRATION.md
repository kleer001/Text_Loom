# Text Loom MCP Integration

## What is MCP?

Model Context Protocol (MCP) is an open protocol that standardizes how LLMs interact with external tools and data sources. It's like a USB port for AI - a universal way for LLMs to connect to your tools.

## Why MCP for Text Loom?

Text Loom + MCP enables:

✅ **LLMs as workflow designers** - Claude/GPT can create workflows for you
✅ **Natural language to graphs** - "Summarize these files" → complete workflow
✅ **Automated template creation** - LLM builds reusable workflow templates
✅ **Interactive debugging** - LLM helps fix workflow issues
✅ **Batch automation** - LLM creates workflows you can run repeatedly

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the `mcp>=0.9.0` package.

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "text-loom": {
      "command": "/absolute/path/to/Text_Loom/mcp_server"
    }
  }
}
```

**Important**: Use absolute path, not `~` or relative paths.

### 3. Restart Claude Desktop

The MCP server will auto-start when Claude needs it.

### 4. Try It Out

In Claude Desktop, ask:

> "Using Text Loom, create a workflow that reads article.txt, summarizes it with Claude, and saves to summary.txt"

Claude will:
1. Create isolated session
2. Add nodes (file_in, query, file_out)
3. Connect them
4. Execute the workflow
5. Give you the exported JSON to save

## How It Works

```
┌─────────────┐
│   Claude    │ ← User: "Create a summarization workflow"
│   Desktop   │
└──────┬──────┘
       │ MCP Protocol
       ↓
┌─────────────┐
│ Text Loom   │ ← Tools: create_session, add_node, connect_nodes, etc.
│ MCP Server  │
└──────┬──────┘
       │ Python API
       ↓
┌─────────────┐
│ Text Loom   │ ← Nodes, connections, execution
│    Core     │
└─────────────┘
```

## Available Tools

The MCP server exposes 9 tools to LLMs:

| Tool | Purpose |
|------|---------|
| `create_session` | Start isolated workspace |
| `list_node_types` | See available node types |
| `add_node` | Create nodes in workflow |
| `connect_nodes` | Wire nodes together |
| `execute_workflow` | Run the workflow |
| `get_node_output` | Read results |
| `export_workflow` | Get JSON for saving |
| `set_global` | Set global variables |
| `delete_session` | Clean up |

See [mcp_server.md](mcp_server.md) for complete reference.

## Use Cases

### 1. Rapid Prototyping

**Before MCP**:
- Open GUI
- Manually drag nodes
- Configure each one
- Wire connections
- Test and debug

**With MCP**:
- Ask Claude: "Create a workflow that processes these 10 files"
- Get working workflow in seconds
- Open in GUI to refine

### 2. Template Library

Ask Claude to create templates:
- "Email extraction and categorization"
- "Multi-step research pipeline"
- "Batch image description generation"

Save exports, reuse forever.

### 3. Learning Text Loom

**New users**: Ask Claude to build workflows while explaining each step.

**Example**:
> "Show me how to use the looper node to process a list"

Claude creates working example + explanation.

### 4. Debugging

**When stuck**, ask Claude to analyze your workflow:
> "Here's my workflow JSON. Why isn't the query node working?"

Claude can inspect, diagnose, suggest fixes.

### 5. Integration Scripts

Use MCP server in Python scripts:

```python
from mcp.client import Client

async with Client("text-loom") as client:
    # Programmatic workflow creation
    session = await client.create_session()
    # ... build workflow
    result = await client.execute_workflow(session["session_id"])
```

## Workflow Philosophy

### LLM Creates, Human Refines

1. **LLM builds initial workflow** - Fast, automated
2. **Human reviews/modifies** - Visual editing in GUI/TUI
3. **Batch execution** - Reliable, repeatable

This combines:
- **Speed** of LLM generation
- **Precision** of visual editing
- **Power** of batch automation

### Session Isolation

Each LLM operation uses isolated session:
- No interference between workflows
- Safe concurrent operations
- Clean state management

### Export-First Design

Every LLM-created workflow is **exportable**:
- User owns the JSON
- Can version control it
- Can share with others
- Can modify offline

## Architecture

### Components

```
src/mcp/
├── __init__.py           # Package init
├── server.py             # MCP server (9 tools)
├── session_manager.py    # Workspace isolation
└── workflow_builder.py   # High-level workflow API
```

### Sessions

```python
# Each session has:
{
  "session_id": "uuid",
  "created_at": "timestamp",
  "workspace_file": "/tmp/text_loom_sessions/uuid.json",
  "metadata": {"user": "alice", "purpose": "..."}
}
```

Sessions are:
- Automatically persisted
- Isolated from each other
- Exportable as flowstate JSON
- Cleanable with `delete_session`

### Workflow Builder

High-level API wrapping Text Loom core:

```python
builder = WorkflowBuilder()

# Add nodes
builder.add_node("text", "my_text", parameters={"text_string": "Hello"})
builder.add_node("query", "llm", parameters={"prompt": "Summarize:"})

# Connect
builder.connect("my_text", "llm")

# Execute
results = builder.execute_all()

# Get output
output = builder.get_output("llm")
```

Simpler than direct core API, perfect for LLM agents.

## Configuration Examples

### Claude Desktop (macOS)

`~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "text-loom": {
      "command": "/Users/alice/Text_Loom/mcp_server"
    }
  }
}
```

### Claude Desktop (Windows)

`%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "text-loom": {
      "command": "C:\\Users\\Alice\\Text_Loom\\mcp_server"
    }
  }
}
```

### Claude Desktop (Linux)

`~/.config/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "text-loom": {
      "command": "/home/alice/Text_Loom/mcp_server"
    }
  }
}
```

### With Virtual Environment

If using venv:

```json
{
  "mcpServers": {
    "text-loom": {
      "command": "/path/to/Text_Loom/.venv/bin/python",
      "args": ["/path/to/Text_Loom/mcp_server"]
    }
  }
}
```

## Troubleshooting

### Server won't start

**Check**:
1. Is `mcp_server` executable? `chmod +x mcp_server`
2. Is path absolute in config?
3. Can Python find modules? Check PYTHONPATH in script

**Test manually**:
```bash
cd Text_Loom
./mcp_server
# Should wait for input (MCP protocol)
```

### Tools not appearing in Claude

**Check**:
1. Restarted Claude Desktop after config change?
2. JSON syntax valid? Use `jsonlint` or similar
3. Check Claude logs (Help > View Logs)

### Import errors

**Check**:
1. Dependencies installed? `pip install -r requirements.txt`
2. In correct directory? `pwd` should show Text_Loom
3. Python path correct? `echo $PYTHONPATH`

### Workflow execution fails

**Check**:
1. LLM API keys configured? (for query nodes)
2. File paths accessible?
3. Node parameters correct?

**Debug**:
Ask Claude to export workflow, inspect JSON manually.

## Security Considerations

### File Access

MCP server runs with **your user permissions**. LLMs can:
- ✅ Read/write files you can access
- ❌ No privilege escalation
- ❌ No network access (unless via LLM API calls in query nodes)

### Best Practices

1. **Review workflows** before executing
2. **Check file paths** in exported JSON
3. **Use specific paths** rather than wildcards
4. **Limit LLM scope** via session metadata
5. **Clean up sessions** when done

### Isolation

Each session is isolated:
- Separate workspace
- No cross-session access
- Temporary files cleaned up

## Performance

### Benchmarks

Typical operations:
- Create session: <10ms
- Add node: <5ms
- Connect nodes: <1ms
- Execute simple workflow: <100ms
- Export workflow: <50ms

### Scaling

- Sessions are lightweight (just JSON state)
- Concurrent sessions supported
- No database required
- Memory scales with node count per session

## Examples

See [example_usage.md](../examples/mcp_workflows/example_usage.md) for detailed examples.

## Next Steps

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Add to Claude Desktop config
3. **Try**: Ask Claude to create a simple workflow
4. **Learn**: Review exported JSON in GUI
5. **Iterate**: Build templates, automate workflows

## Resources

- **MCP Server Docs**: [mcp_server.md](mcp_server.md)
- **API Reference**: [api/](/docs/api/)
- **Examples**: [examples/mcp_workflows/](/examples/mcp_workflows/)
- **MCP Specification**: https://modelcontextprotocol.io

## Contributing

Found a bug? Want a new tool? Open an issue:
https://github.com/kleer001/Text_Loom/issues

---

**Ready to supercharge Text Loom with LLM automation? Install the MCP server and let Claude build workflows for you!**
