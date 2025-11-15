import sys
import argparse
from pathlib import Path
from typing import Optional
from repl.namespace import build_namespace
from repl.helpers import (
    create, connect, connect_next, disconnect, destroy,
    run, inspect, tree, ls, find,
    load, save, clear, types, get_global, set_global, globals_dict, parm
)


VERSION = "1.0.0"


def get_banner():
    return """
TextLoom Python Shell (tloom)
==============================
Available helpers:
  create(type, name, **params)   - Create node with optional params
  connect(src, dst, out=0, in=0) - Connect nodes at specific indices
  connect_next(src, dst, out=0)  - Connect to next available input
  disconnect(node, input_idx)    - Remove input connection
  destroy(node)                  - Delete node
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
        'connect_next': connect_next,
        'disconnect': disconnect,
        'destroy': destroy,
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
        try:
            import readline
            import rlcompleter
            readline.set_completer(rlcompleter.Completer(namespace).complete)
            readline.parse_and_bind("tab: complete")
        except ImportError:
            pass

        import code
        code.interact(banner=get_banner(), local=namespace)


def main():
    parser = argparse.ArgumentParser(
        prog='tloom',
        description='TextLoom Python Shell - Interactive REPL for TextLoom node workflows',
        epilog='Examples:\n  tloom                  # Interactive shell\n  tloom workflow.json    # Load flowstate\n  tloom script.py        # Execute script',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'file',
        nargs='?',
        help='Workflow file (.json) to load or script file (.py) to execute'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'tloom {VERSION}'
    )

    args = parser.parse_args()

    flowstate_file = None
    script_file = None

    if args.file:
        file_path = Path(args.file)

        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        if file_path.suffix == '.json':
            flowstate_file = file_path
        elif file_path.suffix == '.py':
            script_file = file_path
        else:
            print(f"Error: Unknown file type: {file_path}", file=sys.stderr)
            print("Supported types: .json (flowstate), .py (script)", file=sys.stderr)
            sys.exit(1)

    run_shell(flowstate_file, script_file)


if __name__ == "__main__":
    main()
