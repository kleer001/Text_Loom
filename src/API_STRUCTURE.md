# TextLoom API Structure

Complete file organization and implementation guide for the TextLoom REST API.

## 📁 Directory Structure

```
TextLoom/
├── api/
│   ├── __init__.py                 # API package initialization
│   ├── main.py                     # FastAPI app setup & CORS
│   ├── models.py                   # Pydantic DTOs & conversion utilities
│   └── routers/
│       ├── __init__.py             # Routers package
│       ├── nodes.py                # Node endpoints
│       └── workspace.py            # Workspace endpoints
├── test_api_endpoints.py           # Complete test script
├── API_TESTING_GUIDE.md           # Testing documentation
└── API_STRUCTURE.md               # This file
```

## 📄 File Descriptions

### `api/models.py`
**Purpose:** Data Transfer Objects (DTOs) and type definitions

**Contains:**
- `NodeResponse` - Complete node state with all parameters
- `NodeCreateRequest` - Node creation payload
- `NodeUpdateRequest` - Node update payload
- `ParameterInfo` - Parameter details with type info
- `InputInfo` / `OutputInfo` - Socket information
- `ConnectionResponse` - Connection between nodes
- `ConnectionRequest` - Connection creation payload
- `WorkspaceState` - Complete workspace snapshot
- `ExecutionResponse` - Node execution results
- `ErrorResponse` / `SuccessResponse` - Standard responses
- `node_to_response()` - Conversion from internal Node to DTO
- `connection_to_response()` - Conversion from NodeConnection to DTO

**Key Design Decisions:**
- Uses `session_id` as unique identifier
- Includes UI state (position, color, selected)
- Exposes raw parameter values (not evaluated)
- Read-only flag for output parameters
- Multi-output nodes return flat list format

### `api/main.py`
**Purpose:** FastAPI application entry point

**Contains:**
- FastAPI app initialization
- CORS middleware configuration
- Router registration
- Root health check endpoint
- API info endpoint

**Configuration:**
- Swagger UI at `/api/v1/docs`
- ReDoc at `/api/v1/redoc`
- CORS allows common dev server ports

### `api/routers/nodes.py`
**Purpose:** Node-related API endpoints

**Endpoints:**
- `GET /api/v1/nodes` - List all nodes
- `GET /api/v1/nodes/{session_id}` - Get single node details

**Features:**
- Full node details in responses
- 404 handling for missing nodes
- Error handling for conversion failures
- Session ID-based lookup

### `api/routers/workspace.py`
**Purpose:** Workspace state endpoint

**Endpoints:**
- `GET /api/v1/workspace` - Complete workspace state

**Features:**
- Returns all nodes, connections, and globals
- Deduplicates connections
- Comprehensive error handling

### `test_api_endpoints.py`
**Purpose:** Automated testing script

**Features:**
- Creates test workspace with nodes
- Tests all endpoints
- Displays formatted results
- Provides usage examples

## 🔄 Data Flow

```
Frontend Request
    ↓
FastAPI Router (api/routers/*.py)
    ↓
Backend Node Classes (core/*.py)
    ↓
Conversion Functions (api/models.py)
    ↓
Pydantic Models (validation)
    ↓
JSON Response
    ↓
Frontend
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn
```

### 2. Create Test Workspace
```bash
python test_api_endpoints.py
# (Follow prompts to start server)
```

### 3. Start Server
```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Test Endpoints
Open browser to: http://127.0.0.1:8000/api/v1/docs

## 📊 API Endpoints

### Read-Only Endpoints (Implemented)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/v1` | API info |
| GET | `/api/v1/workspace` | Complete workspace state |
| GET | `/api/v1/nodes` | List all nodes |
| GET | `/api/v1/nodes/{session_id}` | Get single node |

### Write Endpoints (Future)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/nodes` | Create new node |
| PUT | `/api/v1/nodes/{session_id}` | Update node |
| DELETE | `/api/v1/nodes/{session_id}` | Delete node |
| POST | `/api/v1/connections` | Create connection |
| DELETE | `/api/v1/connections` | Delete connection |
| POST | `/api/v1/nodes/{session_id}/execute` | Execute node |
| PUT | `/api/v1/globals/{key}` | Set global variable |

## 🔧 Configuration

### CORS Origins
Edit `api/main.py` to add your frontend URLs:
```python
origins = [
    "http://localhost:3000",      # Your frontend dev server
    "http://localhost:5173",
]
```

### Server Port
Change port in startup command:
```bash
uvicorn api.main:app --reload --port 9000
```

### API Prefix
Modify in `api/main.py`:
```python
app.include_router(
    nodes.router,
    prefix="/api/v2",  # Change version
    tags=["nodes"]
)
```

## 🧪 Testing Strategies

### 1. Interactive (Swagger UI)
Best for: Initial exploration, manual testing
- Open http://127.0.0.1:8000/api/v1/docs
- Click "Try it out" on any endpoint
- See formatted responses

### 2. Command Line (curl)
Best for: Quick checks, scripting
```bash
curl http://127.0.0.1:8000/api/v1/workspace | jq
```

### 3. Python Script
Best for: Automated testing, integration tests
```bash
python test_api_endpoints.py
```

### 4. Frontend Integration
Best for: Real-world usage
```javascript
const response = await fetch('http://127.0.0.1:8000/api/v1/workspace');
const workspace = await response.json();
```

## 📝 Response Format Examples

### Single Node
```json
{
  "session_id": 123456789,
  "name": "text1",
  "path": "/text1",
  "type": "text",
  "state": "unchanged",
  "parameters": {
    "text_string": {
      "type": "STRING",
      "value": "Hello",
      "default": "",
      "read_only": false
    }
  },
  "inputs": [],
  "outputs": [],
  "errors": [],
  "warnings": [],
  "position": [100.0, 200.0],
  "selected": false
}
```

### Workspace State
```json
{
  "nodes": [ /* array of NodeResponse */ ],
  "connections": [ /* array of ConnectionResponse */ ],
  "globals": {
    "TEST_VAR": "value",
    "VERSION": "1.0.0"
  }
}
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'api'"
```bash
# Run from project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn api.main:app --reload
```

### "Connection refused"
- Ensure server is running
- Check correct port (default: 8000)
- Verify no other process using the port

### "Empty workspace"
- Create test nodes first
- Run `test_api_endpoints.py` to setup test data

### "CORS error"
- Add your frontend URL to `origins` list in `api/main.py`
- Restart server after changes

## 🎯 Next Steps

1. ✅ **Read-only endpoints** (Done!)
2. 🔄 **Write endpoints** - Create, update, delete nodes
3. 🔄 **Execution endpoints** - Trigger node cooking
4. 🔄 **Connection management** - Create/delete connections
5. 🔄 **Global variables** - CRUD operations
6. 🔄 **WebSocket support** - Real-time updates (optional)

## 📚 Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic Documentation: https://docs.pydantic.dev/
- Swagger UI: http://127.0.0.1:8000/api/v1/docs
- ReDoc: http://127.0.0.1:8000/api/v1/redoc