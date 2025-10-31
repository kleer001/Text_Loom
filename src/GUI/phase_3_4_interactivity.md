# Phase 3.4: Interactivity - Create and Delete Connections

## Objective
Enable users to create connections by dragging between handles and delete connections by selecting edges and pressing Delete.

## Prerequisites
- Phase 3.1 complete: Types and API client methods exist
- Phase 3.2 complete: Handles visible on all nodes
- Phase 3.3 complete: Existing connections render as edges
- React Flow `onConnect` and `onEdgesDelete` available

## Overview

React Flow provides built-in interaction handlers:
- **`onConnect`**: Called when user drags from one handle to another
- **`onEdgesDelete`**: Called when user selects edges and presses Delete/Backspace

We'll implement these handlers to:
1. Call backend API to create/delete connections
2. Update local edge state
3. Refresh workspace to sync node states (connected flags, connection counts)

**User interaction flow**:
```
Create:  Drag from output handle → input handle → onConnect → API → refresh
Delete:  Click edge → select → press Delete → onEdgesDelete → API → refresh
```

---

## React Flow Event Handlers

**Documentation**:
- [onConnect](https://reactflow.dev/api-reference/react-flow#onconnect)
- [onEdgesDelete](https://reactflow.dev/api-reference/react-flow#onedgesdelete)

### onConnect Handler

**Triggered when**: User successfully drags from source handle to target handle

**Receives**: `Connection` object
```typescript
interface Connection {
  source: string;           // Source node ID
  target: string;           // Target node ID
  sourceHandle: string | null;  // Source handle ID
  targetHandle: string | null;  // Target handle ID
}
```

**Example**: User drags from node "123" output-0 to node "456" input-0
```javascript
{
  source: "123",
  target: "456",
  sourceHandle: "output-0",
  targetHandle: "input-0"
}
```

### onEdgesDelete Handler

**Triggered when**: User selects edges and presses Delete or Backspace

**Receives**: `Edge[]` array of edges to delete

**Example**: User selects one edge and presses Delete
```javascript
[
  {
    id: "123-0-456-0",
    source: "123",
    target: "456",
    sourceHandle: "output-0",
    targetHandle: "input-0"
  }
]
```

---

## Implementation

### Step 1: Locate React Flow Component

Find where you render `<ReactFlow>` (from Phase 3.3). You'll add event handlers here.

**Current state** (after Phase 3.3):
```tsx
<ReactFlow
  nodes={nodes}
  edges={edges}
  fitView
/>
```

**After Phase 3.4**:
```tsx
<ReactFlow
  nodes={nodes}
  edges={edges}
  onConnect={onConnect}
  onEdgesDelete={onEdgesDelete}
  fitView
/>
```

### Step 2: Implement onConnect Handler

**File**: Your React Flow component (e.g., `NodeEditor.tsx`)

```tsx
import { useCallback } from 'react';
import { Connection, Edge } from 'reactflow';
import { apiClient } from '../apiClient';
import type { ConnectionRequest, NodeResponse } from '../types';

export function NodeEditor() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  // Handler for creating connections
  const onConnect = useCallback(async (connection: Connection) => {
    // 1. Parse handle IDs to get socket indices
    const sourceOutputIndex = parseInt(connection.sourceHandle?.replace('output-', '') || '0');
    const targetInputIndex = parseInt(connection.targetHandle?.replace('input-', '') || '0');

    // 2. Find node data to get paths
    const sourceNode = nodes.find(n => n.id === connection.source);
    const targetNode = nodes.find(n => n.id === connection.target);

    if (!sourceNode || !targetNode) {
      console.error('Source or target node not found');
      return;
    }

    // 3. Build API request
    const request: ConnectionRequest = {
      source_node_path: sourceNode.data.path,
      source_output_index: sourceOutputIndex,
      target_node_path: targetNode.data.path,
      target_input_index: targetInputIndex,
    };

    try {
      // 4. Call backend API
      const newConnection = await apiClient.createConnection(request);

      // 5. Update edges state
      setEdges(prevEdges => {
        // Remove any existing edge to same target input
        // (backend auto-replaces, so we mirror that behavior)
        const filtered = prevEdges.filter(e =>
          !(e.target === connection.target &&
            e.targetHandle === connection.targetHandle)
        );

        // Add new edge
        const newEdge: Edge = {
          id: `${newConnection.source_node_session_id}-${newConnection.source_output_index}-${newConnection.target_node_session_id}-${newConnection.target_input_index}`,
          source: connection.source,
          target: connection.target,
          sourceHandle: connection.sourceHandle!,
          targetHandle: connection.targetHandle!,
        };

        return [...filtered, newEdge];
      });

      // 6. Refresh workspace to sync node states
      await refreshWorkspace();

    } catch (error) {
      console.error('Failed to create connection:', error);
      // TODO: Show error notification to user
    }
  }, [nodes]);

  // Rest of component...
}
```

**Key steps**:
1. **Parse handle IDs**: Extract socket indices from handle IDs like "output-0"
2. **Find node data**: Look up nodes to get their `path` (required by API)
3. **Build request**: Create `ConnectionRequest` with paths and indices
4. **Call API**: Send to backend, which validates and creates connection
5. **Update edges**: Remove old edge to target input (if any), add new edge
6. **Refresh workspace**: Sync node states (connected flags, connection counts)

**Auto-replacement logic**:
The backend automatically replaces connections to the same target input. The frontend mirrors this by filtering out any existing edge with the same `target` and `targetHandle` before adding the new edge.

### Step 3: Implement onEdgesDelete Handler

**File**: Same React Flow component

```tsx
import { Edge } from 'reactflow';
import type { ConnectionDeleteRequest } from '../types';

export function NodeEditor() {
  // ... existing code ...

  // Handler for deleting connections
  const onEdgesDelete = useCallback(async (edgesToDelete: Edge[]) => {
    // Delete connections sequentially (backend processes one at a time)
    for (const edge of edgesToDelete) {
      // 1. Parse handle IDs to get socket indices
      const sourceOutputIndex = parseInt(edge.sourceHandle?.replace('output-', '') || '0');
      const targetInputIndex = parseInt(edge.targetHandle?.replace('input-', '') || '0');

      // 2. Find node data to get paths
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);

      if (!sourceNode || !targetNode) {
        console.warn('Source or target node not found for edge:', edge.id);
        continue; // Skip this edge
      }

      // 3. Build API request
      const request: ConnectionDeleteRequest = {
        source_node_path: sourceNode.data.path,
        source_output_index: sourceOutputIndex,
        target_node_path: targetNode.data.path,
        target_input_index: targetInputIndex,
      };

      try {
        // 4. Call backend API
        await apiClient.deleteConnection(request);

      } catch (error) {
        console.error('Failed to delete connection:', error);
        // TODO: Show error notification
        // Continue to next edge even if this one fails
      }
    }

    // 5. Remove edges from state
    setEdges(prevEdges =>
      prevEdges.filter(e => !edgesToDelete.includes(e))
    );

    // 6. Refresh workspace to sync node states
    await refreshWorkspace();

  }, [nodes]);

  // Rest of component...
}
```

**Key differences from onConnect**:
- **Sequential processing**: Loop through edges, delete one at a time
- **Continue on error**: If one deletion fails, continue with others
- **No replacement logic**: Just remove the specified edges
- **Multi-select support**: User can Shift+click multiple edges, all get deleted

### Step 4: Implement Workspace Refresh

Both handlers call `refreshWorkspace()` to sync node states after connection changes.

**Option A: Simple refresh** (reload entire workspace):
```tsx
async function refreshWorkspace() {
  const workspace = await apiClient.getWorkspace();

  // Update nodes
  setNodes(workspace.nodes.map(node => ({
    id: node.session_id,
    type: 'custom',
    position: { x: node.position[0], y: node.position[1] },
    data: node,
  })));

  // Update edges
  setEdges(connectionsToEdges(workspace.connections));
}
```

**Option B: Optimized refresh** (update node data only):
```tsx
async function refreshWorkspace() {
  const workspace = await apiClient.getWorkspace();

  // Update node data without resetting positions
  setNodes(prevNodes =>
    prevNodes.map(node => {
      const updated = workspace.nodes.find(n => n.session_id === node.id);
      if (updated) {
        return {
          ...node,
          data: updated, // Update data (connected flags, etc.)
        };
      }
      return node;
    })
  );

  // Edges are already updated in onConnect/onEdgesDelete
}
```

**Option C: Use context** (if using WorkspaceContext from Phase 3.3):
```tsx
const { refreshWorkspace } = useWorkspace();

// Call it in onConnect and onEdgesDelete
await refreshWorkspace();
```

**Why refresh?**
After creating/deleting a connection, node states change:
- `InputInfo.connected` flag updates
- `OutputInfo.connection_count` updates
- These affect handle styling and node logic

### Step 5: Add Handlers to ReactFlow Component

**File**: Your React Flow component

```tsx
import ReactFlow from 'reactflow';
import 'reactflow/dist/style.css';

export function NodeEditor() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  // ... onConnect handler ...
  // ... onEdgesDelete handler ...
  // ... refreshWorkspace function ...

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onConnect={onConnect}
        onEdgesDelete={onEdgesDelete}
        nodeTypes={nodeTypes}
        fitView
      >
        {/* Optional: Add controls, minimap, etc. */}
      </ReactFlow>
    </div>
  );
}
```

---

## Optional: Connection Validation

Prevent invalid connections before they reach the backend.

**Add to ReactFlow component**:
```tsx
import { Connection } from 'reactflow';

const isValidConnection = useCallback((connection: Connection) => {
  // Prevent self-connections
  if (connection.source === connection.target) {
    console.warn('Cannot connect node to itself');
    return false;
  }

  // Add other validation rules here:
  // - Check data type compatibility
  // - Prevent duplicate connections
  // - etc.

  return true; // Allow connection
}, []);

return (
  <ReactFlow
    isValidConnection={isValidConnection}
    // ... other props
  />
);
```

**When to use validation**:
- **Self-connections**: Prevent node connecting to itself
- **Type checking**: Ensure compatible data types (requires type info)
- **Duplicate prevention**: Block identical connections

**Note**: Backend also validates, so frontend validation is optional but improves UX.

---

## Error Handling

### Display Errors to User

Replace `console.error()` with user-visible notifications.

**Example with toast library** (react-toastify, react-hot-toast, etc.):
```tsx
import { toast } from 'react-hot-toast';

try {
  await apiClient.createConnection(request);
  toast.success('Connection created');
} catch (error) {
  toast.error(`Failed to create connection: ${error.message}`);
}
```

**Example with custom error UI**:
```tsx
const [errorMessage, setErrorMessage] = useState<string | null>(null);

try {
  await apiClient.createConnection(request);
  setErrorMessage(null);
} catch (error) {
  setErrorMessage(error.message);
}

// In render:
{errorMessage && (
  <div className="error-banner">
    {errorMessage}
    <button onClick={() => setErrorMessage(null)}>✕</button>
  </div>
)}
```

### Common Error Cases

**404: Node not found**
- User deleted a node while dragging connection
- Refresh workspace before retrying

**400: Invalid socket index**
- Handle ID parsing error
- Check handle ID format matches Phase 3.2

**Network errors**
- Backend server down
- Check `http://localhost:8000/api/v1` is accessible

### Rollback on Error

If API call fails, don't update edge state:

```tsx
try {
  await apiClient.createConnection(request);
  // Only update edges if API succeeded
  setEdges(/* ... */);
} catch (error) {
  console.error(error);
  // Edge state unchanged - connection not created
}
```

---

## Testing

### Manual Test: Create Connection

1. Start backend server with at least 2 nodes
2. Start frontend dev server
3. Open app in browser
4. **Drag from output handle to input handle**

**Expected behavior**:
- ✅ Cursor changes to indicate connection mode
- ✅ Connection line appears between handles
- ✅ Network request: `POST /api/v1/connections`
- ✅ Response: `ConnectionResponse` (201 Created)
- ✅ Edge added to React Flow
- ✅ Node states refresh (connected flags update)

**In browser DevTools**:
- Network tab shows POST request
- Console shows no errors
- React components re-render with new connection

### Manual Test: Replace Connection

1. Create a connection to an input
2. **Drag a different output to the same input**

**Expected behavior**:
- ✅ Old edge disappears
- ✅ New edge appears
- ✅ Only one connection to the input (backend auto-replaces)
- ✅ Source output can have multiple connections (fan-out)

### Manual Test: Delete Connection

1. Create a connection
2. **Click the edge** to select it (should highlight)
3. **Press Delete or Backspace**

**Expected behavior**:
- ✅ Edge selected (visual highlight)
- ✅ Press Delete: edge disappears
- ✅ Network request: `DELETE /api/v1/connections`
- ✅ Response: `SuccessResponse` (200 OK)
- ✅ Node states refresh (connected flag now false)

### Manual Test: Multi-Delete

1. Create multiple connections
2. **Click first edge**, then **Shift+click second edge**
3. **Press Delete**

**Expected behavior**:
- ✅ Both edges selected
- ✅ Both edges deleted
- ✅ Multiple DELETE requests (sequential)
- ✅ All edges removed from UI

### Automated Test Example

**File**: `NodeEditor.test.tsx` (optional)

```tsx
import { render, fireEvent, waitFor } from '@testing-library/react';
import { NodeEditor } from './NodeEditor';
import { apiClient } from '../apiClient';

jest.mock('../apiClient');

test('creates connection on onConnect', async () => {
  const mockCreateConnection = jest.fn().mockResolvedValue({
    source_node_session_id: '123',
    source_output_index: 0,
    target_node_session_id: '456',
    target_input_index: 0,
  });
  apiClient.createConnection = mockCreateConnection;

  const { getByTestId } = render(<NodeEditor />);

  // Simulate React Flow onConnect
  // (This requires React Flow testing setup - see their docs)

  await waitFor(() => {
    expect(mockCreateConnection).toHaveBeenCalledWith({
      source_node_path: '/text1',
      source_output_index: 0,
      target_node_path: '/fileout1',
      target_input_index: 0,
    });
  });
});
```

### Edge Case Testing

**Self-connection attempt**:
- Try dragging from output to input on same node
- If validation implemented: Should be prevented
- If no validation: Backend should reject with 400

**Connection to deleted node**:
- Delete target node while dragging
- Should fail gracefully (404 error)

**Rapid connection creation**:
- Quickly drag multiple connections
- All should be created (may be slow if sequential)

**Connection with no handles**:
- Try connecting nodes without handles (shouldn't be possible)
- Handles should exist from Phase 3.2

---

## Validation Checklist

- [ ] `onConnect` handler implemented
- [ ] `onEdgesDelete` handler implemented
- [ ] `refreshWorkspace()` function exists
- [ ] Handlers attached to `<ReactFlow>` component
- [ ] Create connection: drag works, API called, edge appears
- [ ] Delete connection: select + Delete works, API called, edge removed
- [ ] Multi-delete: Shift+click works, all edges deleted
- [ ] Auto-replacement: new connection replaces old one to same input
- [ ] Error handling: failed API calls don't crash app
- [ ] Node states refresh after connection changes
- [ ] No console errors during normal operation

---

## Deliverable

At the end of Phase 3.4:
- ✅ Users can create connections by dragging between handles
- ✅ Connections persist to backend immediately
- ✅ Backend auto-replaces existing input connections
- ✅ Users can delete connections by selecting and pressing Delete
- ✅ Multi-select delete works (sequential API calls)
- ✅ Workspace state refreshes after connection operations
- ✅ Error handling prevents crashes
- ✅ **Phase 3 is complete!**

---

## Complete Example

Here's a full React Flow component with all handlers:

```tsx
import { useCallback, useEffect, useState } from 'react';
import ReactFlow, { Connection, Edge, Node } from 'reactflow';
import 'reactflow/dist/style.css';
import { apiClient } from '../apiClient';
import { connectionsToEdges } from '../utils/edgeMapping';
import type { ConnectionRequest, ConnectionDeleteRequest } from '../types';

const nodeTypes = {
  custom: CustomNode,
};

export function NodeEditor() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  // Load workspace on mount
  useEffect(() => {
    refreshWorkspace();
  }, []);

  async function refreshWorkspace() {
    const workspace = await apiClient.getWorkspace();
    setNodes(workspace.nodes.map(node => ({
      id: node.session_id,
      type: 'custom',
      position: { x: node.position[0], y: node.position[1] },
      data: node,
    })));
    setEdges(connectionsToEdges(workspace.connections));
  }

  const onConnect = useCallback(async (connection: Connection) => {
    const sourceOutputIndex = parseInt(connection.sourceHandle?.replace('output-', '') || '0');
    const targetInputIndex = parseInt(connection.targetHandle?.replace('input-', '') || '0');

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

      setEdges(prevEdges => {
        const filtered = prevEdges.filter(e =>
          !(e.target === connection.target && e.targetHandle === connection.targetHandle)
        );

        return [...filtered, {
          id: `${newConnection.source_node_session_id}-${newConnection.source_output_index}-${newConnection.target_node_session_id}-${newConnection.target_input_index}`,
          source: connection.source,
          target: connection.target,
          sourceHandle: connection.sourceHandle!,
          targetHandle: connection.targetHandle!,
        }];
      });

      await refreshWorkspace();
    } catch (error) {
      console.error('Failed to create connection:', error);
    }
  }, [nodes]);

  const onEdgesDelete = useCallback(async (edgesToDelete: Edge[]) => {
    for (const edge of edgesToDelete) {
      const sourceOutputIndex = parseInt(edge.sourceHandle?.replace('output-', '') || '0');
      const targetInputIndex = parseInt(edge.targetHandle?.replace('input-', '') || '0');

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
      }
    }

    setEdges(prevEdges => prevEdges.filter(e => !edgesToDelete.includes(e)));
    await refreshWorkspace();
  }, [nodes]);

  const isValidConnection = useCallback((connection: Connection) => {
    return connection.source !== connection.target;
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onConnect={onConnect}
        onEdgesDelete={onEdgesDelete}
        isValidConnection={isValidConnection}
        nodeTypes={nodeTypes}
        fitView
      />
    </div>
  );
}
```

---

## Troubleshooting

**onConnect not firing**
- Check handler is attached: `onConnect={onConnect}`
- Verify handles exist on nodes (Phase 3.2)
- Check browser console for React Flow errors
- Ensure handles have correct `type` (source/target)

**Connection created but edge doesn't appear**
- Check `setEdges()` is called after API success
- Verify edge ID is unique
- Check sourceHandle and targetHandle match handle IDs

**onEdgesDelete not firing**
- Edge must be selected first (click to select)
- Press Delete or Backspace key
- Check handler is attached: `onEdgesDelete={onEdgesDelete}`

**API call fails**
- Check backend server is running
- Verify node paths are correct
- Check socket indices are valid
- See Network tab for detailed error response

**Workspace doesn't refresh**
- Verify `refreshWorkspace()` is called after API
- Check API call is `await`ed before refresh
- Ensure refresh updates both nodes and edges

**Performance issues with many connections**
- Sequential deletion is slow for many edges
- Consider batching (backend would need batch endpoint)
- For now, this is acceptable for MVP

---

## Next Steps

Phase 3 is now complete! You have full connection management:
- Visual handles on nodes
- Existing connections displayed
- Create connections by dragging
- Delete connections by selecting

**Suggested next features**:
- Edge styling and colors
- Connection validation by data type
- Batch delete optimization
- Connection tooltips/labels
- Undo/redo for connections
- Keyboard shortcuts for connection operations
