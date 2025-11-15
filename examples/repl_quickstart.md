# TextLoom REPL Quickstart

The TextLoom REPL (Read-Eval-Print Loop) provides a Python shell with the full TextLoom API pre-loaded, similar to Houdini's `hython`.

## Installation

**Quick Start (from repo):**
```bash
./tloom
```

**Install as command:**
```bash
pip install -e .           # Basic install
pip install -e ".[repl]"   # With IPython (enhanced tab completion)
tloom
```

**Note:** Tab completion is always available, but IPython provides enhanced completion with better formatting and introspection.

## Usage

```bash
tloom                    # Start interactive shell
tloom workflow.json      # Load flowstate and start shell
tloom script.py          # Execute script with TextLoom environment
tloom --help             # Show help
tloom --version          # Show version
```

## Basic Usage

### Creating Nodes

```python
text = create('text', 'my_text')
text = create('text', text_string="Hello World")
query = create('query', 'llm_query', query_string="What is AI?")
```

The second parameter is the node name. If omitted, TextLoom auto-generates names like `text_1`, `text_2`, etc.

### Setting Parameters

```python
parm(text, 'text_string', "New value")
value = parm(text, 'text_string')
```

### Connecting Nodes

```python
text = create('text')
merge = create('merge')

connect(text, merge, source_output=0, target_input=0)
connect_next(text, merge)
```

`connect_next()` automatically finds the next available input slot, useful for nodes with multiple inputs.

### Running Nodes

```python
output = run(text)
output = run(text, force=True)
```

### Inspecting

```python
inspect(text)
tree()
ls()
find('/my_text')
```

### Flowstate Management

```python
save('my_workflow.json')
load('my_workflow.json')
clear()
```

### Globals

```python
set_global('PROJECT', 'my_project')
value = get_global('PROJECT')
all_globals = globals_dict()
```

## Example Workflow

```python
text1 = create('text', 'greeting', text_string="Hello")
text2 = create('text', 'farewell', text_string="World")
merge = create('merge', 'combiner')

connect_next(text1, merge)
connect_next(text2, merge)

result = run(merge)
print(result)

tree()

save('hello_world.json')
```

## Tips

- **Tab completion is enabled** - press TAB to autocomplete function names, variables, and methods
- Type `cre` then TAB to see `create`, `create(` to see parameters (IPython only)
- Type `text.` then TAB to see all methods available on a node object
- Access node parameters via `node._parms['param_name']`
- All core TextLoom classes are pre-loaded (Node, NodeEnvironment, etc.)
- Type `types()` to see all available node types
- Use `help(function)` for detailed documentation
- Install IPython (`pip install ipython`) for enhanced tab completion with parameter hints
