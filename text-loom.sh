#!/bin/bash
# text-loom.sh
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "${SCRIPT_DIR}/.venv/bin/activate"
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"
python3 "${SCRIPT_DIR}/src/TUI/tui_skeleton.py" "$@"

REM text-loom.bat
@echo off
SET SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
SET PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%
python "%SCRIPT_DIR%src\TUI\tui_skeleton.py" %*