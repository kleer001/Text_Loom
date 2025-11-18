# Sphinx Documentation Migration Plan
 
## Phase 1: Setup (~30 mins)
 
```bash
pip install sphinx sphinx-rtd-theme
cd docs/  # create if needed
sphinx-quickstart
```
 
**conf.py additions:**
```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]
napoleon_google_docstring = True
html_theme = 'sphinx_rtd_theme'
```
 
---
 
## Phase 2: Docstring Conversion Format
 
### Google Style Template
 
```python
class NodeName(Node):
    """Short one-line description.
 
    Longer description paragraph explaining the node's purpose
    and primary use case.
 
    Args:
        name: Node name identifier
        path: Node path in hierarchy
        node_type: Type classification
 
    Attributes:
        param_name (type): Description of parameter.
        another_param (type): Another description.
 
    Example:
        >>> node = NodeName("test", "/root", NodeType.X)
        >>> node.cook()
 
    Note:
        Important caveats or special behavior.
    """
```
 
---
 
## Phase 3: Conversion Checklist
 
### Priority 1 - Core Nodes
- [ ] text_node.py
- [ ] query_node.py
- [ ] merge_node.py
- [ ] split_node.py
- [ ] looper_node.py
 
### Priority 2 - I/O Nodes
- [ ] file_in_node.py
- [ ] file_out_node.py
- [ ] folder_node.py
 
### Priority 3 - Utility Nodes
- [ ] section_node.py
- [ ] make_list_node.py
- [ ] json_node.py
- [ ] null_node.py
- [ ] input_null_node.py
- [ ] output_null_node.py
 
---
 
## Conversion Example
 
### Before (current style):
```python
"""
QueryNode: A node that interfaces with Large Language Models...
 
Key Features:
    1. LLM Integration:
        - Automatically detects...
 
Parameters:
    limit (bool):
        When True, restricts processing...
"""
```
 
### After (Google style):
```python
"""A node that interfaces with Large Language Models.
 
Enables prompt-based text generation by connecting to local
LLM installations like Ollama.
 
Attributes:
    limit (bool): Restricts processing to first prompt only.
    response (List[str]): History of LLM responses.
    llm_name (str): Target LLM identifier (default: "Ollama").
    find_llm (button): Triggers automatic LLM detection.
    respond (button): Forces reprocessing of prompts.
 
Example:
    >>> query = Node.create_node(NodeType.QUERY)
    >>> query.parms()["llm_name"].set("Ollama")
    >>> query.cook()
 
Note:
    Always time-dependent. Response caching available but not forced.
"""
```
 
---
 