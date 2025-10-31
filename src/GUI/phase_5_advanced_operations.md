# Phase 5: Advanced Operations & Workspace Management

## Objective
Implement undo/redo, save/load flowstate, node reparenting, and workspace clearing.

## Undo/Redo System

### Undo Stack Integration
Create undo/redo UI controls:
- Keyboard shortcuts (Ctrl+Z for undo, Ctrl+Y for redo)
- Undo/Redo buttons in top toolbar
- Display operation name being undone/redone
- Disable buttons when stacks are empty
- Show undo/redo history depth indicator

### Backend Undo API
Query backend undo state:
- Create GET endpoint to check if undo/redo available
- Create POST /undo endpoint calling UndoManager.undo()
- Create POST /redo endpoint calling UndoManager.redo()
- Return operation name in response
- Refresh entire workspace after undo/redo operation

### State Restoration
Handle complete workspace reload:
- After undo/redo, backend restores previous state
- Frontend must fetch full workspace (GET /workspace)
- Replace all nodes, connections, and globals
- Reset React Flow viewport to previous view
- Clear any temporary UI state

### Operation Tracking
Show what can be undone:
- Display last operation name in UI
- Tooltip showing undo stack depth
- Optional: full undo history modal
- Clear visual feedback when undo succeeds

## Save/Load Flowstate

### Save Workflow
Implement workspace serialization:
- Create POST /flowstate/save endpoint calling save_flowstate()
- File dialog or predefined save location
- Backend serializes all nodes, connections, globals
- Include timestamp and version metadata
- Show success notification with file path

### Quick Save vs Save As
Provide save options:
- Ctrl+S for quick save (overwrite current file)
- Ctrl+D or Ctrl+Shift+S for "Save As" dialog
- Track current filename in application state
- Prompt for filename if none exists
- Update window title with current filename

### Load Workflow
Implement workspace restoration:
- Create POST /flowstate/load endpoint calling load_flowstate()
- File picker dialog for selecting .json file
- Backend clears existing workspace
- Backend deserializes nodes in correct order
- Backend restores connections and globals
- Frontend refetches entire workspace after load

### File Format Display
Show save file information:
- Display software version from file
- Show save timestamp
- List node count before loading
- Warn if loading will clear current workspace

## Node Reparenting (Move Path)

### Parent Selection Interface
Create path movement UI:
- Right-click context menu with "Move to..."
- Modal dialog showing node tree hierarchy
- Select new parent from tree view
- Input field for custom parent path

### Move Operation
Implement PUT /nodes/{session_id}/move endpoint:
- Backend calls NodeEnvironment.update_node_path()
- Moves node to new parent path
- Automatically renames if name conflict exists
- Updates all child nodes recursively
- Returns new path and name_changed flag

### Visual Tree Representation
Show node hierarchy:
- Indent child nodes under parents
- Collapsible tree view of workspace
- Drag-and-drop reparenting if feasible
- Update node path display after move

### Conflict Handling
Manage naming collisions:
- Show warning if new parent has child with same name
- Display auto-generated new name
- Allow user to provide alternative name
- Update all references to moved node

## Workspace Clearing

### Clear All Nodes
Implement workspace reset:
- Create POST /workspace/clear endpoint calling NodeEnvironment.flush_all_nodes()
- Ctrl+W keyboard shortcut
- "Clear Workspace" menu option
- Strong confirmation dialog (requires typing "clear" or checking boxes)

### Selective Clearing
Provide partial clear options:
- Clear only selected nodes
- Clear disconnected nodes
- Clear all connections only
- Clear all globals only

### Safety Measures
Prevent accidental data loss:
- Multi-step confirmation for destructive actions
- Offer to save before clearing
- Disable clear if unsaved changes exist
- Show count of nodes/connections to be deleted

## Session Management

### Auto-save Feature
Implement periodic saves:
- Optional auto-save to temporary location
- Configurable interval (every N minutes)
- Save to .autosave file separate from main file
- Offer recovery on application restart

### Workspace Metadata
Track workspace information:
- Creation timestamp
- Last modified timestamp
- Total node count
- Total connection count
- Dirty flag for unsaved changes

## Performance Optimization

### Large Workspace Handling
Optimize for many nodes:
- Lazy load node details (only fetch selected)
- Virtualize large node lists
- Debounce viewport changes
- Batch API calls where possible

### Canvas Optimization
Improve React Flow performance:
- Use node extent limits for bounded canvas
- Implement viewport clipping
- Reduce re-renders with memo and callbacks
- Optimize edge rendering for many connections

## Backend Mapping

This phase implements:
- UndoManager.undo() - via POST /undo
- UndoManager.redo() - via POST /redo
- save_flowstate() - via POST /flowstate/save
- load_flowstate() - via POST /flowstate/load
- NodeEnvironment.update_node_path() - via PUT /nodes/{session_id}/move
- NodeEnvironment.flush_all_nodes() - via POST /workspace/clear

## Deliverables

At the end of Phase 5:
- Full undo/redo capability with keyboard shortcuts
- Save workspace to JSON file
- Load workspace from JSON file
- Quick save and save-as functionality
- Nodes can be moved between parents
- Entire workspace can be cleared with confirmation
- All operations handle errors gracefully
- Complete feature parity with TUI backend functions
- Production-ready application with all core features
