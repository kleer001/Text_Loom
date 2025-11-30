# MCP Server Example Usage

This document shows how LLMs interact with Text Loom via MCP.

## Example 1: Simple Text Processing

**User Request**: "Create a workflow that summarizes a text file using Claude"

**LLM Actions**:

```json
// 1. Create session
{
  "tool": "create_session",
  "arguments": {
    "metadata": {"purpose": "text summarization"}
  }
}
// Response: {"session_id": "abc-123"}

// 2. Add file input node
{
  "tool": "add_node",
  "arguments": {
    "session_id": "abc-123",
    "node_type": "file_in",
    "name": "input_file",
    "parameters": {
      "file_path": "~/documents/article.txt"
    },
    "position": [100, 100]
  }
}

// 3. Add query node (LLM)
{
  "tool": "add_node",
  "arguments": {
    "session_id": "abc-123",
    "node_type": "query",
    "name": "summarizer",
    "parameters": {
      "prompt": "Summarize this text in 3 sentences:",
      "llm_name": "Claude"
    },
    "position": [300, 100]
  }
}

// 4. Add output file node
{
  "tool": "add_node",
  "arguments": {
    "session_id": "abc-123",
    "node_type": "file_out",
    "name": "output_file",
    "parameters": {
      "file_path": "~/documents/summary.txt"
    },
    "position": [500, 100]
  }
}

// 5. Connect nodes
{
  "tool": "connect_nodes",
  "arguments": {
    "session_id": "abc-123",
    "source_name": "input_file",
    "target_name": "summarizer"
  }
}

{
  "tool": "connect_nodes",
  "arguments": {
    "session_id": "abc-123",
    "source_name": "summarizer",
    "target_name": "output_file"
  }
}

// 6. Execute workflow
{
  "tool": "execute_workflow",
  "arguments": {
    "session_id": "abc-123"
  }
}

// 7. Export for user
{
  "tool": "export_workflow",
  "arguments": {
    "session_id": "abc-123"
  }
}
```

**LLM Response to User**:
"I've created a workflow that:
1. Reads your article from ~/documents/article.txt
2. Sends it to Claude for summarization
3. Saves the summary to ~/documents/summary.txt

I've executed it and here's the exported workflow JSON. You can save this as `summarize.json` and run it anytime with:
```bash
./text_loom -b -f summarize.json
```

You can also open it in the GUI to modify the prompt or file paths:
```bash
./text_loom -g
# Then File > Import > summarize.json
```"

---

## Example 2: Batch Processing Multiple Files

**User Request**: "Process all text files in a folder through GPT-4 for translation"

**LLM Actions**:

```json
// 1. Create session
{
  "tool": "create_session",
  "arguments": {
    "metadata": {"purpose": "batch translation"}
  }
}

// 2. Create list of files
{
  "tool": "add_node",
  "arguments": {
    "session_id": "xyz-789",
    "node_type": "make_list",
    "name": "file_list",
    "parameters": {
      "items": [
        "~/docs/file1.txt",
        "~/docs/file2.txt",
        "~/docs/file3.txt"
      ]
    },
    "position": [100, 100]
  }
}

// 3. Add looper to process each file
{
  "tool": "add_node",
  "arguments": {
    "session_id": "xyz-789",
    "node_type": "looper",
    "name": "file_looper",
    "position": [300, 100]
  }
}

// 4. Add file reader inside loop
{
  "tool": "add_node",
  "arguments": {
    "session_id": "xyz-789",
    "node_type": "file_in",
    "name": "read_file",
    "parameters": {
      "file_path": "$LOOP_ITEM"  // Special variable from looper
    },
    "position": [320, 150]
  }
}

// 5. Add query node for translation
{
  "tool": "add_node",
  "arguments": {
    "session_id": "xyz-789",
    "node_type": "query",
    "name": "translator",
    "parameters": {
      "prompt": "Translate this to Spanish:",
      "llm_name": "GPT-4"
    },
    "position": [320, 200]
  }
}

// 6. Merge results
{
  "tool": "add_node",
  "arguments": {
    "session_id": "xyz-789",
    "node_type": "merge",
    "name": "collect_translations",
    "position": [500, 100]
  }
}

// 7. Output to file
{
  "tool": "add_node",
  "arguments": {
    "session_id": "xyz-789",
    "node_type": "file_out",
    "name": "save_translations",
    "parameters": {
      "file_path": "~/docs/translations.txt"
    },
    "position": [700, 100]
  }
}

// 8. Connect everything
// file_list → looper
// looper → read_file → translator → merge
// merge → file_out

// 9. Execute and export
```

---

## Example 3: Interactive Debugging

**User**: "The query node isn't working"

**LLM**: "Let me check the workflow configuration..."

```json
// 1. Get node output to see what happened
{
  "tool": "get_node_output",
  "arguments": {
    "session_id": "abc-123",
    "node_name": "query_node",
    "output_index": 0
  }
}

// Response shows empty output and errors

// 2. Export workflow to inspect
{
  "tool": "export_workflow",
  "arguments": {
    "session_id": "abc-123"
  }
}

// LLM analyzes exported JSON and finds issue
```

**LLM Response**:
"I found the issue - the query node doesn't have an LLM configured. I can fix this by updating the parameters. Would you like me to:
1. Update it to use Claude
2. Update it to use GPT-4
3. Let you choose in the GUI?"

---

## Example 4: Template Creation

**User**: "Create a template for processing survey responses"

**LLM**: Creates workflow with:
- File input (CSV)
- Split by delimiter
- Multiple query nodes (sentiment, categorization, summary)
- Merge results
- JSON output

Then exports as `survey_analysis_template.json` that user can reuse.

---

## Best Practices Shown

1. **Descriptive names**: `input_file`, not `node1`
2. **Logical positioning**: Left-to-right flow
3. **Always export**: Give user the JSON
4. **Clear instructions**: How to run/modify
5. **Error handling**: Check outputs, explain issues
6. **Reusable templates**: Export for future use

---

## Running These Examples

These are conceptual examples showing MCP tool calls. In practice:

1. **Via Claude Desktop**: Just ask Claude to create workflows
2. **Via API**: Call MCP server directly
3. **Via Python**: Use the MCP client library

Example Python client:

```python
from mcp.client import Client

async with Client("text-loom") as client:
    # Create session
    result = await client.call_tool("create_session", {})
    session_id = result["session_id"]

    # Build workflow
    await client.call_tool("add_node", {
        "session_id": session_id,
        "node_type": "text",
        "name": "my_node"
    })

    # Export
    workflow = await client.call_tool("export_workflow", {
        "session_id": session_id
    })

    print(workflow["flowstate"])
```
