# Phase 3.2: Visual Handles - Input/Output Sockets

## Objective
Add visual input/output handles (sockets) to nodes so users can see where connections can be made. This phase makes connection points visible but doesn't yet make them interactive.

## Prerequisites
- Phase 3.1 complete: Types and API methods exist
- React Flow installed and working
- Custom node components rendering in React Flow
- Nodes displaying with `NodeResponse` data

## Overview

In React Flow, connections are made between **Handles**. Handles are small circular attachment points rendered on nodes:
- **Input handles** (type="target"): Left side of node, receive data
- **Output handles** (type="source"): Right side of node, send data

Each node's `NodeResponse` contains:
- `inputs: InputInfo[]` - Array of input socket definitions
- `outputs: OutputInfo[]` - Array of output socket definitions

We need to render a Handle component for each input and output.

---

## React Flow Handle Basics

**Documentation**: [React Flow Custom Nodes](https://reactflow.dev/learn/customization/custom-nodes)

### Handle Component
```tsx
import { Handle, Position } from 'reactflow';

<Handle
  type="target"           // "target" for inputs, "source" for outputs
  position={Position.Left} // Left for inputs, Right for outputs
  id="input-0"            // Unique ID within this node
  style={{ top: '50%' }}  // CSS positioning
/>
```

**Key Props**:
- `type`: "target" (input) or "source" (output)
- `position`: `Position.Left`, `Position.Right`, `Position.Top`, `Position.Bottom`
- `id`: Unique identifier for this handle (used when creating connections)
- `style`: CSS to position the handle on the node

**Handle ID Convention**:
- Input handles: `input-{index}` (e.g., "input-0", "input-1")
- Output handles: `output-{index}` (e.g., "output-0", "output-1")

This convention must match the parsing in Phase 3.4 when creating connections.

---

## Implementation

### Step 1: Locate Your Custom Node Component

**Find the file** where you render React Flow nodes. This is likely:
- A component named something like `CustomNode`, `TextLoomNode`, `NodeComponent`
- Imported and used in your React Flow setup
- Registered in `nodeTypes` for React Flow

**How to find it**:
```bash
cd src/GUI
# Search for React Flow node type registration
grep -r "nodeTypes" src/
# Search for Handle imports (if already partially implemented)
grep -r "from 'reactflow'" src/ | grep Handle
# Search for custom node components
grep -r "function.*Node" src/components/
```

**Example file structure**:
```
src/GUI/src/
  components/
    NodeEditor.tsx          # Main React Flow component
    CustomNode.tsx          # Your custom node renderer ← YOU'LL EDIT THIS
  App.tsx
  types.ts
  apiClient.ts
```

### Step 2: Import Handle Components

**File**: Your custom node component file (e.g., `CustomNode.tsx`)

**Add imports**:
```tsx
import { Handle, Position } from 'reactflow';
import type { NodeResponse, InputInfo, OutputInfo } from '../types';
```

### Step 3: Access Node Data

Your custom node component receives data through props:

```tsx
interface CustomNodeProps {
  data: NodeResponse;  // Full node data from backend
  id: string;          // React Flow node ID (session_id)
  selected?: boolean;  // Whether node is selected
}

function CustomNode({ data, id, selected }: CustomNodeProps) {
  // data.inputs: InputInfo[]
  // data.outputs: OutputInfo[]
  // data.name, data.type, data.parameters, etc.
}
```

**Data structure reminder**:
```typescript
interface InputInfo {
  index: number | string;  // Socket index
  name: string;           // Display name
  data_type: string;      // Type annotation
  connected: boolean;     // Whether connected
}

interface OutputInfo {
  index: number | string;  // Socket index
  name: string;           // Display name
  data_type: string;      // Type annotation
  connection_count: number; // Number of connections
}
```

### Step 4: Render Input Handles

Add input handles to the left side of your node:

```tsx
function CustomNode({ data }: CustomNodeProps) {
  return (
    <div className="custom-node">
      {/* Input handles - LEFT SIDE */}
      {data.inputs.map((input, idx) => (
        <Handle
          key={`input-${input.index}`}
          type="target"
          position={Position.Left}
          id={`input-${input.index}`}
          style={{
            top: `${((idx + 1) / (data.inputs.length + 1)) * 100}%`,
            background: input.connected ? '#555' : '#999',
          }}
        />
      ))}

      {/* Your existing node content */}
      <div className="node-header">
        <span className="node-type">{data.type}</span>
        <span className="node-name">{data.name}</span>
      </div>

      {/* Node body, parameters, etc. */}

    </div>
  );
}
```

**Handle positioning calculation**:
```typescript
top: `${((idx + 1) / (data.inputs.length + 1)) * 100}%`
```
- For 1 input: 50% (middle)
- For 2 inputs: 33%, 66% (evenly spaced)
- For 3 inputs: 25%, 50%, 75%

**Optional styling**:
- `background`: Color of the handle (gray if not connected)
- `width`, `height`: Size of the handle circle
- `border`: Border styling

### Step 5: Render Output Handles

Add output handles to the right side:

```tsx
function CustomNode({ data }: CustomNodeProps) {
  return (
    <div className="custom-node">
      {/* Input handles */}
      {data.inputs.map((input, idx) => (
        <Handle
          key={`input-${input.index}`}
          type="target"
          position={Position.Left}
          id={`input-${input.index}`}
          style={{
            top: `${((idx + 1) / (data.inputs.length + 1)) * 100}%`,
          }}
        />
      ))}

      {/* Node content */}
      <div className="node-content">
        {/* ... */}
      </div>

      {/* Output handles - RIGHT SIDE */}
      {data.outputs.map((output, idx) => (
        <Handle
          key={`output-${output.index}`}
          type="source"
          position={Position.Right}
          id={`output-${output.index}`}
          style={{
            top: `${((idx + 1) / (data.outputs.length + 1)) * 100}%`,
            background: output.connection_count > 0 ? '#555' : '#999',
          }}
        />
      ))}
    </div>
  );
}
```

**Key differences from input handles**:
- `type="source"` (instead of "target")
- `position={Position.Right}` (instead of Left)
- `id={`output-${output.index}`}` (instead of "input-")
- Check `output.connection_count > 0` (instead of `input.connected`)

### Step 6: Handle Edge Cases

Some nodes may have no inputs or no outputs:

```tsx
{/* Only render input handles if node has inputs */}
{data.inputs && data.inputs.length > 0 && data.inputs.map((input, idx) => (
  <Handle /* ... */ />
))}

{/* Only render output handles if node has outputs */}
{data.outputs && data.outputs.length > 0 && data.outputs.map((output, idx) => (
  <Handle /* ... */ />
))}
```

**Common node configurations**:
- **Source node** (e.g., `text`): No inputs, has outputs
- **Processing node** (e.g., `query`): Has inputs and outputs
- **Sink node** (e.g., `fileout`): Has inputs, no outputs

### Step 7: Optional - Add Tooltips

Show socket information on hover:

```tsx
<Handle
  key={`input-${input.index}`}
  type="target"
  position={Position.Left}
  id={`input-${input.index}`}
  title={`${input.name} (${input.data_type})`}
  style={{ /* ... */ }}
/>
```

The `title` attribute shows a native browser tooltip on hover.

---

## Complete Example

Here's a full custom node component with handles:

```tsx
import React from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeResponse } from '../types';

interface CustomNodeProps {
  data: NodeResponse;
  selected?: boolean;
}

export function CustomNode({ data, selected }: CustomNodeProps) {
  return (
    <div
      className={`custom-node ${selected ? 'selected' : ''}`}
      style={{
        border: selected ? '2px solid blue' : '1px solid #ddd',
        borderRadius: '8px',
        padding: '10px',
        background: 'white',
        minWidth: '150px',
      }}
    >
      {/* Input Handles */}
      {data.inputs && data.inputs.map((input, idx) => (
        <Handle
          key={`input-${input.index}`}
          type="target"
          position={Position.Left}
          id={`input-${input.index}`}
          title={`${input.name} (${input.data_type})`}
          style={{
            top: `${((idx + 1) / (data.inputs.length + 1)) * 100}%`,
            background: input.connected ? '#4CAF50' : '#999',
            width: '10px',
            height: '10px',
          }}
        />
      ))}

      {/* Node Header */}
      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
        {data.glyph && <span style={{ marginRight: '5px' }}>{data.glyph}</span>}
        {data.name}
      </div>

      {/* Node Type */}
      <div style={{ fontSize: '0.8em', color: '#666' }}>
        {data.type}
      </div>

      {/* Errors/Warnings */}
      {data.errors.length > 0 && (
        <div style={{ color: 'red', fontSize: '0.8em' }}>
          ⚠ {data.errors.length} error(s)
        </div>
      )}

      {/* Output Handles */}
      {data.outputs && data.outputs.map((output, idx) => (
        <Handle
          key={`output-${output.index}`}
          type="source"
          position={Position.Right}
          id={`output-${output.index}`}
          title={`${output.name} (${output.data_type})`}
          style={{
            top: `${((idx + 1) / (data.outputs.length + 1)) * 100}%`,
            background: output.connection_count > 0 ? '#4CAF50' : '#999',
            width: '10px',
            height: '10px',
          }}
        />
      ))}
    </div>
  );
}
```

---

## Styling Handles

### Default React Flow Styles
React Flow provides default handle styles. You can override them with CSS:

```css
/* In your CSS file */
.react-flow__handle {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid white;
}

.react-flow__handle-left {
  left: -5px;  /* Extend out from node border */
}

.react-flow__handle-right {
  right: -5px;
}

/* Style based on connection state */
.react-flow__handle.connected {
  background: #4CAF50;
}

.react-flow__handle.not-connected {
  background: #999;
}
```

### Inline Styles (Simpler)
Use the `style` prop on Handle for quick customization:

```tsx
<Handle
  style={{
    width: '12px',
    height: '12px',
    background: '#4CAF50',
    border: '2px solid white',
  }}
/>
```

---

## Testing

### Visual Test
1. Start the frontend dev server
2. Open the app in browser
3. Create or view a node

**Expected results**:
- ✅ Input handles appear on left side of node
- ✅ Output handles appear on right side of node
- ✅ Handles are evenly spaced vertically
- ✅ Number of handles matches node's input/output count
- ✅ Nodes with no inputs don't show input handles
- ✅ Nodes with no outputs don't show output handles

### Different Node Types
Test with various node types:

**Text node** (source):
- No input handles
- 1 output handle on right

**FileOut node** (sink):
- 1+ input handles on left
- No output handles

**Query node** (processor):
- Input handles on left
- Output handles on right

### Hover Test
Hover over handles to verify:
- ✅ Cursor changes (React Flow default is crosshair)
- ✅ Tooltip shows (if you added `title` attribute)

### Multi-Socket Nodes
If any nodes have multiple inputs or outputs:
- ✅ All handles are visible
- ✅ Handles don't overlap
- ✅ Handles are evenly distributed

---

## Troubleshooting

**Handles not visible**
- Check React Flow is rendering (`<ReactFlow>` component)
- Verify `Handle` is imported from 'reactflow'
- Inspect element in browser - handles should be rendered as `<div class="react-flow__handle">`
- Check if handles are positioned off-screen (adjust `style.top`)

**Handles in wrong position**
- Verify `position` is `Position.Left` for inputs, `Position.Right` for outputs
- Check the parent node has `position: relative` in CSS
- Adjust `top` percentage calculation

**Can't connect handles (too early)**
- This is expected! Phase 3.2 only adds visual handles
- Interactivity comes in Phase 3.4
- Handles should still show hover cursor change

**Handle ID errors in console**
- Make sure each handle ID is unique within the node
- Use template: `input-${input.index}` or `output-${output.index}`
- Don't use the same ID for multiple handles

**TypeScript errors on Handle component**
- Verify you imported from 'reactflow' (not '@reactflow/core')
- Check React Flow version is compatible (v11+)
- Ensure `@types/react` is installed

**Handles overlap when node has many inputs/outputs**
- Increase node height based on socket count
- Adjust spacing calculation
- Consider using absolute pixel spacing instead of percentages

---

## Validation Checklist

- [ ] `Handle` component imported from 'reactflow'
- [ ] Input handles render on left side (type="target", position=Left)
- [ ] Output handles render on right side (type="source", position=Right)
- [ ] Handle IDs follow convention: `input-{index}`, `output-{index}`
- [ ] Handles positioned correctly (evenly spaced)
- [ ] Edge cases handled (nodes with 0 inputs or 0 outputs)
- [ ] Tooltips show socket name and type (optional)
- [ ] Different node types render correct number of handles
- [ ] No console errors related to React Flow handles

---

## Deliverable

At the end of Phase 3.2:
- ✅ All nodes display input handles on the left
- ✅ All nodes display output handles on the right
- ✅ Handle count matches `NodeResponse.inputs.length` and `outputs.length`
- ✅ Handles have unique IDs following the convention
- ✅ Handles are visually distinct and positioned correctly
- ✅ No functionality yet (can't create connections) - that's Phase 3.4

**What's NOT included**:
- No connection creation (Phase 3.4)
- No connection lines visible yet (Phase 3.3)
- No handle validation or constraints

---

## Next Phase

**Phase 3.3** will map existing connections from the backend to React Flow edges, making connection lines visible between nodes.

---

## Optional Enhancements (Not Required)

### Color-coded by data type
```tsx
const getHandleColor = (dataType: string) => {
  if (dataType.includes('str')) return '#3498db';
  if (dataType.includes('int') || dataType.includes('float')) return '#e74c3c';
  return '#999';
};

<Handle
  style={{ background: getHandleColor(input.data_type) }}
/>
```

### Show socket labels
```tsx
<div style={{ position: 'relative' }}>
  <Handle id={`input-${input.index}`} />
  <span style={{ fontSize: '0.7em', marginLeft: '15px' }}>
    {input.name}
  </span>
</div>
```

### Animated connected handles
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.react-flow__handle.connected {
  animation: pulse 2s infinite;
}
```
