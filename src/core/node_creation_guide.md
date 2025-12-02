# Node Creation Guide

## 1. Overview/Purpose

Text_Loom's node-based architecture enables modular text processing through a graph of interconnected processing units. Each node performs specific operations on text data while maintaining connections to other nodes, creating flexible processing pipelines.

This guide covers the structural requirements and conventions for creating new node types. You'll learn the mandatory interfaces, parameter systems, state management, and integration patterns that every node must implement.

New nodes are automatically discovered at runtime through filename conventions, so focus on implementing the correct structure rather than manual registration. The system expects nodes to handle List[str] data types, manage their own state, and participate in the cooking/evaluation cycle.

This is a technical reference for experienced developers who understand object-oriented patterns and need to extend the Text_Loom processing capabilities.

## 2. Quick Reference

### Essential Requirements Checklist

**File Structure:**
```python
# Filename: src/core/your_node_name_node.py
class YourNodeNameNode(Node):
    GLYPH = '⚡'                  # Visual identifier (single character/emoji)
    GROUP = FunctionalGroup.XXX  # Functional grouping (TEXT/FILE/LIST/FLOW)
    SINGLE_INPUT = True/False    # Connection limits
    SINGLE_OUTPUT = True/False
```

**Mandatory Implementations:**
```python
def __init__(name, path, node_type)          # Constructor with parameters
def _internal_cook(force=False)              # Core processing logic
def input_names() -> Dict[str, str]          # Input connection labels
def output_names() -> Dict[str, str]         # Output connection labels  
def input_data_types() -> Dict[str, str]     # Expected input types
def output_data_types() -> Dict[str, str]    # Provided output types
```

**Standard Pattern:**
1. Initialize with `super().__init__(name, path, position, node_type)`
2. Create `_parms` dictionary with `Parm` objects
3. Set default parameter values
4. Implement processing in `_internal_cook()`
5. Set `self._output` with results
6. Manage `NodeState` appropriately

## 3. Core Concepts

### Node Lifecycle

Nodes exist in a dependency graph where data flows from inputs to outputs. The system uses a "cooking" metaphor - nodes "cook" (process) when their inputs change or when explicitly requested.

**State Management:** Nodes track their processing state through `NodeState` enum:
- `UNCOOKED`: Needs processing
- `COOKING`: Currently processing  
- `UNCHANGED`: Up-to-date, no processing needed

**Cooking Process:** When `eval()` is called, the system:
1. Checks if cooking is needed via `needs_to_cook()`
2. Cooks dependencies first through `cook_dependencies()`
3. Calls `_internal_cook()` for actual processing
4. Updates state and caches results

### Visual Identity & Grouping

Each node has a visual identity defined by two class variables:

**GLYPH:** A single character or emoji that represents the node visually in the UI. Choose something intuitive:
- Text operations: `'Ꭲ'`, `'⎔'`, `'§'`
- File I/O: `'⤵'` (in), `'⤴'` (out), `'📁'` (folder)
- List operations: `'⋈'` (merge), `'⋔'` (split), `'≣'` (make list)
- Flow control: `'⟲'` (loop), `'∅'` (null), `'⌘'` (query)
- Search/Find: `'🔍'`, `'#'` (count)

**GROUP:** Categorizes nodes by function using `FunctionalGroup` enum:
- `FunctionalGroup.TEXT` - Text manipulation and formatting
- `FunctionalGroup.FILE` - File system operations
- `FunctionalGroup.LIST` - List processing and transformation
- `FunctionalGroup.FLOW` - Control flow and logic

These identifiers help users quickly recognize node types and organize their workflows.

### Connection System

Nodes connect through `NodeConnection` objects that link outputs to inputs. The base `Node` class manages these connections automatically - you define the interface through name and type methods.

**Single vs Multiple Connections:** Use `SINGLE_INPUT`/`SINGLE_OUTPUT` class variables to restrict connection counts. Most nodes are single-input/single-output for simplicity.

**Data Flow:** All data passes as `List[str]` between nodes. Input validation and type conversion happens in individual nodes as needed.

### Parameter System

Parameters expose node configuration through the `Parm` class, supporting various types (STRING, INT, FLOAT, TOGGLE, BUTTON, etc.). Parameters can hold static values or expressions that evaluate dynamically.

Time-dependent nodes (those with expression parameters) automatically recook on every evaluation by setting `self._is_time_dependent = True`.

## 4. Implementation Details

### Class Structure

Every node inherits from the base `Node` class and must implement specific methods:

```python
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.enums import FunctionalGroup

class ExampleNode(Node):
    GLYPH = '⚡'                    # Visual identifier in UI
    GROUP = FunctionalGroup.TEXT   # Functional category
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False

        # Initialize parameters
        self._parms: Dict[str, Parm] = {
            "param_name": Parm("param_name", ParameterType.STRING, self),
        }

        # Set defaults
        self._parms["param_name"].set("default_value")
```

### Parameter Management

Parameters are the primary interface for node configuration. Create them in `__init__()`:

```python
self._parms: Dict[str, Parm] = {
    "text_input": Parm("text_input", ParameterType.STRING, self),
    "enabled": Parm("enabled", ParameterType.TOGGLE, self),
    "count": Parm("count", ParameterType.INT, self),
    "refresh": Parm("refresh", ParameterType.BUTTON, self),
}
```

**Parameter Types:**
- `STRING`: Text input
- `INT`/`FLOAT`: Numeric values
- `TOGGLE`: Boolean flags
- `BUTTON`: Trigger actions
- `STRINGLIST`: List of strings

**Accessing Values:** Use `.eval()` for current values, `.raw_value()` for stored values:
```python
current_text = self._parms["text_input"].eval()
```

### Core Processing Method

Implement all processing logic in `_internal_cook()`:

```python
def _internal_cook(self, force: bool = False) -> None:
    self.set_state(NodeState.COOKING)
    self._cook_count += 1
    start_time = time.time()
    
    try:
        # Get input data
        input_data = []
        if self.inputs():
            input_data = self.inputs()[0].output_node().eval(requesting_node=self)
        
        # Get parameter values
        param_value = self._parms["param_name"].eval()
        
        # Process data
        result = self.process_data(input_data, param_value)
        
        # Set output
        self._output = result
        self.set_state(NodeState.UNCHANGED)
        
    except Exception as e:
        self.add_error(f"Processing error: {str(e)}")
        self.set_state(NodeState.UNCOOKED)
    
    self._last_cook_time = (time.time() - start_time) * 1000
```

### Interface Methods

Define connection interfaces through these methods:

```python
def input_names(self) -> Dict[str, str]:
    return {"input": "Input Text"}

def output_names(self) -> Dict[str, str]:
    return {"output": "Processed Text"}

def input_data_types(self) -> Dict[str, str]:
    return {"input": "List[str]"}

def output_data_types(self) -> Dict[str, str]:
    return {"output": "List[str]"}
```

### Error Handling

Use built-in error management:
```python
self.add_error("Critical error message")      # Stops processing
self.add_warning("Non-critical warning")     # Continues processing
```

Errors automatically set node state to `UNCOOKED`. Always wrap processing in try/catch blocks.

## 5. Common Patterns

### Simple Processing Node (TextNode Pattern)

TextNode demonstrates straightforward text manipulation:

```python
def _internal_cook(self, force: bool = False) -> None:
    # Standard setup
    self.set_state(NodeState.COOKING)
    start_time = time.time()
    
    # Get parameters
    text_string = self._parms["text_string"].eval()
    pass_through = self._parms["pass_through"].eval()
    
    # Get input
    input_data = []
    if pass_through and self.inputs():
        input_data = self.inputs()[0].output_node().eval(requesting_node=self)
    
    # Process using helper method
    parsed_strings = self._parse_string_list(text_string)
    
    # Combine/manipulate data
    if input_data:
        result = self.combine_data(parsed_strings, input_data)
    else:
        result = parsed_strings
        
    # Standard cleanup
    self._output = result
    self.set_state(NodeState.UNCHANGED)
    self._last_cook_time = (time.time() - start_time) * 1000
```

### File I/O Node (FileInNode Pattern)

FileInNode shows file handling with validation:

```python
def _internal_cook(self, force: bool = False) -> None:
    self.set_state(NodeState.COOKING)
    start_time = time.time()
    
    try:
        # File operations with validation
        file_path = self._parms["file_name"].eval()
        
        if not file_path:
            raise ValueError("File path is empty")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Read and process
        with open(file_path, 'r') as file:
            content = file.read()
            
        # Hash-based change detection
        new_hash = self._calculate_file_hash(content)
        if force or new_hash != self._file_hash:
            self._output = self._parse_string_list(content)
            self._file_hash = new_hash
            
        self.set_state(NodeState.UNCHANGED)
        
    except Exception as e:
        self.add_error(f"Error processing file: {str(e)}")
        self.set_state(NodeState.UNCOOKED)
```

### Complex Internal Management (LooperNode Pattern)

LooperNode demonstrates advanced patterns with internal nodes:

```python
def __init__(self, name: str, path: str, node_type: NodeType):
    super().__init__(name, path, [0.0, 0.0], node_type)
    
    # Complex parameter setup
    self._parms: Dict[str, Parm] = {
        "min": Parm("min", ParameterType.INT, self),
        "max": Parm("max", ParameterType.INT, self),
        "timeout_limit": Parm("timeout_limit", ParameterType.FLOAT, self),
    }
    
    # Internal state management
    self._internal_nodes_created = False
    self._input_node = None
    self._output_node = None

@classmethod
def post_registration_init(cls, node):
    """Called after node registration for complex setup"""
    if isinstance(node, LooperNode):
        node._create_internal_nodes()

def validate_parameters(self):
    """Custom validation beyond basic type checking"""
    min_val = self._parms["min"].eval()
    max_val = self._parms["max"].eval()
    
    if min_val > max_val:
        self.add_error("'min' must be less than 'max'")
```

## 6. Integration Points

### Automatic Discovery

Nodes are discovered automatically based on filename patterns. Place your node file in `src/core/` with naming convention:
```
your_node_name_node.py → YourNodeNameNode class
```

The system dynamically imports modules and instantiates node classes based on `NodeType` enum values.

### NodeEnvironment Integration

`NodeEnvironment` manages the global node registry. Your nodes automatically participate through:
- Registration on creation via `Node.create_node()`
- Path-based lookup and hierarchy management
- Connection validation and cleanup

### Evaluation System

The evaluation system calls your node through:
1. `eval()` - Public interface that checks cooking needs
2. `cook()` - Dependency management and cooking coordination  
3. `_internal_cook()` - Your implementation
4. `get_output()` - Result retrieval with connection context

### Connection Management

Base `Node` class handles all connection logic. Your role:
- Define interface through name/type methods
- Validate input data in `_internal_cook()`
- Set `SINGLE_INPUT`/`SINGLE_OUTPUT` flags appropriately

### State Propagation

Node states flow through the dependency graph. Error states prevent downstream cooking, while `UNCHANGED` states enable caching and performance optimization.

## 7. Troubleshooting/Gotchas

### Common Mistakes

**Forgetting State Management:** Always set `NodeState.COOKING` at start and appropriate final state. Missing state updates cause evaluation issues.

**Parameter Access Errors:** Use `.eval()` for current values, not direct dictionary access. Parameters may contain expressions requiring evaluation.

**Input Validation:** Check `self.inputs()` before accessing. Not all nodes have inputs, and connections can change.

**Exception Handling:** Unhandled exceptions leave nodes in inconsistent states. Always wrap processing in try/catch blocks.

### Performance Considerations

**Hash-Based Caching:** Implement `needs_to_cook()` with hash comparison for expensive operations. See FileInNode example with `_calculate_file_hash()`.

**Time Dependencies:** Set `self._is_time_dependent = True` only when necessary. Time-dependent nodes recook on every evaluation.

**Memory Management:** Large data processing should consider the LooperNode pattern with memory limits and timeout protection.

### Debugging Tips

**Cook Count Tracking:** Use `self._cook_count` to verify cooking frequency. Unexpected cooking indicates dependency or state issues.

**Error Messages:** Include context in error messages. "Processing failed" is less helpful than "File processing failed: permission denied for /path/file.txt".

**State Inspection:** Check node state through the UI or debugging tools. `COOKING` state that persists indicates incomplete processing methods.

The node system is designed for robustness - follow these patterns and most integration issues resolve automatically.