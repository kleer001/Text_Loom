# Phase 3.1: Foundation - TypeScript Types & API Client

## Objective
Add TypeScript type definitions and API client methods for connection management. This is a foundational step with no UI changes.

## Prerequisites
- Phase 1 complete: Node creation/deletion working
- Phase 2 complete: Node editing working
- Backend connection endpoints exist at `/api/v1/connections`

## Overview

This phase adds the frontend infrastructure for connection management without changing any UI. We're extending existing files with new types and API methods that will be used in later phases.

The backend already has connection endpoints (see `src/api/routers/connections.py`), and we already have `ConnectionResponse` in our types. We need to add the **request** types that we'll send to the backend.

---

## Implementation

### Task 1: Add Connection Request Types

**File**: `src/GUI/src/types.ts`

**Location**: Add after `NodeUpdateRequest` (around line 79)

**Code to add**:
```typescript
// Request types for connection operations
export interface ConnectionRequest {
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}

export interface ConnectionDeleteRequest {
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}
```

**Why these types?**
- `ConnectionRequest`: Sent to `POST /api/v1/connections` to create a connection
- `ConnectionDeleteRequest`: Sent to `DELETE /api/v1/connections` to remove a connection
- Both are identical in structure but semantically different (create vs delete)
- Match backend Pydantic models in `src/api/models.py:251-284`

**Already exists**: `ConnectionResponse` (lines 43-52 in types.ts) - this is what the backend returns

---

### Task 2: Add API Client Methods

**File**: `src/GUI/src/apiClient.ts`

**Location**: Add to `ApiClient` class after `listNodes()` method (after line 75)

**Code to add**:
```typescript
// Connection operations
async createConnection(request: ConnectionRequest): Promise<ConnectionResponse> {
  return this.fetchJson<ConnectionResponse>('/connections', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

async deleteConnection(request: ConnectionDeleteRequest): Promise<void> {
  await this.fetchJson<void>('/connections', {
    method: 'DELETE',
    body: JSON.stringify(request),
  });
}
```

**Update imports**: Add to the import statement at the top of the file:
```typescript
import type {
  WorkspaceState,
  ApiError,
  NodeResponse,
  NodeCreateRequest,
  NodeUpdateRequest,
  ConnectionRequest,      // ADD THIS
  ConnectionResponse,     // ADD THIS
  ConnectionDeleteRequest // ADD THIS
} from './types';
```

**Method details**:

#### `createConnection()`
- **Endpoint**: `POST /api/v1/connections`
- **Returns**: `ConnectionResponse` with full connection details
- **Backend behavior**: Auto-replaces existing connection if target input is already connected
- **Throws**: Error if nodes not found or socket indices invalid

#### `deleteConnection()`
- **Endpoint**: `DELETE /api/v1/connections`
- **Returns**: Nothing (void)
- **Backend behavior**: Removes connection from both nodes
- **Throws**: Error if connection not found or doesn't match parameters

---

## Backend API Reference

### POST /api/v1/connections

**Implementation**: `src/api/routers/connections.py:23-124`

**Request Example**:
```json
{
  "source_node_path": "/text1",
  "source_output_index": 0,
  "target_node_path": "/fileout1",
  "target_input_index": 0
}
```

**Response Example** (201 Created):
```json
{
  "source_node_session_id": "123456789",
  "source_node_path": "/text1",
  "source_output_index": 0,
  "source_output_name": "output",
  "target_node_session_id": "987654321",
  "target_node_path": "/fileout1",
  "target_input_index": 0,
  "target_input_name": "input"
}
```

**Important**: The backend calls `target_node.set_input()` which **automatically replaces** any existing connection to that input. The frontend doesn't need to delete the old connection first.

### DELETE /api/v1/connections

**Implementation**: `src/api/routers/connections.py:127-205`

**Request Example**:
```json
{
  "source_node_path": "/text1",
  "source_output_index": 0,
  "target_node_path": "/fileout1",
  "target_input_index": 0
}
```

**Response Example** (200 OK):
```json
{
  "success": true,
  "message": "Connection from /text1[0] to /fileout1[0] deleted"
}
```

**Important**: You must specify the exact connection to delete using all 4 parameters. The backend verifies the connection matches before deleting.

---

## Testing

### Compilation Test
After adding the types and methods, verify TypeScript compiles:

```bash
cd src/GUI
npm run build
```

**Expected**: No TypeScript errors related to the new types.

### Type Import Test
Create a test file or use browser console to verify imports work:

```typescript
import { ConnectionRequest, ConnectionDeleteRequest } from './types';
import { apiClient } from './apiClient';

// These should not show TypeScript errors
const request: ConnectionRequest = {
  source_node_path: "/test1",
  source_output_index: 0,
  target_node_path: "/test2",
  target_input_index: 0
};

// Method exists on apiClient
console.log(typeof apiClient.createConnection); // "function"
console.log(typeof apiClient.deleteConnection); // "function"
```

### API Method Test (Optional)
If you want to test the actual API calls, you'll need:
1. Backend server running (`uvicorn api.main:app`)
2. At least 2 nodes created with outputs/inputs

```typescript
// Example: Create a connection (requires real nodes)
const conn = await apiClient.createConnection({
  source_node_path: "/text1",
  source_output_index: 0,
  target_node_path: "/fileout1",
  target_input_index: 0
});
console.log(conn); // Should show ConnectionResponse

// Delete it
await apiClient.deleteConnection({
  source_node_path: "/text1",
  source_output_index: 0,
  target_node_path: "/fileout1",
  target_input_index: 0
});
```

---

## Validation Checklist

- [ ] TypeScript types added to `types.ts`
- [ ] Types exported correctly
- [ ] API methods added to `apiClient.ts`
- [ ] Imports updated in `apiClient.ts`
- [ ] No TypeScript compilation errors
- [ ] `npm run build` succeeds
- [ ] Types can be imported in other files
- [ ] API methods are accessible via `apiClient` instance

---

## Deliverable

At the end of Phase 3.1:
- ✅ `ConnectionRequest` type exists and is exported
- ✅ `ConnectionDeleteRequest` type exists and is exported
- ✅ `apiClient.createConnection()` method exists
- ✅ `apiClient.deleteConnection()` method exists
- ✅ TypeScript compiles without errors
- ✅ No UI changes (this is purely infrastructure)

**What's NOT included**:
- No UI for creating connections (that's Phase 3.4)
- No handles on nodes (that's Phase 3.2)
- No edges displayed (that's Phase 3.3)

---

## Next Phase

**Phase 3.2** will add visual handles (input/output sockets) to nodes, which will enable connection points for users to interact with.

---

## Troubleshooting

**TypeScript error: "Cannot find name 'ConnectionRequest'"**
- Make sure you added `export` before the interface
- Check the import statement in other files includes `ConnectionRequest`

**API call fails with 404**
- Verify backend server is running on `http://localhost:8000`
- Check the node paths exist by calling `apiClient.listNodes()`
- Verify socket indices are valid (0-based, within range)

**API call fails with 400 "Invalid socket index"**
- Check the node actually has that many inputs/outputs
- Use `apiClient.getNode(sessionId)` to see available inputs/outputs
- Remember indices are 0-based

**TypeScript error in apiClient.ts after adding methods**
- Make sure you added the import types at the top
- Check you didn't break the existing code structure
- Verify the closing braces of the `ApiClient` class are correct
