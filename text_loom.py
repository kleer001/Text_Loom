#!/usr/bin/env python3
"""Text Loom unified launcher for REPL, TUI, API, GUI, and batch modes."""

import sys
import os
import socket
import argparse
import subprocess
import time
from enum import Enum
from pathlib import Path
from threading import Thread
from typing import Optional
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

VERSION = "1.0.0"
VALID_EXTENSIONS = {'.json', '.tl'}
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 5173
SERVER_TIMEOUT = 30


class Color(str, Enum):
    TEAL = '\033[38;5;30m'
    BURGUNDY = '\033[38;5;88m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'


@dataclass
class ServerConfig:
    backend_port: int = DEFAULT_BACKEND_PORT
    frontend_port: int = DEFAULT_FRONTEND_PORT
    open_browser: bool = True


class Output:
    @staticmethod
    def colored(message: str, color: Color) -> str:
        return f"{color.value}{message}{Color.RESET.value}"

    @staticmethod
    def info(message: str):
        print(Output.colored(message, Color.GREEN))

    @staticmethod
    def warn(message: str):
        print(Output.colored(message, Color.YELLOW))

    @staticmethod
    def error(message: str):
        print(Output.colored(message, Color.YELLOW), file=sys.stderr)

    @staticmethod
    def fail(message: str, code: int = 1):
        Output.error(message)
        sys.exit(code)


class WorkflowFile:
    def __init__(self, path: Optional[str]):
        self.path = self._validate(path) if path else None

    def _validate(self, path_str: str) -> Path:
        path = Path(path_str)

        if not path.exists():
            Output.fail(f"File not found: {path}")

        if path.suffix not in VALID_EXTENSIONS:
            Output.fail(f"Invalid file type: {path.suffix}\nSupported: {', '.join(VALID_EXTENSIONS)}")

        return path

    def __bool__(self):
        return self.path is not None

    def __str__(self):
        return str(self.path)


class ProcessStream:
    def __init__(self, process: subprocess.Popen, prefix: str, color: Color):
        self.process = process
        self.prefix = prefix
        self.color = color

    def _format_line(self, line: str) -> str:
        return f"{self.color.value}[{self.prefix}]{Color.RESET.value} {line}"

    def _read_lines(self):
        for line in self.process.stdout:
            decoded = line.decode().rstrip()
            if decoded:
                yield decoded

    def stream(self):
        for line in self._read_lines():
            print(self._format_line(line), flush=True)


class REPLLauncher:
    @staticmethod
    def run(workflow: WorkflowFile):
        from repl.tloom_shell import run_shell

        Output.info("Launching Text Loom REPL...\n")
        run_shell(flowstate_file=workflow.path)


class TUILauncher:
    @staticmethod
    def run(workflow: WorkflowFile):
        from TUI.tui_skeleton import TUIApp

        Output.info("Launching Text Loom TUI...")

        if workflow:
            TUILauncher._load_workflow(workflow)

        try:
            TUIApp().run()
        except Exception as e:
            import traceback
            Output.error(f"TUI Error: {e}")
            traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def _load_workflow(workflow: WorkflowFile):
        from core.flowstate_manager import load_flowstate

        try:
            load_flowstate(str(workflow))
            print(f"Loaded workflow: {workflow}")
        except Exception as e:
            Output.fail(f"Error loading workflow: {e}")


class APILauncher:
    @staticmethod
    def run(port: int, workflow: WorkflowFile):
        Output.info(f"Launching Text Loom API Server on port {port}...")

        if workflow:
            Output.warn("Workflow file available via API endpoints")
            print(f"  Load via: POST /api/v1/workspace/load with file: {workflow}")

        APILauncher._show_docs(port)

        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'

        try:
            subprocess.run(
                ["uvicorn", "api.main:app", "--reload", "--port", str(port)],
                cwd=PROJECT_ROOT,
                env=env
            )
        except KeyboardInterrupt:
            Output.info("\nAPI server stopped.")

    @staticmethod
    def _show_docs(port: int):
        print("\nAPI Documentation:")
        print(f"  Swagger UI: http://localhost:{port}/api/v1/docs")
        print(f"  ReDoc:      http://localhost:{port}/api/v1/redoc")
        print("\nPress Ctrl+C to stop\n")


class GUILauncher:
    def __init__(self, config: ServerConfig, workflow: WorkflowFile):
        self.config = config
        self.workflow = workflow
        self.backend = None
        self.frontend = None

    def run(self):
        Output.info("Launching Text Loom GUI...\n")

        if self.workflow:
            Output.warn(f"Workflow file: {self.workflow}")
            print("  Load via File Browser in the GUI\n")

        self._start_servers()
        self._stream_outputs()
        self._open_browser_if_requested()
        self._wait()

    def _start_servers(self):
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'

        self.backend = subprocess.Popen(
            ["uvicorn", "api.main:app", "--reload", "--port", str(self.config.backend_port)],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=0
        )

        self.frontend = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=PROJECT_ROOT / "src" / "GUI",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0
        )

        print("Starting backend and frontend...")
        print("Press Ctrl+C to stop all services\n")

    def _stream_outputs(self):
        Thread(
            target=ProcessStream(self.backend, "BACKEND", Color.BURGUNDY).stream,
            daemon=True
        ).start()

        Thread(
            target=ProcessStream(self.frontend, "FRONTEND", Color.TEAL).stream,
            daemon=True
        ).start()

    def _open_browser_if_requested(self):
        self._show_urls()

    def _show_urls(self):
        print(f"GUI available at: http://localhost:{self.config.frontend_port}")
        print(f"API available at: http://localhost:{self.config.backend_port}\n")

    def _wait(self):
        try:
            self.backend.wait()
            self.frontend.wait()
        except KeyboardInterrupt:
            self._shutdown()

    def _shutdown(self):
        Output.info("\n\nShutting down...")
        if self.backend:
            self.backend.terminate()
            self.backend.wait()
        if self.frontend:
            self.frontend.terminate()
            self.frontend.wait()
        Output.info("Services stopped.")


class BatchLauncher:
    @staticmethod
    def run(workflow: WorkflowFile):
        from core.flowstate_manager import load_flowstate
        from core.base_classes import NodeEnvironment

        if not workflow:
            Output.fail("Batch mode requires a workflow file\nUsage: text_loom.py -b -f workflow.json")

        Output.info(f"Batch Mode: Processing {workflow}")

        try:
            print(f"Loading workflow: {workflow}")
            load_flowstate(str(workflow))

            nodes = list(NodeEnvironment.get_instance().nodes.values())

            if not nodes:
                Output.warn("Warning: No nodes found in workflow")
                return

            BatchLauncher._execute_workflow(nodes)

        except Exception as e:
            import traceback
            Output.error(f"\nBatch execution failed: {e}")
            traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def _execute_workflow(nodes):
        print(f"Found {len(nodes)} nodes")
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

        BatchLauncher._show_summary(executed, len(nodes), errors)

    @staticmethod
    def _show_summary(executed: int, total: int, errors: list):
        Output.info(f"\nBatch execution complete:")
        print(f"  Nodes executed: {executed}/{total}")

        if errors:
            print(f"  Errors: {len(errors)}")
            for err in errors:
                print(f"    {err}")
            sys.exit(1)
        else:
            print(f"  Status: {Output.colored('SUCCESS', Color.GREEN)}")


class ArgumentParser:
    @staticmethod
    def parse():
        parser = argparse.ArgumentParser(
            prog='text_loom.py',
            description='Text Loom - Unified launcher for all interfaces',
            epilog=ArgumentParser._examples(),
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument('-v', '--version', action='version', version=f'Text Loom {VERSION}')

        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('-r', '--repl', action='store_true', help='Launch interactive Python REPL')
        mode.add_argument('-t', '--tui', action='store_true', help='Launch Terminal User Interface')
        mode.add_argument('-a', '--api', action='store_true', help='Launch API server only')
        mode.add_argument('-g', '--gui', action='store_true', help='Launch full GUI (backend + frontend + browser)')
        mode.add_argument('-b', '--batch', action='store_true', help='Execute workflow in batch mode (non-interactive)')

        parser.add_argument('-f', '--file', type=str, metavar='FILE', help='Workflow file to load (.json or .tl)')
        parser.add_argument('--no-browser', action='store_true', help='GUI mode: Do not automatically open browser')
        parser.add_argument('-p', '--port', type=ArgumentParser._valid_port, default=DEFAULT_BACKEND_PORT, metavar='PORT', help='API server port (default: 8000)')
        parser.add_argument('--frontend-port', type=ArgumentParser._valid_port, default=DEFAULT_FRONTEND_PORT, metavar='PORT', help='Frontend dev server port (default: 5173)')

        return parser.parse_args()

    @staticmethod
    def _valid_port(value):
        port = int(value)
        if not 1 <= port <= 65535:
            raise argparse.ArgumentTypeError(f"Port must be between 1 and 65535, got {port}")
        return port

    @staticmethod
    def _examples():
        return '''
Examples:
  %(prog)s                  # Start GUI (default)
  %(prog)s -r               # Interactive Python shell
  %(prog)s -t -f work.json  # Terminal UI with workflow
  %(prog)s -b -f work.tl    # Execute workflow and exit
  %(prog)s -g --no-browser  # GUI without auto-opening browser
  %(prog)s -a -p 8080       # API server on custom port
        '''


class Application:
    def __init__(self, args):
        self.workflow = WorkflowFile(args.file)
        self.config = ServerConfig(
            backend_port=args.port,
            frontend_port=args.frontend_port,
            open_browser=not args.no_browser
        )
        self.mode = self._determine_mode(args)

    def _determine_mode(self, args):
        if args.repl:
            return lambda: REPLLauncher.run(self.workflow)
        if args.tui:
            return lambda: TUILauncher.run(self.workflow)
        if args.api:
            return lambda: APILauncher.run(self.config.backend_port, self.workflow)
        if args.batch:
            return lambda: BatchLauncher.run(self.workflow)
        return lambda: GUILauncher(self.config, self.workflow).run()

    def run(self):
        self.mode()


def main():
    Application(ArgumentParser.parse()).run()


if __name__ == "__main__":
    main()
