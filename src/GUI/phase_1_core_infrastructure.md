# Phase 1: Core Infrastructure & Workspace Viewing

## Objective
Establish the foundational application structure and implement read-only workspace visualization.

## Components to Build

### Application Shell
Create the main React application with:
- Single-page layout using MUI's Box/Container components
- Top navigation bar with application title
- Main content area for graph visualization
- Right sidebar for information display

### API Client Layer
Implement fetch-based communication module:
- Base URL configuration (localhost:8000/api/v1)
- Generic fetch wrapper with error handling
- Response parsing and error transformation
- Connection state management

### React Context Setup
Establish state management architecture:
- WorkspaceContext for global application state
- Stores nodes array, connections array, and globals object
- Provides actions for state updates
- Handles loading and error states

### Initial Data Loading
Implement workspace fetching:
- Call GET /workspace on application mount
- Parse NodeResponse objects into display format
- Parse ConnectionResponse objects into edge format
- Store initial state in context

## React Flow Integration

### Graph Canvas Setup
Configure React Flow for node visualization:
- Install and import @xyflow/react
- Set up ReactFlow component with basic configuration
- Enable background grid pattern
- Add zoom and pan controls
- Configure viewport to fit all nodes initially

### Node Display
Transform backend node data for React Flow:
- Convert NodeResponse.position to React Flow coordinates
- Map NodeResponse to React Flow node format
- Create basic node rendering component showing name and type
- Display node path as subtitle
- Show state indicator (unchanged/uncooked/cooking)

### Connection Display
Visualize node connections:
- Convert ConnectionResponse to React Flow edge format
- Map source/target using node paths
- Use source_output_index and target_input_index for handle IDs
- Style edges based on connection state
- Add directional arrows to show data flow

## Status Display

### Selected Node Panel
Create right sidebar showing selected node details:
- Display node name, path, and type
- List all parameters with current values
- Show input/output socket names
- Display errors and warnings arrays
- Show node state and cook count

### Error Handling
Implement user-facing error messages:
- Connection failure notifications
- API error display with retry option
- Invalid state warnings
- Loading indicators during fetch operations

## Backend Mapping

This phase establishes the foundation for:
- Node.get_output() - via workspace state viewing
- NodeEnvironment.list_nodes() - implicit in workspace fetch
- All read-only operations that don't modify state

## Deliverables

At the end of Phase 1:
- Application loads and displays existing workspace
- Nodes render in correct positions
- Connections draw between nodes
- Clicking a node shows its details
- No editing capabilities yet (read-only view)
- Refresh button to reload workspace from backend
