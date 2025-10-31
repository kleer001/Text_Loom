# Phase 3: Connection Management & Data Flow

## Objective
Implement connection creation, deletion, and visual feedback for node networking.

## Connection Visual System

### Input/Output Handles
Design socket rendering on nodes:
- Display input sockets on left side of node
- Display output sockets on right side of node
- Use different colors for connected vs unconnected
- Show socket index for multi-socket nodes

### Handle Metadata
Fetch and display socket information:
- Parse input_names and output_names from NodeResponse
- Display data type on hover
- Show connection compatibility hints

## Connection Creation Workflow


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
- Shift-Click on additional edges to select more edges


### Delete Workflow
Implement DELETE /connections:
- Use connection ID from workspace state
- Send DELETE request to backend
- Remove connection from workspace context
- Update React Flow edges array


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

## Backend Mapping

This phase implements:
- Node.set_next_input() - via POST /connections
- Node.remove_input() - via DELETE /connections
- Connection auto-replacement behavior from backend

## Deliverables

At the end of Phase 3:
- Users can create connections by clicking between sockets
- Alternative drag-to-connect also works
- Invalid connections are prevented
- Connections can be selected and deleted
- Backend automatically handles connection replacement
- All connection operations persist immediately
