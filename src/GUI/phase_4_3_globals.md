# Phase 4.3: Global Variables Management

## Objective
Implement complete global variables management interface with CRUD operations and validation.

## Global Variables Panel

### Panel Interface
Create dedicated globals interface:
- Separate tab or modal for globals management
- Table showing all key-value pairs
- Add/Edit/Delete operations
- Search/filter capabilities
- Keyboard shortcuts (N for new, Cut for delete)

### Panel Location Options
Consider placement:
- Side panel alongside parameters
- Dedicated tab in main interface
- Modal dialog accessed from toolbar
- Floating window for advanced users

## Globals List Display

### GET /globals Visualization
Implement globals listing:
- Fetch all globals from backend
- Display as editable table or list
- Show key name and current value
- Indicate system vs user variables if distinguishable
- Sort alphabetically or by creation date
- Show usage count if available

### Table Columns
Display relevant information:
- **Key**: Variable name (uppercase)
- **Value**: Current value (editable inline)
- **Type**: Inferred type (string, number, etc.)
- **Actions**: Edit, Delete buttons

## Add/Edit Global

### PUT /globals/{key} Implementation
Implement global creation/editing:
1. Input field for key (uppercase, 2+ chars, no $ prefix)
2. Input field for value (any type)
3. Validate key format client-side before API call
4. Backend calls GlobalStore.set() with validation
5. Update globals list after successful add
6. Show success/error feedback

### Validation Rules
Enforce global variable naming:
- **Uppercase only**: Convert or reject lowercase
- **Minimum 2 characters**: Prevent single-char globals
- **No $ prefix**: $ is for references, not definitions
- **Valid identifier**: Alphanumeric and underscores only
- Display validation errors clearly

### Inline Editing
Quick value updates:
- Click value to edit inline
- Enter to save, Escape to cancel
- Immediate API call on save
- Visual feedback during update

## Delete Global

### DELETE /globals/{key} Implementation
Implement global deletion:
1. Confirmation dialog for delete action
2. Show warning if global is referenced by nodes
3. Send DELETE request to backend
4. Backend calls GlobalStore.cut()
5. Remove from globals list in UI
6. Show deletion confirmation

### Deletion Safety
Prevent accidental deletion:
- Require confirmation for delete
- Show impact analysis (which nodes use this global)
- Option to bulk delete unused globals
- Undo capability if possible

## Bulk Operations

### Mass Global Management
Add bulk operations:
- **Delete All Globals** button with strong confirmation
- **Delete Unused Globals** option
- **Export Globals** to file (JSON/text)
- **Import Globals** from file
- Calls GlobalStore.flush_all_globals() via API
- Clear globals display after operation

### Safety Confirmations
Multi-step confirmation for destructive operations:
- Type "DELETE ALL" to confirm flush
- Show count of globals to be deleted
- Final confirmation dialog
- Cannot be undone warning

## Global Variable Usage

### Usage Tracking
Show where globals are used:
- List nodes that reference each global
- Click to navigate to referencing node
- Highlight parameters using the global
- Warn when deleting used globals

### Reference Detection
Identify global usage:
- Scan parameter values for $VARNAME patterns
- Update references list on parameter changes
- Show reference count in globals table
- Mark unused globals for cleanup

## Backend Mapping

This phase implements:
- **GET /globals** - List all global variables
- **PUT /globals/{key}** - via GlobalStore.set()
- **DELETE /globals/{key}** - via GlobalStore.cut()
- **DELETE /globals (all)** - via GlobalStore.flush_all_globals()
- Global variable validation and naming rules

## Deliverables

At the end of Phase 4.3:
- Global variables can be created, edited, and deleted
- Globals display in organized table/list
- Validation prevents invalid global names
- Bulk operations available for mass management
- Usage tracking shows where globals are referenced
- All globals operations persist to backend
- Clear feedback on all operations
- Safety confirmations prevent accidental deletion
