#!/bin/bash

CYAN='\033[1;36m'    
MAGENTA='\033[1;35m' 
BOLD='\033[1m'       
NC='\033[0m'         

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE=""

cleanup() {
    log "Cleaning up..."
    rm -rf "$SCRIPT_DIR/Text_Loom"
    rm -rf "$SCRIPT_DIR/venv"
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

setup_logging() {
    mkdir -p "$LOG_DIR"
    LOG_FILE="$LOG_DIR/install.log"
    if [ -f "$LOG_FILE" ]; then
        i=1
        while [ -f "$LOG_DIR/install_$i.log" ]; do
            ((i++))
        done
        LOG_FILE="$LOG_DIR/install_$i.log"
    fi
    touch "$LOG_FILE"
    log "Logging started"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_python_version() {
    PYTHON_VERSION=$(python3 -c 'import sys; ver = sys.version_info; print(f"{ver.major}.{ver.minor}")')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
        log "Error: Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    log "Python version $PYTHON_VERSION OK"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command_exists git; then
        log "Error: git is not installed. Please install git and try again."
        exit 1
    fi
    
    if ! command_exists python3; then
        log "Error: python3 is not installed. Please install python3 and try again."
        exit 1
    fi
    
    check_python_version
}

clone_repo() {
    log "Cloning the repository..."
    git clone https://github.com/kleer001/Text_Loom.git "$SCRIPT_DIR/Text_Loom"
    cd "$SCRIPT_DIR/Text_Loom" || exit 1
}



setup_venv() {
    log "Setting up virtual environment..."
    cd "$SCRIPT_DIR/Text_Loom" || {
        log "Error: Could not change to Text_Loom directory"
        exit 1
    }
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    log "Installing requirements..."
    if [ ! -f requirements.txt ]; then
        log "Error: requirements.txt not found in $(pwd)"
        exit 1
    fi
    pip install -r requirements.txt
    pip install -e .
}

create_launcher() {
    log "Creating text-loom launcher..."
    INSTALL_DIR="$SCRIPT_DIR/Text_Loom"
    cat > "$INSTALL_DIR/text-loom" << EOL
#!/bin/bash
echo "=== Text_Loom Launcher ==="
SCRIPT_PATH="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="\${SCRIPT_PATH}"
echo "Install directory: \$INSTALL_DIR"

echo "Activating virtual environment..."
source "\$INSTALL_DIR/.venv/bin/activate"

if [ -z "\$PYTHONPATH" ]; then
    export PYTHONPATH="\$INSTALL_DIR/src"
else
    # Remove any empty elements from PYTHONPATH
    CLEAN_PYTHONPATH=\$(echo "\$PYTHONPATH" | tr ':' '\n' | grep -v '^$' | tr '\n' ':' | sed 's/:$//')
    export PYTHONPATH="\$INSTALL_DIR/src:\$CLEAN_PYTHONPATH"
fi
echo "PYTHONPATH: \$PYTHONPATH"

echo "Changing to src directory..."
cd "\$INSTALL_DIR/src" || {
    echo "Error: Could not change to src directory"
    exit 1
}
echo "Current directory: \$(pwd)"

echo "Starting Text_Loom..."
python3 TUI/tui_skeleton.py "\$@"
EOL
    chmod +x "$INSTALL_DIR/text-loom"
    log "Launcher created at: $INSTALL_DIR/text-loom"
}

main() {
    setup_logging
    trap cleanup EXIT

    check_prerequisites
    clone_repo
    setup_venv
    create_launcher
    
    log "Installation complete!"
    echo -e "${MAGENTA}IF YOU WANT TO USE THE QUERY NODE THEN...${NC}"
    echo -e "${MAGENTA}PLEASE MAKE SURE YOUR LLM IS SETUP CORRECTLY!${NC}"
    echo -e "${BOLD} - - - - - - - - - - - - - - - - - - - -${NC}"
    echo -e "${CYAN}You can now run Text_Loom by executing:${NC}"
    echo -e "${CYAN}  ./text-loom${NC}"
    trap - EXIT
}

main