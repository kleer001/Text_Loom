# Phase 3: Connection Management & Data Flow

## Objective
Implement connection creation and deletion between nodes using React Flow's built-in edge system, backed by the TextLoom API.

## Overview

This phase connects the React Flow UI to the TextLoom backend's connection management system. The backend already implements connection creation (via `Node.set_input()`) and deletion (via `Node.remove_connection()`). This phase exposes those operations through the GUI.

### Key Technologies
- **React Flow**: Node-based editor library with built-in connection/edge support
- **Backend API**: FastAPI endpoints at `/api/v1/connections`
- **State Management**: React Context for workspace state synchronization

---

## Data Structures

### Frontend Types (src/GUI/src/types.ts)

#### InputInfo
```typescript
interface InputInfo {
  index: number | string;    // Socket index or key
  name: string;              // Display name (e.g., "input", "text_in")
  data_type: string;         // Type annotation (e.g., "List[str]")
  connected: boolean;        // Whether this input has a connection
}
```

#### OutputInfo
```typescript
interface OutputInfo {
  index: number | string;    // Socket index or key
  name: string;              // Display name (e.g., "output", "result")
  data_type: string;         // Type annotation (e.g., "List[str]")
  connection_count: number;  // Number of outgoing connections
}
```

#### ConnectionResponse
```typescript
interface ConnectionResponse {
  source_node_session_id: string;
  source_node_path: string;
  source_output_index: number;
  source_output_name: string;
  target_node_session_id: string;
  target_node_path: string;
  target_input_index: number;
  target_input_name: string;
}
```

**Note**: Connections have no unique `id` field. They are identified by the 4-tuple:
`(source_node_path, source_output_index, target_node_path, target_input_index)`

#### ConnectionRequest (ADD THIS to types.ts)
```typescript
interface ConnectionRequest {
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}
```

#### ConnectionDeleteRequest (ADD THIS to types.ts)
```typescript
interface ConnectionDeleteRequest {
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}
```

### Backend Models (src/api/models.py)

These models are already implemented. See `api/models.py:251-284` for full definitions.

---

## API Endpoints

### POST /api/v1/connections

**Implementation**: `src/api/routers/connections.py:23-124`

**Request Body**:
```json
{
  "source_node_path": "/text1",
  "source_output_index": 0,
  "target_node_path": "/fileout1",
  "target_input_index": 0
}
```

**Response**: `ConnectionResponse` (201 Created)

**Behavior**:
- Creates connection from source output to target input
- **Auto-replaces** existing connection on target input (backend behavior)
- Validates node existence and socket indices
- Calls `target_node.set_input(target_input_index, source_node, source_output_index)`

**Error Cases**:
- 404: Node not found
- 400: Invalid socket index
- 500: Connection creation failed

### DELETE /api/v1/connections

**Implementation**: `src/api/routers/connections.py:127-205`

**Request Body**:
```json
{
  "source_node_path": "/text1",
  "source_output_index": 0,
  "target_node_path": "/fileout1",
  "target_input_index": 0
}
```

**Response**: `SuccessResponse` (200 OK)

**Behavior**:
- Finds connection at target input
- Verifies it matches source parameters
- Calls `target_node.remove_connection(connection)`

**Error Cases**:
- 404: Node or connection not found
- 404: Connection mismatch (different source than specified)

---

## Implementation Tasks

### 1. Add Missing TypeScript Types

**File**: `src/GUI/src/types.ts`

Add after line 79 (after `NodeUpdateRequest`):

```typescript
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

### 2. Add API Client Methods

**File**: `src/GUI/src/apiClient.ts`

Add these methods to the `ApiClient` class:

```typescript
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

Don't forget to import `ConnectionRequest`, `ConnectionResponse`, and `ConnectionDeleteRequest` from `./types`.

### 3. Render Input/Output Handles on Nodes

**File**: Create or modify your React Flow custom node component

Each node must render `Handle` components from React Flow for its inputs and outputs.

**Reference**: [React Flow Custom Nodes](https://reactflow.dev/learn/customization/custom-nodes)

**Example**:
```tsx
import { Handle, Position } from 'reactflow';

function CustomNode({ data }: { data: NodeResponse }) {
  return (
    <div className="custom-node">
      {/* Input handles on left side */}
      {data.inputs.map((input) => (
        <Handle
          key={`input-${input.index}`}
          type="target"
          position={Position.Left}
          id={`input-${input.index}`}
          style={{ top: calculateSocketY(input.index, data.inputs.length) }}
        />
      ))}

      {/* Node content */}
      <div>{data.name}</div>

      {/* Output handles on right side */}
      {data.outputs.map((output) => (
        <Handle
          key={`output-${output.index}`}
          type="source"
          position={Position.Right}
          id={`output-${output.index}`}
          style={{ top: calculateSocketY(output.index, data.outputs.length) }}
        />
      ))}
    </div>
  );
}
```

**Important**:
- `type="target"` for inputs (left side)
- `type="source"` for outputs (right side)
- Handle `id` must match the socket index for connection mapping
- Use `data.inputs` and `data.outputs` from `NodeResponse`

### 4. Map NodeResponse to React Flow Node Data

When converting `NodeResponse[]` to React Flow nodes, include the full response as `data`:

```typescript
const reactFlowNodes = nodes.map(node => ({
  id: node.session_id,
  type: 'custom',  // Your custom node type
  position: { x: node.position[0], y: node.position[1] },
  data: node,      // Full NodeResponse available in custom node
}));
```

### 5. Map ConnectionResponse to React Flow Edges

**File**: Your workspace state manager or React Flow component

React Flow edges require:
- Unique `id`
- `source`: source node id
- `target`: target node id
- `sourceHandle`: handle id on source node
- `targetHandle`: handle id on target node

**Mapping**:
```typescript
const reactFlowEdges = connections.map(conn => ({
  id: `${conn.source_node_session_id}-${conn.source_output_index}-${conn.target_node_session_id}-${conn.target_input_index}`,
  source: conn.source_node_session_id,
  target: conn.target_node_session_id,
  sourceHandle: `output-${conn.source_output_index}`,
  targetHandle: `input-${conn.target_input_index}`,
}));
```

### 6. Handle Connection Creation

**Reference**: [React Flow onConnect](https://reactflow.dev/api-reference/react-flow#onconnect)

Add `onConnect` handler to your `<ReactFlow>` component:

```tsx
import { useCallback } from 'react';
import { Connection, addEdge } from 'reactflow';

function WorkspaceEditor() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  const onConnect = useCallback(async (connection: Connection) => {
    // Parse handle IDs to get socket indices
    const sourceOutputIndex = parseInt(connection.sourceHandle.replace('output-', ''));
    const targetInputIndex = parseInt(connection.targetHandle.replace('input-', ''));

    // Find node paths from session IDs
    const sourceNode = nodes.find(n => n.id === connection.source);
    const targetNode = nodes.find(n => n.id === connection.target);

    if (!sourceNode || !targetNode) return;

    const request: ConnectionRequest = {
      source_node_path: sourceNode.data.path,
      source_output_index: sourceOutputIndex,
      target_node_path: targetNode.data.path,
      target_input_index: targetInputIndex,
    };

    try {
      const newConnection = await apiClient.createConnection(request);

      // Add to workspace context and React Flow edges
      // (Backend auto-replaces existing connection if needed)
      setEdges(edges => {
        // Remove any existing edge to same target input
        const filtered = edges.filter(e =>
          !(e.target === connection.target &&
            e.targetHandle === connection.targetHandle)
        );

        // Add new edge
        return addEdge({
          id: `${newConnection.source_node_session_id}-${newConnection.source_output_index}-${newConnection.target_node_session_id}-${newConnection.target_input_index}`,
          source: connection.source,
          target: connection.target,
          sourceHandle: connection.sourceHandle,
          targetHandle: connection.targetHandle,
        }, filtered);
      });

      // Refresh workspace to get updated node states
      await refreshWorkspace();

    } catch (error) {
      console.error('Failed to create connection:', error);
      // Show error toast/notification
    }
  }, [nodes]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onConnect={onConnect}
      // ... other props
    />
  );
}
```

**Key Points**:
- React Flow calls `onConnect` when user drags from output handle to input handle
- Backend automatically replaces existing input connections
- Frontend should remove old edge to same target input before adding new one
- Refresh workspace after connection to sync state

### 7. Handle Connection Deletion

**Reference**: [React Flow onEdgesDelete](https://reactflow.dev/api-reference/react-flow#onedgesdelete)

Add `onEdgesDelete` handler:

```tsx
const onEdgesDelete = useCallback(async (edgesToDelete: Edge[]) => {
  // Delete connections sequentially (backend supports one at a time)
  for (const edge of edgesToDelete) {
    // Parse IDs from edge
    const sourceOutputIndex = parseInt(edge.sourceHandle.replace('output-', ''));
    const targetInputIndex = parseInt(edge.targetHandle.replace('input-', ''));

    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);

    if (!sourceNode || !targetNode) continue;

    const request: ConnectionDeleteRequest = {
      source_node_path: sourceNode.data.path,
      source_output_index: sourceOutputIndex,
      target_node_path: targetNode.data.path,
      target_input_index: targetInputIndex,
    };

    try {
      await apiClient.deleteConnection(request);
    } catch (error) {
      console.error('Failed to delete connection:', error);
      // Show error notification
    }
  }

  // Remove from React Flow edges
  setEdges(edges => edges.filter(e => !edgesToDelete.includes(e)));

  // Refresh workspace
  await refreshWorkspace();

}, [nodes]);

return (
  <ReactFlow
    onEdgesDelete={onEdgesDelete}
    // ... other props
  />
);
```

**Edge Selection**:
- Click edge to select (React Flow built-in)
- Shift+click for multi-select (React Flow built-in)
- Press Delete/Backspace to delete selected edges
- React Flow automatically calls `onEdgesDelete` with selected edges

**Deletion is Sequential**: Loop through edges and delete one at a time, as backend only accepts single `ConnectionDeleteRequest`.

### 8. Connection Validation (Optional)

If you want to prevent certain connections before they're created:

**Reference**: [React Flow isValidConnection](https://reactflow.dev/api-reference/react-flow#isvalidconnection)

```tsx
const isValidConnection = useCallback((connection: Connection) => {
  // Prevent self-connections
  if (connection.source === connection.target) {
    return false;
  }

  // Add other validation rules here
  // - Data type compatibility
  // - Prevent duplicate connections
  // etc.

  return true;
}, []);

return (
  <ReactFlow
    isValidConnection={isValidConnection}
    // ... other props
  />
);
```

---

## Backend Reference

### Backend Connection Logic

**File**: `src/core/base_classes.py` (assumed from API usage)

**Key Methods**:
- `Node.set_input(input_index, source_node, output_index)`: Creates connection, auto-replaces existing
- `Node.remove_connection(connection)`: Removes specific connection
- `Node.input_names()`: Returns dict of `{index: name}`
- `Node.output_names()`: Returns dict of `{index: name}`
- `Node.input_data_types()`: Returns dict of `{index: type_string}`
- `Node.output_data_types()`: Returns dict of `{index: type_string}`
- `Node._inputs`: Dict of `{index: NodeConnection}`
- `Node._outputs`: Dict of `{index: [NodeConnection, ...]}`

**Connection Auto-Replacement**:
When `set_input()` is called on an already-connected input, the backend automatically removes the old connection before creating the new one. The frontend doesn't need to handle this explicitly on creation, but should handle it when updating the edge list.

---

## Testing Checklist

### Manual Testing
- [ ] Create connection by dragging from output to input
- [ ] Verify connection appears in React Flow
- [ ] Verify backend receives POST /connections
- [ ] Check workspace state updates with new connection
- [ ] Replace existing connection (drag new connection to occupied input)
- [ ] Verify old connection is removed, new one added
- [ ] Select edge by clicking
- [ ] Select multiple edges with Shift+click
- [ ] Delete edge with Delete/Backspace key
- [ ] Verify backend receives DELETE /connections
- [ ] Multi-input nodes: create connections to different inputs
- [ ] Multi-output nodes: create multiple connections from same output
- [ ] Nodes with no inputs/outputs render without handles

### Edge Cases
- [ ] Connection to non-existent node (should fail gracefully)
- [ ] Connection to invalid socket index (should fail gracefully)
- [ ] Delete non-existent connection (should handle error)
- [ ] Network error during connection creation (should rollback UI state)
- [ ] Self-connection (optional: prevent if validation implemented)

---

## Deliverables

At the end of Phase 3:
- ✅ TypeScript types for connection requests/responses
- ✅ API client methods for create/delete connections
- ✅ Input/output handles rendered on all nodes
- ✅ Connection creation via React Flow drag-and-drop
- ✅ Connection deletion via edge selection + Delete key
- ✅ Backend auto-replacement of input connections
- ✅ Workspace state synchronization after connection ops
- ✅ All connection operations persist to backend immediately

---

## Future Enhancements (Not in Phase 3)

- Custom edge styling (colors, animations)
- Visual feedback during drag (temporary connection line)
- Connection compatibility hints
- Handle color changes (connected vs unconnected)
- Data type validation before connection
- Batch delete optimization
- Connection labels showing data flow
- Animated edges showing data direction
- Connection error states
