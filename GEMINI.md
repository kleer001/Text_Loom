# GEMINI.md

## Project Overview

This project, Text Loom, is a visual programming environment for building and executing LLM-based text processing workflows. It allows users to create, connect, and run nodes in a graph-based editor to perform complex text manipulations.

The project consists of several key components:

*   **Core Engine:** A Python-based engine that manages the node graph, data flow, and execution logic.
*   **Backend API:** A FastAPI server that exposes a RESTful API for interacting with the core engine. This allows for programmatic control and integration.
*   **Frontend GUI:** A React-based web interface that provides a visual node editor for creating and managing workflows.
*   **Terminal User Interface (TUI):** A terminal-based interface for users who prefer a command-line experience.
*   **REPL:** An interactive Python shell for scripting and direct interaction with the Text Loom core.

The system is designed to be modular and extensible, allowing for the creation of custom nodes and workflows. It supports various LLMs and provides a flexible framework for text-based data processing.

## Building and Running

### Prerequisites

*   Python 3.8+
*   Node.js and npm

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kleer001/Text_Loom
    cd Text_Loom
    ```

2.  **Set up the Python environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src
    ```

3.  **Install frontend dependencies:**
    ```bash
    cd src/GUI
    npm install
    ```

### Running the Application

Text Loom can be run in several modes:

*   **GUI Mode:**
    ```bash
    ./text_loom.py -g
    ```
    This will start the FastAPI backend and the Vite development server for the React frontend. The GUI will be accessible at `http://localhost:5173`.

*   **TUI Mode:**
    ```bash
    ./text_loom.py -t
    ```

*   **REPL Mode:**
    ```bash
    ./text_loom.py -r
    ```

*   **API Only:**
    ```bash
    ./text_loom.py -a
    ```
    The API documentation will be available at `http://localhost:8000/api/v1/docs`.

*   **Batch Mode:**
    ```bash
    ./text_loom.py -b -f <workflow_file.json>
    ```

### Testing

The project contains a `tests` directory with a suite of tests. To run the tests, you can use `pytest`:

```bash
pytest
```

## Development Conventions

*   **Backend:** The backend is written in Python and uses FastAPI. Code is organized into modules within the `src` directory.
*   **Frontend:** The frontend is a React application built with Vite. Source code is located in `src/GUI/src`.
*   **Styling:** The project uses a consistent coding style, but there is no explicit linter configuration file. It is recommended to follow the existing code style.
*   **Dependencies:** Python dependencies are managed in `setup.py`, and frontend dependencies are in `src/GUI/package.json`.
*   **API:** The API follows RESTful principles and is documented using OpenAPI (Swagger) and ReDoc.
