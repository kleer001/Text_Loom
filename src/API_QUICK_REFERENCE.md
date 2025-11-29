# TextLoom API Quick Reference

Complete reference for all API endpoints with curl examples.

## Base URL

```
http://127.0.0.1:8000/api/v1
```

---

## 📖 Node Endpoints

### List All Nodes
```bash
curl http://127.0.0.1:8000/api/v1/nodes
```

### Get Single Node
```bash
curl http://127.0.0.1:8000/api/v1/nodes/123456789
```

### Create Node
```bash
curl -X POST http://127.0.0.1:8000/api/v1/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "name": "my_text_node",
    "parent_path": "/",
    "position": [100.0, 200.0]
  }'
```

**Node Type Naming:**
- Use underscores: `file_out`, `file_in`, `make_list`, `input_null`, `output_null`
- Available types: `text`, `file_out`, `file_in`, `null`, `merge`, `split`, `query`, `looper`, `make_list`, `section`, `folder`, `json`, `input_null`, `output_null`

### Update Node
```bash
curl -X PUT http://127.0.0.1:8000/api/v1/nodes/123456789 \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "text_string": "Updated text",
      "pass_through": false
    },
    "position": [150.0, 250.0]
  }'
```

### Delete Node
```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/nodes/123456789
```

### Execute Node
```bash
curl -X POST http://127.0.0.1:8000/api/v1/nodes/123456789/execute
```

**Response includes:**
- `success`: boolean
- `output_data`: array of output lists
- `execution_time`: milliseconds
- `node_state`: "cooked", "unchanged", "error"
- `errors`: array of error messages
- `warnings`: array of warning messages

---

## 🔗 Connection Endpoints

### Create Connection
```bash
curl -X POST http://127.0.0.1:8000/api/v1/connections \
  -H "Content-Type: application/json" \
  -d '{
    "source_node_path": "/text1",
    "source_output_index": 0,
    "target_node_path": "/fileout1",
    "target_input_index": 0
  }'
```

### Delete Connection
```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/connections \
  -H "Content-Type: application/json" \
  -d '{
    "source_node_path": "/text1",
    "source_output_index": 0,
    "target_node_path": "/fileout1",
    "target_input_index": 0
  }'
```

---

## 🌍 Global Variables

### List All Globals
```bash
curl http://127.0.0.1:8000/api/v1/globals
```

### Get Single Global
```bash
curl http://127.0.0.1:8000/api/v1/globals/MYVAR
```

### Set Global Variable
```bash
curl -X PUT http://127.0.0.1:8000/api/v1/globals/MYVAR \
  -H "Content-Type: application/json" \
  -d '{"value": "my value"}'
```

**Key requirements:**
- At least 2 characters
- All uppercase
- Cannot start with '$'

### Delete Global
```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/globals/MYVAR
```

---

## 🗺️ Workspace

### Get Complete Workspace State
```bash
curl http://127.0.0.1:8000/api/v1/workspace
```

Returns:
- `nodes`: array of all nodes with full details
- `connections`: array of all connections
- `globals`: dictionary of global variables

---

## 💡 Common Workflows

### Create a Simple Text → FileOut Pipeline

```bash
# Create text node
TEXT_NODE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/nodes \
  -H "Content-Type: application/json" \
  -d '{"type": "text", "name": "my_text"}' | jq -r '.session_id')

# Set text content
curl -X PUT http://127.0.0.1:8000/api/v1/nodes/$TEXT_NODE \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"text_string": "Hello World", "pass_through": false}}'

# Create fileout node
FILEOUT_NODE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/nodes \
  -H "Content-Type: application/json" \
  -d '{"type": "file_out", "name": "output"}' | jq -r '.session_id')

# Set output filename
curl -X PUT http://127.0.0.1:8000/api/v1/nodes/$FILEOUT_NODE \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"file_name": "./output.txt"}}'

# Connect them
curl -X POST http://127.0.0.1:8000/api/v1/connections \
  -H "Content-Type: application/json" \
  -d "{
    \"source_node_path\": \"/my_text\",
    \"source_output_index\": 0,
    \"target_node_path\": \"/output\",
    \"target_input_index\": 0
  }"

# Execute
curl -X POST http://127.0.0.1:8000/api/v1/nodes/$FILEOUT_NODE/execute

# Check the file
cat ./output.txt
```

### Query Workspace State

```bash
# Get all nodes
curl http://127.0.0.1:8000/api/v1/nodes | jq '.[] | {name, type, path}'

# Get specific node details
curl http://127.0.0.1:8000/api/v1/nodes/123456789 | jq '.parameters'

# List all connections
curl http://127.0.0.1:8000/api/v1/workspace | jq '.connections'

# Show globals
curl http://127.0.0.1:8000/api/v1/globals | jq '.globals'
```

### Batch Operations

```bash
# Delete all nodes
curl -s http://127.0.0.1:8000/api/v1/nodes | \
  jq -r '.[].session_id' | \
  while read id; do
    curl -X DELETE http://127.0.0.1:8000/api/v1/nodes/$id
  done

# Update all text nodes
curl -s http://127.0.0.1:8000/api/v1/nodes | \
  jq -r '.[] | select(.type == "text") | .session_id' | \
  while read id; do
    curl -X PUT http://127.0.0.1:8000/api/v1/nodes/$id \
      -H "Content-Type: application/json" \
      -d '{"parameters": {"text_string": "Batch updated!"}}'
  done
```

---

## 🐛 Error Responses

All errors follow this format:

```json
{
  "detail": {
    "error": "error_code",
    "message": "Human-readable message"
  }
}
```

### Common Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| `node_not_found` | 404 | Node with given session_id doesn't exist |
| `invalid_node_type` | 400 | Unknown node type specified |
| `invalid_parameter` | 400 | Parameter name doesn't exist or value is invalid |
| `connection_not_found` | 404 | Specified connection doesn't exist |
| `invalid_key` | 400 | Global variable key format is invalid |
| `global_not_found` | 404 | Global variable doesn't exist |
| `internal_error` | 500 | Unexpected server error |

---

## 📚 Python Client Example

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Create a workflow
text_node = requests.post(
    f"{BASE_URL}/nodes",
    json={"type": "text", "name": "greeting"}
).json()

# Update it
requests.put(
    f"{BASE_URL}/nodes/{text_node['session_id']}",
    json={"parameters": {"text_string": "Hello API!"}}
)

# Create output node
fileout = requests.post(
    f"{BASE_URL}/nodes",
    json={"type": "file_out", "name": "output"}
).json()

# Connect them
requests.post(
    f"{BASE_URL}/connections",
    json={
        "source_node_path": text_node['path'],
        "source_output_index": 0,
        "target_node_path": fileout['path'],
        "target_input_index": 0
    }
)

# Execute
result = requests.post(
    f"{BASE_URL}/nodes/{fileout['session_id']}/execute"
).json()

print(f"Success: {result['success']}")
print(f"Time: {result['execution_time']:.2f}ms")
```

---

## 🔍 Interactive Documentation

### Swagger UI
`http://127.0.0.1:8000/api/v1/docs`

Features: Try endpoints interactively, view schemas, test workflows

### ReDoc
`http://127.0.0.1:8000/api/v1/redoc`

Features: Clean reference, mobile-friendly

---

## ⚡ Performance Tips

- **Batch reads**: Use `GET /workspace` instead of multiple `GET /nodes/{id}` calls
- **Partial updates**: Only send changed parameters in PUT requests
- **Connection management**: Connections auto-replace, no need to delete first
- **Error handling**: Check `success` field in execution responses
- **Session IDs**: Cache session IDs on frontend to avoid path lookups
