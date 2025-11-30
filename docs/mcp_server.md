# Text Loom MCP Server

Enable LLMs to create and execute Text Loom workflows via Model Context Protocol (MCP).

## Overview

The Text Loom MCP server exposes Text Loom's workflow capabilities to LLM agents like Claude. LLMs can:

- Create text processing workflows programmatically
- Execute workflows and get results
- Export workflows for users to edit in GUI/TUI
- Run workflows in batch mode

## Installation

1. **Install MCP dependency**:
```bash
pip install mcp>=0.9.0
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

2. **Configure Claude Desktop** (or other MCP client):

Add to your MCP configuration file (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "text-loom": {
      "command": "/path/to/Text_Loom/mcp_server",
      "args": []
    }
  }
}
```

## Usage

### Starting the Server

**Via Claude Desktop**: Automatically starts when Claude needs it.

**Standalone testing**:
```bash
./mcp_server
```

### Available Tools

The MCP server provides these tools to LLMs:

#### 1. `create_session`
Create an isolated workflow session.

**Parameters**:
- `metadata` (optional): Dict with session metadata

**Returns**: `session_id` for use in all other operations

**Example**:
```json
{
  "metadata": {
    "user": "alice",
    "purpose": "text summarization"
  }
}
```

---

#### 2. `list_node_types`
Get all available node types and descriptions.

**Returns**: List of node types with descriptions

---

#### 3. `add_node`
Add a node to the workflow.

**Parameters**:
- `session_id` (required): Session ID
- `node_type` (required): Type of node (e.g., "text", "query", "file_out")
- `name` (required): Unique name for the node
- `parameters` (optional): Node-specific parameters
- `position` (optional): Visual position [x, y]

**Common node types**:
- `text`: Static text input
- `query`: Send to LLM
- `file_in`: Read file
- `file_out`: Write file
- `merge`: Combine inputs
- `split`: Split into multiple outputs
- `looper`: Process list items

**Example**:
```json
{
  "session_id": "abc123",
  "node_type": "text",
  "name": "input_text",
  "parameters": {
    "text_string": "Hello, world!"
  },
  "position": [100, 100]
}
```

---

#### 4. `connect_nodes`
Connect two nodes together.

**Parameters**:
- `session_id` (required): Session ID
- `source_name` (required): Source node name
- `target_name` (required): Target node name
- `source_output` (optional): Source output index (default 0)
- `target_input` (optional): Target input index (default 0)

**Example**:
```json
{
  "session_id": "abc123",
  "source_name": "input_text",
  "target_name": "query_node"
}
```

---

#### 5. `execute_workflow`
Execute all nodes in the workflow.

**Parameters**:
- `session_id` (required): Session ID

**Returns**: Execution results for all nodes

---

#### 6. `get_node_output`
Get output from a specific node after execution.

**Parameters**:
- `session_id` (required): Session ID
- `node_name` (required): Node name
- `output_index` (optional): Output index (default 0)

**Returns**: List of output strings

---

#### 7. `export_workflow`
Export workflow as JSON flowstate.

**Parameters**:
- `session_id` (required): Session ID

**Returns**: Flowstate JSON that user can save and load in Text Loom

---

#### 8. `set_global`
Set a global variable accessible to all nodes.

**Parameters**:
- `session_id` (required): Session ID
- `key` (required): Variable name
- `value` (required): List of strings

---

#### 9. `delete_session`
Clean up session and resources.

**Parameters**:
- `session_id` (required): Session ID

---

## Example Workflows

### Simple Text to File

```
1. Create session
2. Add text node with content
3. Add file_out node
4. Connect text → file_out
5. Execute workflow
6. Export for user
```

### LLM Query Pipeline

```
1. Create session
2. Add text node (prompt)
3. Add query node (LLM)
4. Add file_out node
5. Connect: text → query → file_out
6. Execute workflow
7. Get output from query node
```

### Batch Processing

```
1. Create session
2. Add file_in node (read list)
3. Add looper node
4. Add query node (inside looper)
5. Add merge node (collect results)
6. Add file_out node
7. Connect: file_in → looper → query → merge → file_out
8. Execute workflow
9. Export for user to modify
```

## Architecture

### Session Isolation

Each LLM operation gets its own session with:
- Separate node environment
- Isolated global variables
- Independent execution context

Sessions are automatically saved to temp files and can be exported.

### Workflow Builder

High-level API for creating workflows:
- Simple node creation
- Automatic connection management
- Batch execution
- Result retrieval

### Integration Points

**For Users**:
1. LLM creates initial workflow via MCP
2. Export workflow as JSON
3. User loads in GUI/TUI to modify
4. User runs with `./text_loom -b -f workflow.json`

**For LLMs**:
- Create complex workflows from natural language
- Execute and validate results
- Iterate on workflow design
- Provide working templates

## Best Practices

### For LLMs

1. **Always create a session first**
2. **Use descriptive node names** (e.g., "prompt_generator" not "node1")
3. **Set positions** for visual clarity when user loads
4. **Export workflows** so users can save them
5. **Handle errors gracefully** and suggest fixes
6. **Clean up sessions** when done

### For Users

1. **Review LLM-generated workflows** before running
2. **Save exported JSON** for reuse
3. **Modify in GUI/TUI** for fine-tuning
4. **Use batch mode** for production runs

## Troubleshooting

### MCP Server Won't Start

- Check Python path in config
- Verify `mcp_server` is executable: `chmod +x mcp_server`
- Check `PYTHONPATH` includes `src/`

### Node Creation Fails

- Verify node type matches enum exactly (e.g., `file_out` not `fileout`)
- Check parameter names match node class attributes
- Use `list_node_types` to see available types

### Connection Errors

- Ensure both nodes exist before connecting
- Verify output/input indices are valid
- Check node names are exact matches

### Execution Fails

- Review node parameters
- Check file paths are accessible
- Verify LLM API keys are configured
- Look at error messages in execution results

## API Reference

See `/docs/api/` for complete REST API documentation.

## Examples

See `/examples/mcp_workflows/` for example workflow scripts.

---

**Need Help?**

- GitHub Issues: https://github.com/kleer001/Text_Loom/issues
- Documentation: `/docs/`
- API Docs: `http://localhost:8000/api/v1/docs` (when API server running)
