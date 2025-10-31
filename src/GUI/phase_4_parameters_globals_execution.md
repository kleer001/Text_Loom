# Phase 4: Parameters, Globals, and Node Execution

## Objective
Implement parameter editing, global variable management, node execution, and output display.

## Parameter Editing System

### Parameter Panel Redesign
Create comprehensive parameter interface:
- Show all parameters for selected node
- Display parameter name, type, and current value
- Show default value as placeholder text
- Indicate read-only parameters (greyed out)
- Group parameters logically if metadata available

### Type-Specific Input Widgets
Map parameter types to appropriate MUI components:
- STRING: TextField with text input
- INT: TextField with number input and integer validation
- FLOAT: TextField with number input and decimal support
- TOGGLE: Switch or Checkbox component
- BUTTON: Button component that triggers parameter action
- STRINGLIST: Multi-line TextField with array handling
- MENU: Select dropdown if options provided

### Parameter Update Flow
Implement PUT /nodes/{session_id} for parameters:
- Capture value changes from input widgets
- Debounce text inputs to avoid excessive API calls
- Send updated parameter in request body parameters dict
- Backend calls Parm.set() which validates and converts type
- Update workspace context with response
- Reflect changes in UI immediately

### Parameter Validation
Add frontend validation before API call:
- Type checking (int vs float vs string)
- Range validation if min/max provided
- Required field checking
- Format validation for special types

## Node Execution

### Execution Interface
Create execution controls:
- "Cook" button in parameter panel for selected node
- Keyboard shortcut (Shift+C) matching TUI
- Visual cooking indicator (spinner, progress)
- Display cook count after execution

### Execute API Call
Implement POST /nodes/{session_id}/execute:
- Trigger on user action
- Backend calls Node.cook() which:
  - Gathers dependencies via cook_dependencies()
  - Cooks upstream nodes if needed
  - Executes _internal_cook() on this node
- Receive ExecutionResponse with output and timing
- Update node state to reflect cooked status

### Output Display
Show execution results:
- Create output panel or expandable section
- Display List[str] output as formatted list
- Show execution time from response
- Display line numbers or indices
- Format long strings with wrapping or scrolling

### Error and Warning Display
Handle execution problems:
- Show errors array in red alert boxes
- Show warnings array in yellow/orange alerts
- Link errors to specific parameters if possible
- Provide clear error messages from backend

## Global Variables Management

### Global Variables Panel
Create dedicated globals interface:
- Separate tab or modal for globals management
- Table showing all key-value pairs
- Add/Edit/Delete operations
- Keyboard shortcuts (N for new, Cut for delete)

### Globals List Display
Implement GET /globals visualization:
- Fetch all globals from backend
- Display as editable table or list
- Show key name and current value
- Indicate system vs user variables if distinguishable

### Add/Edit Global
Implement PUT /globals/{key}:
- Input field for key (uppercase, 2+ chars, no $ prefix)
- Input field for value (any type)
- Validate key format client-side before API call
- Backend calls GlobalStore.set() with validation
- Update globals list after successful add

### Delete Global
Implement DELETE /globals/{key}:
- Confirmation dialog for delete action
- Send DELETE request to backend
- Backend calls GlobalStore.cut()
- Remove from globals list in UI

### Bulk Operations
Add mass global management:
- "Delete All Globals" button with strong confirmation
- Calls GlobalStore.flush_all_globals() via API
- Clear globals display after operation

## Parameter Expression Support

### Global Variable References
Enable $VAR substitution in parameters:
- Detect $VAR patterns in string parameters
- Show resolved value on hover or in tooltip
- Backend handles evaluation during cook
- Display both raw and evaluated values

### Expression Validation
Check expressions before sending:
- Validate global variable exists if referenced
- Warn about undefined variables
- Preview evaluated result if possible

## State Synchronization

### Automatic State Updates
Keep UI in sync with backend:
- Poll workspace state after execution
- Update node states (unchanged/uncooked/cooking)
- Refresh outputs after cook completes
- Update all changed nodes, not just executed one

### Optimistic Updates
Improve responsiveness:
- Update UI immediately on parameter change
- Show loading state during API call
- Revert on error with notification
- Batch rapid changes to avoid API spam

## Backend Mapping

This phase implements:
- Parm.set() - via PUT /nodes/{session_id} parameters
- Node.cook() - via POST /nodes/{session_id}/execute
- Node.get_output() - displayed in execution response
- GlobalStore.set() - via PUT /globals/{key}
- GlobalStore.cut() - via DELETE /globals/{key}
- GlobalStore.flush_all_globals() - via API endpoint

## Deliverables

At the end of Phase 4:
- All parameter types can be edited with appropriate widgets
- Parameter changes save to backend immediately
- Nodes can be executed individually
- Execution output displays clearly
- Errors and warnings show in context
- Global variables can be created, edited, and deleted
- All globals operations persist to backend
- UI remains responsive during operations
