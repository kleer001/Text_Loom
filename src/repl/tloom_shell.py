import sys
from pathlib import Path
from typing import Optional
from repl.namespace import build_namespace
from repl.helpers import (
    create, connect, run, inspect, tree, ls, find,
    load, save, clear, types, get_global, set_global, globals_dict, parm
)


def get_banner():
    return """
TextLoom Python Shell (tloom)
==============================
Available helpers:
  create(type, name, **params)   - Create node with optional params
  connect(src, dst, out=0, in=0) - Connect two nodes
  run(node, force=False)         - Execute node and return output
  parm(node, name, value=None)   - Get/set parameter value
  inspect(node)                  - Show node details
  tree(root=None)                - Display node hierarchy
  ls()                           - List all nodes
  find(name)                     - Find node by path
  load(filepath)                 - Load flowstate from file
  save(filepath)                 - Save flowstate to file
  clear()                        - Clear all nodes
  types()                        - List available node types
  get_global(key)                - Get global variable
  set_global(key, value)         - Set global variable
  globals_dict()                 - Get all globals

Core classes and environment pre-loaded.
Type 'help(<function>)' for more info.
"""


def run_shell(flowstate_file: Optional[Path] = None, script_file: Optional[Path] = None):
    namespace = build_namespace()

    namespace.update({
        'create': create,
        'connect': connect,
        'run': run,
        'parm': parm,
        'inspect': inspect,
        'tree': tree,
        'ls': ls,
        'find': find,
        'load': load,
        'save': save,
        'clear': clear,
        'types': types,
        'get_global': get_global,
        'set_global': set_global,
        'globals_dict': globals_dict,
    })

    if flowstate_file:
        load(str(flowstate_file))
        print(f"Loaded flowstate: {flowstate_file}")

    if script_file:
        with open(script_file) as f:
            exec(f.read(), namespace)
        return

    try:
        from IPython import embed
        embed(banner1=get_banner(), user_ns=namespace)
    except ImportError:
        import code
        code.interact(banner=get_banner(), local=namespace)


def main():
    flowstate_file = None
    script_file = None

    if len(sys.argv) > 1:
        arg_path = Path(sys.argv[1])
        if arg_path.suffix == '.json':
            flowstate_file = arg_path
        elif arg_path.suffix == '.py':
            script_file = arg_path
        else:
            print(f"Unknown file type: {arg_path}")
            sys.exit(1)

    run_shell(flowstate_file, script_file)


if __name__ == "__main__":
    main()
