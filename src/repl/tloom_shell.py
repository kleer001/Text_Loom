import sys
import argparse
from pathlib import Path
from typing import Optional
from repl.namespace import build_namespace
from repl.helpers import (
    create, connect, connect_next, disconnect, destroy,
    run, inspect, tree, ls, find,
    load, save, clear, types, get_global, set_global, globals_dict, parm,
    children, set_parent, errors, clear_errors, warnings, clear_warnings,
    input_names, output_names, node_type, input_nodes,
    cook_count, last_cook_time, needs_to_cook, is_time_dependent, cook_dependencies,
    inputs_with_indices, outputs_with_indices, node_exists, rename,
    token_totals, token_history, node_tokens, reset_tokens
)


VERSION = "1.0.0"


def get_banner():
    return """
TextLoom Python Shell (tloom)
==============================
Core helpers:
  create(type, name, **params)   - Create node with optional params
  connect(src, dst, out=0, in=0) - Connect nodes at specific indices
  connect_next(src, dst, out=0)  - Connect to next available input
  disconnect(node, input_idx)    - Remove input connection
  destroy(node)                  - Delete node
  run(node, force=False)         - Execute node and return output
  parm(node, name, value=None)   - Get/set parameter value
  inspect(node)                  - Show node details
  tree(root=None)                - Display node hierarchy
  ls(), find(name)               - List/find nodes
  load(file), save(file)         - Flowstate persistence
  clear()                        - Clear all nodes
  types()                        - List available node types

Debugging & performance:
  errors(node), warnings(node)   - Get errors/warnings
  cook_count(node)               - Times node has cooked
  last_cook_time(node)           - Last cook time in ms
  needs_to_cook(node)            - Check if node is dirty
  cook_dependencies(node)        - Get upstream nodes

Organization & introspection:
  children(node)                 - Get child nodes
  set_parent(node, path)         - Move node
  rename(old_path, new_parent)   - Rename/move node
  node_type(node)                - Get node type
  input_names(node)              - Get input names dict
  output_names(node)             - Get output names dict

Token tracking (LLM queries):
  token_totals()                 - Get session-wide token usage
  token_history()                - Get query history with timestamps
  node_tokens(node_name)         - Get per-node token totals
  reset_tokens()                 - Clear all token tracking data

Type 'help()' to see all functions. Tab completion enabled.
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
        'children': children,
        'set_parent': set_parent,
        'errors': errors,
        'clear_errors': clear_errors,
        'warnings': warnings,
        'clear_warnings': clear_warnings,
        'input_names': input_names,
        'output_names': output_names,
        'node_type': node_type,
        'input_nodes': input_nodes,
        'cook_count': cook_count,
        'last_cook_time': last_cook_time,
        'needs_to_cook': needs_to_cook,
        'is_time_dependent': is_time_dependent,
        'cook_dependencies': cook_dependencies,
        'inputs_with_indices': inputs_with_indices,
        'outputs_with_indices': outputs_with_indices,
        'node_exists': node_exists,
        'rename': rename,
        'token_totals': token_totals,
        'token_history': token_history,
        'node_tokens': node_tokens,
        'reset_tokens': reset_tokens,
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
