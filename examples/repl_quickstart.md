# TextLoom REPL Quickstart

The TextLoom REPL (Read-Eval-Print Loop) provides a Python shell with the full TextLoom API pre-loaded, similar to Houdini's `hython`.

## Starting the REPL

```bash
./tloom                    # Start interactive shell
./tloom workflow.json      # Load flowstate and start shell
./tloom script.py          # Execute script with TextLoom environment
```

## Basic Usage

### Creating Nodes

```python
text = create('text', 'my_text')
text = create('text', text_string="Hello World")
query = create('query', 'llm_query', query_string="What is AI?")
```

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
```

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
text1 = create('text', text_string="Hello")
text2 = create('text', text_string="World")
merge = create('merge')

connect(text1, merge, target_input=0)
connect(text2, merge, target_input=1)

result = run(merge)
print(result)

save('hello_world.json')
```

## Tips

- Use tab completion to explore available functions and classes
- Access node parameters via `node._parms['param_name']`
- All core TextLoom classes are pre-loaded (Node, NodeEnvironment, etc.)
- Type `types()` to see all available node types
- Use `help(function)` for detailed documentation
