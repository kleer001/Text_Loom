# Phase 3: Connection Management & Data Flow

## Objective
Implement connection creation, deletion, and visual feedback for node networking.

## Connection Visual System

### Input/Output Handles
Design socket rendering on nodes:
- Display input sockets on left side of node
- Display output sockets on right side of node
- Label each handle with socket name from backend
- Use different colors for connected vs unconnected
- Show socket index for multi-socket nodes

### Handle Metadata
Fetch and display socket information:
- Parse input_names and output_names from NodeResponse
- Parse input_data_types and output_data_types
- Display data type on hover
- Show connection compatibility hints

## Connection Creation Workflow

### Two-Step Connection Mode
Implement "start output, end input" pattern:
- User clicks output socket on source node (highlights)
- Mouse cursor shows connection wire following pointer
- User clicks input socket on target node (completes)
- Invalid targets show visual rejection feedback

### Alternative Connection Method
Use React Flow's built-in connection:
- Drag from output handle to input handle
- React Flow handles visual wire rendering
- Use onConnect callback to finalize

### Connection API Call
Implement POST /connections:
- Extract source node path and output index
- Extract target node path and input index
- Send ConnectionRequest to backend
- Backend handles replacement of existing input connections
- Add returned ConnectionResponse to workspace state

## Connection Deletion

### Selection of Connections
Enable edge selection:
- Click edge to select (highlight with different color)
- Show delete button on selected edge
- Edge context menu with delete option

### Delete Workflow
Implement DELETE /connections:
- Use connection ID from workspace state
- Send DELETE request to backend
- Remove connection from workspace context
- Update React Flow edges array

### Bulk Disconnection
Add disconnect operations:
- "Remove all inputs" button on node detail panel
- "Remove all outputs" button on node detail panel
- Iterate through connections and delete individually

## Connection State Visualization

### Visual Feedback
Enhance edge rendering:
- Style edges based on source node state (cooked/uncooked)
- Animate edges when data flows (during cook)
- Use different edge types for different data types
- Thickness or dashing for connection strength/validity

### Connection Information Display
Show connection details on selection:
- Source node path and output name
- Target node path and input name
- Data type being transferred
- Last cook timestamp if available

## Handle Discovery from Backend

### Socket Inspection
Query socket information:
- Use input_names() dict from NodeResponse parameters
- Use output_names() dict from NodeResponse parameters
- Dynamically generate handles based on backend data
- Handle single vs multi input/output modes

### Connection Validation
Implement frontend validation before API call:
- Check if target input already connected (warn about replacement)
- Validate data type compatibility if exposed by backend
- Prevent self-connections
- Prevent duplicate connections

## React Flow Configuration

### Edge Types
Configure edge rendering options:
- Default straight edge for simple connections
- Bezier curves for long-distance connections
- Step edges for hierarchical layouts
- Animated edges during execution

### Connection Modes
Set React Flow connection behavior:
- Strict mode: only output to input allowed
- Validate connections before API call
- Show temporary edge during drag
- Cancel on invalid drop

## Backend Mapping

This phase implements:
- Node.set_next_input() - via POST /connections
- Node.remove_input() - via DELETE /connections
- Connection auto-replacement behavior from backend

## Deliverables

At the end of Phase 3:
- Users can create connections by clicking sockets
- Alternative drag-to-connect also works
- Connections display with source/target information
- Invalid connections are prevented or warned
- Connections can be selected and deleted
- Visual feedback shows connection state
- Backend automatically handles connection replacement
- All connection operations persist immediately
