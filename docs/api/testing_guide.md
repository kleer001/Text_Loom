# TextLoom API Testing Guide

Complete guide for testing the TextLoom read-only API endpoints.

## Prerequisites

```bash
# Install dependencies
pip install fastapi uvicorn

# Ensure you're in the project root directory
cd /path/to/TextLoom
```

## Starting the API Server

```bash
# Start the server with auto-reload (for development)
uvicorn api.main:app --reload --port 8000

# Server will be available at:
# - API: http://127.0.0.1:8000
# - Swagger UI: http://127.0.0.1:8000/api/v1/docs
# - ReDoc: http://127.0.0.1:8000/api/v1/redoc
```

## Testing Strategy

### Option 1: Interactive Swagger UI (Recommended for Initial Testing)

1. **Open Swagger UI**: http://127.0.0.1:8000/api/v1/docs
2. **Explore endpoints** in the interactive documentation
3. **Try it out** - Click any endpoint → "Try it out" → "Execute"
4. **See results** immediately with formatted JSON

### Option 2: curl Commands (Command Line Testing)

```bash
# Test root endpoint (health check)
curl http://127.0.0.1:8000/

# Test API info
curl http://127.0.0.1:8000/api/v1

# Get complete workspace state
curl http://127.0.0.1:8000/api/v1/workspace | jq

# List all nodes
curl http://127.0.0.1:8000/api/v1/nodes | jq

# Get specific node by session_id (replace 123456789 with actual ID)
curl http://127.0.0.1:8000/api/v1/nodes/123456789 | jq
```

### Option 3: Python Requests (Programmatic Testing)

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Get workspace state
response = requests.get(f"{BASE_URL}/workspace")
workspace = response.json()
print(json.dumps(workspace, indent=2))

# Get all nodes
response = requests.get(f"{BASE_URL}/nodes")
nodes = response.json()
print(f"Found {len(nodes)} nodes")

# Get specific node
if nodes:
    session_id = nodes[0]['session_id']
    response = requests.get(f"{BASE_URL}/nodes/{session_id}")
    node = response.json()
    print(f"Node: {node['name']} at {node['path']}")
```

## Creating Test Data

Before testing, create a simple workspace with test nodes:

```python
# test_setup.py
from core.base_classes import Node, NodeType

# Create a simple workflow: TextNode -> FileOutNode
text_node = Node.create_node(NodeType.TEXT, node_name="test_text")
text_node._parms["text_string"].set("Hello from API test!")

fileout_node = Node.create_node(NodeType.FILEOUT, node_name="test_output")
fileout_node._parms["file_name"].set("./test_output.txt")

# Connect them
fileout_node.set_input(0, text_node)

print(f"Created test workspace:")
print(f"  Text node: {text_node.path()} (session_id: {text_node.session_id()})")
print(f"  FileOut node: {fileout_node.path()} (session_id: {fileout_node.session_id()})")
```

Run this before starting the API:
```bash
python test_setup.py
```

## Expected Response Examples

### GET /workspace

```json
{
  "nodes": [
    {
      "session_id": 123456789012345678,
      "name": "test_text",
      "path": "/test_text",
      "type": "text",
      "state": "unchanged",
      "parameters": {
        "text_string": {
          "type": "STRING",
          "value": "Hello from API test!",
          "default": "",
          "read_only": false
        },
        "pass_through": {
          "type": "TOGGLE",
          "value": true,
          "default": true,
          "read_only": false
        }
      },
      "inputs": [
        {
          "index": 0,
          "name": "input",
          "data_type": "List[str]",
          "connected": false
        }
      ],
      "outputs": [
        {
          "index": 0,
          "name": "output",
          "data_type": "List[str]",
          "connection_count": 1
        }
      ],
      "errors": [],
      "warnings": [],
      "position": [0.0, 0.0],
      "color": [1.0, 1.0, 1.0],
      "selected": false,
      "is_time_dependent": false,
      "cook_count": 0,
      "last_cook_time": 0.0
    },
    {
      "session_id": 987654321098765432,
      "name": "test_output",
      "path": "/test_output",
      "type": "fileout",
      "state": "unchanged",
      "parameters": {
        "file_name": {
          "type": "STRING",
          "value": "./test_output.txt",
          "default": "./output.txt",
          "read_only": false
        }
      },
      "inputs": [
        {
          "index": 0,
          "name": "input",
          "data_type": "List[str]",
          "connected": true
        }
      ],
      "outputs": [],
      "errors": [],
      "warnings": [],
      "position": [0.0, 0.0],
      "color": [1.0, 1.0, 1.0],
      "selected": false,
      "is_time_dependent": false,
      "cook_count": 0,
      "last_cook_time": 0.0
    }
  ],
  "connections": [
    {
      "source_node_session_id": 123456789012345678,
      "source_node_path": "/test_text",
      "source_output_index": 0,
      "source_output_name": "output",
      "target_node_session_id": 987654321098765432,
      "target_node_path": "/test_output",
      "target_input_index": 0,
      "target_input_name": "input"
    }
  ],
  "globals": {}
}
```

### GET /nodes

```json
[
  {
    "session_id": 123456789012345678,
    "name": "test_text",
    "path": "/test_text",
    "type": "text",
    "state": "unchanged",
    "parameters": { /* ... */ },
    "inputs": [ /* ... */ ],
    "outputs": [ /* ... */ ],
    "errors": [],
    "warnings": [],
    "position": [0.0, 0.0],
    "color": [1.0, 1.0, 1.0],
    "selected": false,
    "is_time_dependent": false,
    "cook_count": 0,
    "last_cook_time": 0.0
  }
]
```

### GET /nodes/{session_id}

```json
{
  "session_id": 123456789012345678,
  "name": "test_text",
  "path": "/test_text",
  "type": "text",
  "state": "unchanged",
  "parameters": {
    "text_string": {
      "type": "STRING",
      "value": "Hello from API test!",
      "default": "",
      "read_only": false
    }
  },
  "inputs": [],
  "outputs": [],
  "errors": [],
  "warnings": [],
  "position": [0.0, 0.0],
  "color": [1.0, 1.0, 1.0],
  "selected": false,
  "is_time_dependent": false,
  "cook_count": 0,
  "last_cook_time": 0.0
}
```

## Error Responses

### 404 - Node Not Found

```bash
curl http://127.0.0.1:8000/api/v1/nodes/999999999
```

```json
{
  "detail": {
    "error": "node_not_found",
    "message": "Node with session_id 999999999 does not exist",
    "session_id": 999999999
  }
}
```

## Testing Checklist

- [ ] Server starts without errors
- [ ] Swagger UI loads at `/api/v1/docs`
- [ ] Root endpoint (`/`) returns health check
- [ ] `/api/v1/workspace` returns workspace state
- [ ] `/api/v1/nodes` returns array of nodes
- [ ] `/api/v1/nodes/{session_id}` returns single node
- [ ] `/api/v1/nodes/999999` returns 404 error
- [ ] All responses match expected JSON schema
- [ ] CORS headers allow local frontend requests

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'api'`:

```bash
# Make sure you're running from project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn api.main:app --reload
```

### Empty Workspace

If `/api/v1/workspace` returns empty arrays:

```bash
# Run test_setup.py first to create test nodes
python test_setup.py

# Then test the API
curl http://127.0.0.1:8000/api/v1/workspace | jq
```

### CORS Errors in Browser

If frontend shows CORS errors, add your frontend URL to `api/main.py`:

```python
origins = [
    "http://localhost:3000",
    "http://your-frontend-url:port",  # Add your URL here
]
```

## Next Steps

Once read-only endpoints are tested:
1. Test with a real frontend (React/Vue/etc)
2. Add write endpoints (POST, PUT, DELETE)
3. Add execution endpoints (POST /nodes/{id}/execute)
4. Add connection management endpoints
5. Consider WebSocket for real-time updates