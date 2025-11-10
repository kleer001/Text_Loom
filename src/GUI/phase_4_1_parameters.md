# Phase 4.1: Parameter Editing System

## Objective
Implement comprehensive parameter editing interface with type-specific widgets, validation, and expression support.

## Parameter Panel Redesign

### Panel Layout
Create comprehensive parameter interface:
- Show all parameters for selected node
- Display parameter name, type, and current value
- Show default value as placeholder text
- Indicate read-only parameters (greyed out)
- Group parameters logically if metadata available

### Type-Specific Input Widgets
Map parameter types to appropriate MUI components:
- **STRING**: TextField with text input
- **INT**: TextField with number input and integer validation
- **FLOAT**: TextField with number input and decimal support
- **TOGGLE**: Switch or Checkbox component
- **BUTTON**: Button component that triggers parameter action
- **STRINGLIST**: Multi-line TextField with array handling
- **MENU**: Select dropdown if options provided

## Parameter Update Flow

### API Integration
Implement PUT /nodes/{session_id} for parameters:
1. Capture value changes from input widgets
2. Debounce text inputs to avoid excessive API calls
3. Send updated parameter in request body parameters dict
4. Backend calls Parm.set() which validates and converts type
5. Update workspace context with response
6. Reflect changes in UI immediately

### Optimistic Updates
Improve responsiveness:
- Update UI immediately on parameter change
- Show loading state during API call
- Revert on error with notification
- Batch rapid changes to avoid API spam

## Parameter Validation

### Frontend Validation
Add validation before API call:
- Type checking (int vs float vs string)
- Range validation if min/max provided
- Required field checking
- Format validation for special types
- Display validation errors inline

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
- Highlight undefined variable references

## Backend Mapping

This phase implements:
- **Parm.set()** - via PUT /nodes/{session_id} parameters
- Parameter type validation and conversion
- Expression evaluation preparation

## Deliverables

At the end of Phase 4.1:
- All parameter types have appropriate input widgets
- Parameter changes save to backend immediately
- Type validation prevents invalid inputs
- Global variable expressions are recognized
- UI provides clear feedback on parameter state
- Read-only parameters are clearly indicated
