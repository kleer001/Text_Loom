# Phase 2: Node Creation, Deletion & Basic Operations

## Objective
Enable full CRUD operations for nodes and implement node selection/interaction.

## Node Creation System

### Node Type Discovery
Implement available node types fetching:
- Query backend for available node types (deduce from existing nodes or create discovery endpoint)
- Build catalog of creatable node types
- Group types by category if applicable

### Creation Interface
Add node creation UI:
- Floating button or menu bar with "Add Node" option
- Dropdown/menu showing available node types
- Click-to-create workflow (select type, then click canvas position)
- Alternative: draggable palette with node type icons

### Create Operation
Implement POST /nodes endpoint integration:
- Collect node type and position from user interaction
- Generate unique name or let backend auto-generate
- Send POST request with NodeCreateRequest payload
- Update workspace context with returned NodeResponse
- Add new node to React Flow canvas immediately

## Node Deletion

### Selection State
Enhance selection system:
- Single-select mode (click node to select)
- Multi-select support (ctrl/cmd+click for multiple)
- Selection visual feedback (highlight, border change)
- Track selected node paths in context

### Delete Interface
Add deletion controls:
- Delete key handler when node(s) selected
- Delete button in node detail panel
- Context menu with delete option (right-click)
- Confirmation dialog for multi-delete or connected nodes

### Delete Operation
Implement DELETE /nodes/{session_id}:
- Map node path to session_id from workspace state
- Send DELETE request to backend
- Remove node from workspace context
- Remove associated connections
- Update React Flow canvas

## Node Renaming

### Rename UI
Create rename interaction:
- Double-click node name to edit inline
- Edit field in detail panel
- Keyboard shortcut (F2) when selected
- Validation for empty names

### Rename Operation
Implement rename via PUT /nodes/{session_id}:
- Send updated name in request body
- Handle name conflict errors from backend
- Update workspace context with new name/path
- Update React Flow node label
- Refresh connections if path changed

## Node Movement

### Visual Repositioning
Enable drag-to-reposition:
- Use React Flow's onNodeDragStop event
- Capture new position coordinates
- Debounce to avoid excessive API calls

### Position Update
Implement PUT /nodes/{session_id} for position:
- Send position array [x, y] in request body
- Update backend state
- Keep frontend in sync without full refresh

## Selection Context Enhancement

### Multi-Node Selection
Expand selection capabilities:
- Marquee selection (drag rectangle to select multiple)
- Select all (ctrl/cmd+A)
- Deselect all (click canvas background)
- Selection count display

### Selection Actions
Provide bulk operations UI:
- Show "X nodes selected" indicator
- Disable detail panel for multi-select
- Enable only applicable bulk actions (delete, move)

## Backend Mapping

This phase implements:
- Node.create_node() - via POST /nodes
- Node.destroy() - via DELETE /nodes/{session_id}
- Node.rename() - via PUT /nodes/{session_id}
- Position updates - via PUT /nodes/{session_id}

## Deliverables

At the end of Phase 2:
- Users can create nodes from type menu
- Nodes can be dragged to reposition
- Nodes can be selected (single and multi)
- Nodes can be deleted with confirmation
- Nodes can be renamed inline
- All changes persist to backend
- Canvas remains responsive and updates immediately
