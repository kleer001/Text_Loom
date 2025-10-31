# Phase 3.3: Data Mapping - Display Connection Lines

## Objective
Convert backend `ConnectionResponse[]` data to React Flow `Edge[]` and display existing connections as visible lines between nodes.

## Prerequisites
- Phase 3.1 complete: Types and API methods exist
- Phase 3.2 complete: Handles visible on nodes
- Workspace state includes `connections: ConnectionResponse[]`
- React Flow rendering nodes with handles

## Overview

React Flow displays connections as **edges** - lines between node handles. We already have connection data from the backend (loaded via `/api/v1/workspace`), but it's not yet visualized.

This phase is pure data transformation: converting backend connection format to React Flow edge format.

**Backend format** (`ConnectionResponse`):
```typescript
{
  source_node_session_id: "123",
  source_node_path: "/text1",
  source_output_index: 0,
  source_output_name: "output",
  target_node_session_id: "456",
  target_node_path: "/fileout1",
  target_input_index: 0,
  target_input_name: "input"
}
```

**React Flow format** (`Edge`):
```typescript
{
  id: "123-0-456-0",              // Unique edge ID
  source: "123",                  // Source node ID
  target: "456",                  // Target node ID
  sourceHandle: "output-0",       // Source handle ID
  targetHandle: "input-0"         // Target handle ID
}
```

---

## React Flow Edge Basics

**Documentation**: [React Flow Edges](https://reactflow.dev/learn/concepts/terms-and-definitions#edges)

### Edge Structure
```typescript
interface Edge {
  id: string;               // Unique identifier
  source: string;           // Source node ID
  target: string;           // Target node ID
  sourceHandle?: string;    // ID of source handle (optional but needed for multi-handle)
  targetHandle?: string;    // ID of target handle (optional but needed for multi-handle)
  type?: string;            // Edge type (default, smoothstep, step, straight)
  animated?: boolean;       // Animate the edge
  style?: CSSProperties;    // Custom styling
  label?: string;           // Edge label
  data?: any;              // Custom data
}
```

### Multi-Handle Requirement
When nodes have multiple handles (inputs/outputs), you **must** specify `sourceHandle` and `targetHandle`. Otherwise React Flow doesn't know which handles to connect.

---

## Implementation

### Step 1: Locate Your React Flow Component

Find where you render `<ReactFlow>` and manage nodes/edges state.

**Common patterns**:
```tsx
// Pattern 1: Local state
const [nodes, setNodes] = useState<Node[]>([]);
const [edges, setEdges] = useState<Edge[]>([]);

// Pattern 2: Context/Redux
const { nodes, edges } = useWorkspace();

// Pattern 3: Direct props
<ReactFlow nodes={workspaceNodes} edges={workspaceEdges} />
```

**Example file structure**:
```
src/GUI/src/
  components/
    NodeEditor.tsx       # React Flow component ← YOU'LL EDIT THIS
    CustomNode.tsx       # Node renderer (from Phase 3.2)
  contexts/
    WorkspaceContext.tsx # State management (possibly here too)
```

### Step 2: Create Edge Mapping Function

Create a utility function to convert `ConnectionResponse[]` to `Edge[]`.

**File**: Create `src/GUI/src/utils/edgeMapping.ts` or add to existing utils

```typescript
import type { Edge } from 'reactflow';
import type { ConnectionResponse } from '../types';

/**
 * Convert ConnectionResponse from backend to React Flow Edge format
 */
export function connectionToEdge(connection: ConnectionResponse): Edge {
  return {
    id: `${connection.source_node_session_id}-${connection.source_output_index}-${connection.target_node_session_id}-${connection.target_input_index}`,
    source: connection.source_node_session_id,
    target: connection.target_node_session_id,
    sourceHandle: `output-${connection.source_output_index}`,
    targetHandle: `input-${connection.target_input_index}`,
  };
}

/**
 * Convert array of ConnectionResponse to Edge[]
 */
export function connectionsToEdges(connections: ConnectionResponse[]): Edge[] {
  return connections.map(connectionToEdge);
}
```

**Edge ID Format**:
```
{source_node_session_id}-{source_output_index}-{target_node_session_id}-{target_input_index}
```

This creates a unique ID for each connection using all 4 identifying components.

**Handle ID Mapping**:
- Backend: `source_output_index: 0` → React Flow: `sourceHandle: "output-0"`
- Backend: `target_input_index: 0` → React Flow: `targetHandle: "input-0"`

This matches the handle IDs we created in Phase 3.2.

### Step 3: Import and Use in React Flow Component

**File**: Your React Flow component (e.g., `NodeEditor.tsx`)

```tsx
import { useEffect, useState } from 'react';
import ReactFlow, { Node, Edge } from 'reactflow';
import { connectionsToEdges } from '../utils/edgeMapping';
import { apiClient } from '../apiClient';
import type { WorkspaceState } from '../types';

export function NodeEditor() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    // Load workspace on mount
    loadWorkspace();
  }, []);

  async function loadWorkspace() {
    const workspace: WorkspaceState = await apiClient.getWorkspace();

    // Convert nodes to React Flow format
    const rfNodes = workspace.nodes.map(node => ({
      id: node.session_id,
      type: 'custom',
      position: { x: node.position[0], y: node.position[1] },
      data: node,
    }));

    // Convert connections to React Flow edges
    const rfEdges = connectionsToEdges(workspace.connections);

    setNodes(rfNodes);
    setEdges(rfEdges);
  }

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      fitView
    />
  );
}
```

**Key changes**:
1. Import `connectionsToEdges` helper
2. Call it with `workspace.connections`
3. Set edges state with result
4. Pass `edges` to `<ReactFlow edges={edges} />`

### Step 4: Alternative - Use Workspace Context

If you're using a context for workspace state:

**File**: `WorkspaceContext.tsx` (or similar)

```tsx
import { createContext, useContext, useState, useEffect } from 'react';
import { Edge, Node } from 'reactflow';
import { apiClient } from '../apiClient';
import { connectionsToEdges } from '../utils/edgeMapping';
import type { WorkspaceState, NodeResponse, ConnectionResponse } from '../types';

interface WorkspaceContextType {
  nodes: Node[];
  edges: Edge[];
  rawNodes: NodeResponse[];
  rawConnections: ConnectionResponse[];
  refreshWorkspace: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | null>(null);

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const [rawNodes, setRawNodes] = useState<NodeResponse[]>([]);
  const [rawConnections, setRawConnections] = useState<ConnectionResponse[]>([]);

  // Convert to React Flow format
  const nodes: Node[] = rawNodes.map(node => ({
    id: node.session_id,
    type: 'custom',
    position: { x: node.position[0], y: node.position[1] },
    data: node,
  }));

  const edges: Edge[] = connectionsToEdges(rawConnections);

  async function refreshWorkspace() {
    const workspace = await apiClient.getWorkspace();
    setRawNodes(workspace.nodes);
    setRawConnections(workspace.connections);
  }

  useEffect(() => {
    refreshWorkspace();
  }, []);

  return (
    <WorkspaceContext.Provider value={{ nodes, edges, rawNodes, rawConnections, refreshWorkspace }}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) throw new Error('useWorkspace must be used within WorkspaceProvider');
  return context;
}
```

**Then in your React Flow component**:
```tsx
import { useWorkspace } from '../contexts/WorkspaceContext';

export function NodeEditor() {
  const { nodes, edges } = useWorkspace();

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      fitView
    />
  );
}
```

### Step 5: Verify Handle IDs Match

**Critical**: The handle IDs in your edges must match the handle IDs rendered in Phase 3.2.

**From Phase 3.2**, your handles should be:
```tsx
// Input handles
<Handle id={`input-${input.index}`} />

// Output handles
<Handle id={`output-${output.index}`} />
```

**In Phase 3.3**, your edges should reference:
```typescript
sourceHandle: `output-${connection.source_output_index}`
targetHandle: `input-${connection.target_input_index}`
```

If these don't match, edges won't connect to handles.

---

## Testing

### Backend Test: Verify Connections Exist

Before testing the UI, ensure the backend has connections:

```bash
curl http://localhost:8000/api/v1/workspace
```

**Check the response**:
```json
{
  "nodes": [ /* ... */ ],
  "connections": [
    {
      "source_node_session_id": "123",
      "source_output_index": 0,
      "target_node_session_id": "456",
      "target_input_index": 0
      // ...
    }
  ]
}
```

If `connections` array is empty, create a test connection:
```bash
curl -X POST http://localhost:8000/api/v1/connections \
  -H "Content-Type: application/json" \
  -d '{
    "source_node_path": "/text1",
    "source_output_index": 0,
    "target_node_path": "/fileout1",
    "target_input_index": 0
  }'
```

### Visual Test

1. Start backend server (with connections in workspace)
2. Start frontend dev server
3. Open app in browser

**Expected results**:
- ✅ Connection lines appear between nodes
- ✅ Lines connect to the correct handles
- ✅ Lines go from output handle (right side) to input handle (left side)
- ✅ Multiple connections from same output are all visible
- ✅ Replacing a connection removes old line, shows new line

### Browser Console Test

Open DevTools console and check:

```javascript
// Log the edges
console.log('Edges:', edges);

// Should show something like:
// [
//   {
//     id: "123-0-456-0",
//     source: "123",
//     target: "456",
//     sourceHandle: "output-0",
//     targetHandle: "input-0"
//   }
// ]
```

### React Flow DevTools

React Flow adds useful classes to edges:

**Inspect an edge line in browser**:
```html
<g class="react-flow__edge">
  <path class="react-flow__edge-path" d="M ..." />
</g>
```

**Check edge is connected to handles**:
- Edge path should start at source handle
- Edge path should end at target handle
- No floating or disconnected edges

### Edge Cases to Test

**No connections**:
- Empty workspace: No edges shown ✅
- New node: No edges to/from it ✅

**Multiple connections**:
- Node with multiple inputs, all connected: All edges visible ✅
- Node with multiple outputs, all connected: All edges visible ✅

**Invalid connections** (shouldn't happen, but test gracefully):
- Connection references deleted node: Edge not shown (source/target missing) ✅
- Connection with invalid handle ID: Edge shown but not attached ✅

---

## Troubleshooting

**Edges not appearing at all**
- Check browser console for errors
- Verify `edges` state is populated: `console.log(edges)`
- Verify `connections` from backend is not empty
- Check React Flow is imported correctly
- Ensure `edges={edges}` prop is on `<ReactFlow>`

**Edges visible but not attached to handles**
- **Most common issue**: Handle ID mismatch
- Check Phase 3.2 handle IDs: Should be `input-${index}` and `output-${index}`
- Check edge mapping: `sourceHandle: "output-0"` format
- Verify indices match (0 vs "0" - both should work but be consistent)

**Edges go to wrong handles**
- Verify `source_output_index` and `target_input_index` are correct in backend data
- Check the mapping function isn't swapping indices
- Ensure handle positions match indices (first handle is index 0)

**Edges appear as straight lines (not curved)**
- This is default React Flow behavior
- To add curves, use edge `type`:
  ```typescript
  {
    ...connectionToEdge(conn),
    type: 'smoothstep', // or 'default', 'step', 'straight'
  }
  ```

**TypeScript errors about Edge type**
- Ensure you import `Edge` from 'reactflow': `import type { Edge } from 'reactflow';`
- Check your `edges` state is typed as `Edge[]`

**Console error: "Edge source/target not found"**
- Edge references a node that doesn't exist
- Usually happens if node was deleted but connection wasn't
- Backend should prevent this, but check node IDs match

**Edges render but workspace looks wrong**
- Try clicking "Fit View" button or call `fitView()` on React Flow instance
- Edges are there but viewport is zoomed or panned wrong

---

## Validation Checklist

- [ ] Created `connectionToEdge()` helper function
- [ ] Created `connectionsToEdges()` helper function
- [ ] Integrated edge mapping into workspace loading
- [ ] React Flow receives `edges` prop
- [ ] Edges appear as lines between nodes
- [ ] Edges connect to correct handles
- [ ] Handle IDs match between Phase 3.2 and Phase 3.3
- [ ] Multiple connections from same output all visible
- [ ] Edge IDs are unique
- [ ] No console errors related to edges

---

## Deliverable

At the end of Phase 3.3:
- ✅ Backend connections are converted to React Flow edges
- ✅ Connection lines visible between nodes
- ✅ Edges connect to the correct input/output handles
- ✅ Edge mapping function is reusable
- ✅ Workspace loading includes edge conversion
- ✅ Multiple connections render correctly

**What's NOT included**:
- No interactivity (can't create/delete connections) - that's Phase 3.4
- No edge styling or customization
- No edge labels or tooltips

---

## Next Phase

**Phase 3.4** will add interactivity: creating connections by dragging between handles, and deleting connections by selecting and pressing Delete.

---

## Optional Enhancements (Not Required)

### Edge Styling
```typescript
export function connectionToEdge(connection: ConnectionResponse): Edge {
  return {
    id: `${connection.source_node_session_id}-${connection.source_output_index}-${connection.target_node_session_id}-${connection.target_input_index}`,
    source: connection.source_node_session_id,
    target: connection.target_node_session_id,
    sourceHandle: `output-${connection.source_output_index}`,
    targetHandle: `input-${connection.target_input_index}`,
    type: 'smoothstep',         // Curved edges
    animated: false,             // Set true for animation
    style: { strokeWidth: 2 },   // Custom thickness
  };
}
```

### Edge Labels
Show socket names on edges:
```typescript
{
  ...connectionToEdge(conn),
  label: `${conn.source_output_name} → ${conn.target_input_name}`,
}
```

### Color-coded Edges
```typescript
const getEdgeColor = (connection: ConnectionResponse) => {
  // Color by data type, connection state, etc.
  return '#999';
};

{
  ...connectionToEdge(conn),
  style: { stroke: getEdgeColor(connection) },
}
```

### Edge Click Handler
```tsx
<ReactFlow
  edges={edges}
  onEdgeClick={(event, edge) => {
    console.log('Edge clicked:', edge);
    // Show connection details, etc.
  }}
/>
```
