# Phase 4.2: Node Execution and Output Display

## Objective
Implement node execution controls, output display, error handling, and state synchronization.

## Execution Interface

### Execution Controls
Create execution controls:
- "Cook" button in parameter panel for selected node
- Keyboard shortcut (Shift+C) matching TUI
- Visual cooking indicator (spinner, progress)
- Display cook count after execution
- Show node state (unchanged/uncooked/cooking)

### Execute API Call
Implement POST /nodes/{session_id}/execute:
1. Trigger on user action (button or keyboard)
2. Backend calls Node.cook() which:
   - Gathers dependencies via cook_dependencies()
   - Cooks upstream nodes if needed
   - Executes _internal_cook() on this node
3. Receive ExecutionResponse with output and timing
4. Update node state to reflect cooked status

## Output Display

### Output Panel
Show execution results:
- Create output panel or expandable section
- Display List[str] output as formatted list
- Show execution time from response
- Display line numbers or indices
- Format long strings with wrapping or scrolling
- Clear/update output on re-execution

### Output Formatting
Make output readable:
- Monospace font for text output
- Syntax highlighting if applicable
- Line numbers for multi-line output
- Scrollable container for long outputs
- Copy-to-clipboard functionality

## Error and Warning Display

### Error Handling
Handle execution problems:
- Show errors array in red alert boxes
- Display error messages from backend clearly
- Link errors to specific parameters if possible
- Provide actionable error messages
- Don't clear errors until successful cook

### Warning Display
Show non-critical issues:
- Show warnings array in yellow/orange alerts
- Distinguish warnings from errors visually
- Allow dismissing warnings
- Log warnings for debugging

## State Synchronization

### Automatic State Updates
Keep UI in sync with backend:
- Poll workspace state after execution
- Update node states (unchanged/uncooked/cooking)
- Refresh outputs after cook completes
- Update all changed nodes, not just executed one
- Handle multi-node dependency cooking

### State Indicators
Visual feedback for node states:
- **Unchanged**: Node up-to-date, outputs valid
- **Uncooked**: Dependencies changed, needs recook
- **Cooking**: Currently executing
- Show cook count to indicate freshness

## Backend Mapping

This phase implements:
- **Node.cook()** - via POST /nodes/{session_id}/execute
- **Node.get_output()** - displayed in execution response
- **Node.cook_dependencies()** - automatic upstream cooking
- Node state tracking and updates

## Deliverables

At the end of Phase 4.2:
- Nodes can be executed individually via button or keyboard
- Execution output displays clearly and is formatted well
- Errors and warnings show in context with clear messaging
- Node states update automatically after execution
- UI remains responsive during operations
- Cooking progress is visible to user
- Output can be inspected and copied
