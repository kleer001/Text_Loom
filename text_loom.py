#!/usr/bin/env python3
"""
Text Loom Master Launcher
==========================
Unified entry point for all Text Loom interfaces:
- REPL: Interactive Python shell
- TUI: Terminal User Interface
- API: Web server backend
- GUI: Full web application (default)
- Batch: Non-interactive workflow execution

Usage:
    text_loom.py [--repl|--tui|--api|--gui|--batch] [--file FILE] [options]

Examples:
    text_loom.py                        # Start GUI (default)
    text_loom.py --repl                 # Interactive shell
    text_loom.py --tui workflow.json    # TUI with loaded workflow
    text_loom.py --batch workflow.tl    # Execute workflow and exit
    text_loom.py --gui --no-browser     # GUI without auto-opening browser
    text_loom.py --api --port 8080      # API server on custom port
"""

import sys
import os
import argparse
import subprocess
import webbrowser
import time
from pathlib import Path
from threading import Thread
from typing import Optional

# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

VERSION = "1.0.0"


# ANSI color codes for GUI mode output
class Colors:
    TEAL = '\033[38;5;30m'
    BURGUNDY = '\033[38;5;88m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'


def validate_file(file_path: Optional[str]) -> Optional[Path]:
    """Validate and return Path object for workflow file."""
    if not file_path:
        return None

    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    if path.suffix not in ['.json', '.tl']:
        print(f"Error: Invalid file type: {path.suffix}", file=sys.stderr)
        print("Supported formats: .json, .tl", file=sys.stderr)
        sys.exit(1)

    return path


def launch_repl(workflow_file: Optional[Path] = None):
    """Launch the interactive Python REPL."""
    from repl.tloom_shell import run_shell

    print(f"{Colors.GREEN}Launching Text Loom REPL...{Colors.RESET}\n")
    run_shell(flowstate_file=workflow_file)


def launch_tui(workflow_file: Optional[Path] = None):
    """Launch the Terminal User Interface."""
    from TUI.tui_skeleton import TUIApp
    from core.flowstate_manager import load_flowstate

    print(f"{Colors.GREEN}Launching Text Loom TUI...{Colors.RESET}")

    # Load workflow before starting TUI if provided
    if workflow_file:
        try:
            load_flowstate(str(workflow_file))
            print(f"Loaded workflow: {workflow_file}")
        except Exception as e:
            print(f"Error loading workflow: {e}", file=sys.stderr)
            sys.exit(1)

    app = TUIApp()
    try:
        app.run()
    except Exception as e:
        print(f"TUI Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def launch_api(port: int = 8000, workflow_file: Optional[Path] = None):
    """Launch the FastAPI backend server."""
    print(f"{Colors.GREEN}Launching Text Loom API Server on port {port}...{Colors.RESET}")

    if workflow_file:
        print(f"{Colors.YELLOW}Note: Workflow file will be available via API endpoints{Colors.RESET}")
        print(f"  Load via: POST /api/v1/workspace/load with file: {workflow_file}")

    print(f"\nAPI Documentation:")
    print(f"  Swagger UI: http://localhost:{port}/api/v1/docs")
    print(f"  ReDoc:      http://localhost:{port}/api/v1/redoc")
    print(f"\nPress Ctrl+C to stop\n")

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    try:
        subprocess.run(
            ["uvicorn", "api.main:app", "--reload", "--port", str(port)],
            cwd=PROJECT_ROOT,
            env=env
        )
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}API server stopped.{Colors.RESET}")


def stream_output(process, prefix, color):
    """Stream process output with colored prefix."""
    while True:
        line = process.stdout.readline()
        if line:
            decoded = line.decode().rstrip()
            if decoded:
                print(f"{color}[{prefix}]{Colors.RESET} {decoded}", flush=True)

        if process.poll() is not None:
            # Read any remaining output
            for line in process.stdout.readlines():
                decoded = line.decode().rstrip()
                if decoded:
                    print(f"{color}[{prefix}]{Colors.RESET} {decoded}", flush=True)
            break


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Wait for server to be ready."""
    import socket
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(0.5)

    return False


def launch_gui(open_browser: bool = True, backend_port: int = 8000,
               frontend_port: int = 5173, workflow_file: Optional[Path] = None):
    """Launch the full GUI (backend + frontend + browser)."""
    print(f"{Colors.GREEN}Launching Text Loom GUI...{Colors.RESET}\n")

    if workflow_file:
        print(f"{Colors.YELLOW}Workflow file: {workflow_file}{Colors.RESET}")
        print(f"  Load via File Browser in the GUI\n")

    # Environment for backend - disable buffering
    backend_env = os.environ.copy()
    backend_env['PYTHONUNBUFFERED'] = '1'

    # Start backend
    backend = subprocess.Popen(
        ["uvicorn", "api.main:app", "--reload", "--port", str(backend_port)],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=backend_env,
        bufsize=0
    )

    # Start frontend
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=PROJECT_ROOT / "src" / "GUI",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0
    )

    print("Starting backend and frontend...")
    print(f"Press Ctrl+C to stop all services\n")

    # Stream outputs in threads
    Thread(target=stream_output, args=(backend, "BACKEND", Colors.BURGUNDY), daemon=True).start()
    Thread(target=stream_output, args=(frontend, "FRONTEND", Colors.TEAL), daemon=True).start()

    # Open browser if requested
    if open_browser:
        print(f"{Colors.YELLOW}Waiting for servers to start...{Colors.RESET}")
        if wait_for_server(frontend_port, timeout=30):
            time.sleep(1)  # Give it a moment to fully initialize
            url = f"http://localhost:{frontend_port}"
            print(f"{Colors.GREEN}Opening browser: {url}{Colors.RESET}\n")
            webbrowser.open(url)
        else:
            print(f"{Colors.YELLOW}Frontend not ready, skipping browser launch{Colors.RESET}")
            print(f"  Manually open: http://localhost:{frontend_port}\n")
    else:
        print(f"GUI available at: http://localhost:{frontend_port}")
        print(f"API available at: http://localhost:{backend_port}\n")

    try:
        # Wait for both processes
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GREEN}Shutting down...{Colors.RESET}")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print(f"{Colors.GREEN}Services stopped.{Colors.RESET}")


def launch_batch(workflow_file: Path):
    """Execute workflow in batch mode (non-interactive)."""
    from core.flowstate_manager import load_flowstate
    from core.base_classes import NodeEnvironment

    print(f"{Colors.GREEN}Batch Mode: Processing {workflow_file}{Colors.RESET}")

    if not workflow_file:
        print("Error: Batch mode requires a workflow file", file=sys.stderr)
        print("Usage: text_loom.py --batch workflow.json", file=sys.stderr)
        sys.exit(1)

    try:
        # Load the workflow
        print(f"Loading workflow: {workflow_file}")
        load_flowstate(str(workflow_file))

        # Get all nodes
        env = NodeEnvironment.get_instance()
        nodes = list(env.nodes.values())

        if not nodes:
            print("Warning: No nodes found in workflow", file=sys.stderr)
            return

        print(f"Found {len(nodes)} nodes")

        # Execute all nodes in topological order
        print("Executing workflow...")
        executed = 0
        errors = []

        for node in nodes:
            try:
                result = node.cook()
                executed += 1
                print(f"  Executed: {node.path()} -> {type(result).__name__}")
            except Exception as e:
                error_msg = f"  Error in {node.path()}: {e}"
                print(error_msg, file=sys.stderr)
                errors.append(error_msg)

        # Summary
        print(f"\n{Colors.GREEN}Batch execution complete:{Colors.RESET}")
        print(f"  Nodes executed: {executed}/{len(nodes)}")

        if errors:
            print(f"  Errors: {len(errors)}")
            for err in errors:
                print(f"    {err}")
            sys.exit(1)
        else:
            print(f"  Status: {Colors.GREEN}SUCCESS{Colors.RESET}")

    except Exception as e:
        print(f"\n{Colors.YELLOW}Batch execution failed: {e}{Colors.RESET}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        prog='text_loom.py',
        description='Text Loom - Unified launcher for all interfaces',
        epilog='''
Examples:
  %(prog)s                        # Start GUI (default)
  %(prog)s --repl                 # Interactive Python shell
  %(prog)s --tui workflow.json    # Terminal UI with workflow
  %(prog)s --batch workflow.tl    # Execute workflow and exit
  %(prog)s --gui --no-browser     # GUI without auto-opening browser
  %(prog)s --api --port 8080      # API server on custom port
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Version
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'Text Loom {VERSION}'
    )

    # Interface modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--repl',
        action='store_true',
        help='Launch interactive Python REPL'
    )
    mode_group.add_argument(
        '--tui',
        action='store_true',
        help='Launch Terminal User Interface'
    )
    mode_group.add_argument(
        '--api',
        action='store_true',
        help='Launch API server only'
    )
    mode_group.add_argument(
        '--gui',
        action='store_true',
        help='Launch full GUI (backend + frontend + browser)'
    )
    mode_group.add_argument(
        '--batch',
        action='store_true',
        help='Execute workflow in batch mode (non-interactive)'
    )

    # Common options
    parser.add_argument(
        '--file', '-f',
        type=str,
        metavar='FILE',
        help='Workflow file to load (.json or .tl)'
    )

    # GUI-specific options
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='GUI mode: Do not automatically open browser'
    )

    # API/GUI port options
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        metavar='PORT',
        help='API server port (default: 8000)'
    )

    parser.add_argument(
        '--frontend-port',
        type=int,
        default=5173,
        metavar='PORT',
        help='Frontend dev server port (default: 5173)'
    )

    args = parser.parse_args()

    # Validate workflow file if provided
    workflow_file = validate_file(args.file)

    # Determine which mode to launch
    if args.repl:
        launch_repl(workflow_file)
    elif args.tui:
        launch_tui(workflow_file)
    elif args.api:
        launch_api(args.port, workflow_file)
    elif args.batch:
        if not workflow_file:
            parser.error("--batch requires --file argument")
        launch_batch(workflow_file)
    else:
        # Default to GUI mode
        launch_gui(
            open_browser=not args.no_browser,
            backend_port=args.port,
            frontend_port=args.frontend_port,
            workflow_file=workflow_file
        )


if __name__ == "__main__":
    main()
