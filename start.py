#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
from threading import Thread
import select

# ANSI color codes
class Colors:
    TEAL = '\033[38;5;30m'
    BURGUNDY = '\033[38;5;88m'
    RESET = '\033[0m'

def stream_output(process, prefix, color):
    """Stream process output with colored prefix while preserving original colors"""
    while True:
        # Read from stdout
        line = process.stdout.readline()
        if line:
            decoded = line.decode().rstrip()
            if decoded:  # Only print non-empty lines
                print(f"{color}[{prefix}]{Colors.RESET} {decoded}", flush=True)
        
        # Check if process has ended
        if process.poll() is not None:
            # Read any remaining output
            for line in process.stdout.readlines():
                decoded = line.decode().rstrip()
                if decoded:
                    print(f"{color}[{prefix}]{Colors.RESET} {decoded}", flush=True)
            break

def main():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent.resolve()
    
    # Environment for backend - disable buffering
    backend_env = os.environ.copy()
    backend_env['PYTHONUNBUFFERED'] = '1'
    
    # Start backend (from script directory)
    backend = subprocess.Popen(
        ["uvicorn", "api.main:app", "--reload", "--port", "8000"],
        cwd=script_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        env=backend_env,
        bufsize=0  # Unbuffered
    )
    
    # Start frontend (from src/GUI subdirectory)
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=script_dir / "src" / "GUI",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        bufsize=0  # Unbuffered
    )
    
    print("Starting backend and frontend...")
    print("Press Ctrl+C to stop both services\n")
    
    # Stream outputs in threads with colors
    Thread(target=stream_output, args=(backend, "BACKEND", Colors.BURGUNDY), daemon=True).start()
    Thread(target=stream_output, args=(frontend, "FRONTEND", Colors.TEAL), daemon=True).start()
    
    try:
        # Wait for both processes
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("Services stopped.")

if __name__ == "__main__":
    main()
