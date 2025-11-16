#!/bin/bash
set -e

# Colors for output
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
BOLD='\033[1m'
NC='\033[0m'

# Installation directory
INSTALL_DIR="${INSTALL_DIR:-Text_Loom}"

# Functions
print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════╗"
    echo "║      Text Loom Installer v1.0        ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_python_version() {
    if ! command_exists python3; then
        print_error "python3 is not installed"
        echo "Please install Python 3.8 or higher and try again"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; ver = sys.version_info; print(f"{ver.major}.{ver.minor}")')
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
        print_error "Python 3.8+ required (found $PYTHON_VERSION)"
        exit 1
    fi
    print_success "Python $PYTHON_VERSION detected"
}

check_prerequisites() {
    print_step "Checking prerequisites..."

    if ! command_exists git; then
        print_error "git is not installed"
        echo "Please install git and try again"
        exit 1
    fi
    print_success "git found"

    check_python_version
}

clone_repo() {
    print_step "Cloning Text_Loom repository..."

    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory $INSTALL_DIR already exists"
        read -p "Remove and reinstall? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            print_error "Installation cancelled"
            exit 1
        fi
    fi

    if ! git clone https://github.com/kleer001/Text_Loom.git "$INSTALL_DIR"; then
        print_error "Failed to clone repository"
        exit 1
    fi
    print_success "Repository cloned"
}

setup_venv() {
    print_step "Setting up virtual environment..."

    cd "$INSTALL_DIR" || exit 1

    if ! python3 -m venv .venv; then
        print_error "Failed to create virtual environment"
        exit 1
    fi

    # shellcheck disable=SC1091
    source .venv/bin/activate

    print_step "Upgrading pip..."
    pip install --upgrade pip --quiet

    print_step "Installing dependencies..."
    if [ ! -f requirements.txt ]; then
        print_error "requirements.txt not found"
        exit 1
    fi

    if ! pip install -r requirements.txt --quiet; then
        print_error "Failed to install requirements"
        exit 1
    fi

    if ! pip install -e . --quiet; then
        print_error "Failed to install Text_Loom package"
        exit 1
    fi

    print_success "Dependencies installed"
}

create_activation_helper() {
    print_step "Creating activation helper..."

    cat > activate.sh << 'EOL'
#!/bin/bash
# Text_Loom activation helper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/.venv/bin/activate"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "Text_Loom environment activated!"
echo "Run: ./text_loom.py"
EOL

    chmod +x activate.sh
    print_success "Activation helper created"
}

print_next_steps() {
    echo
    echo -e "${MAGENTA}${BOLD}Installation Complete!${NC}"
    echo
    echo -e "${CYAN}To get started:${NC}"
    echo
    echo -e "  ${GREEN}cd $INSTALL_DIR${NC}"
    echo -e "  ${GREEN}source .venv/bin/activate${NC}"
    echo -e "  ${GREEN}export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src${NC}"
    echo -e "  ${GREEN}./text_loom.py${NC}              ${YELLOW}# Start GUI (default)${NC}"
    echo
    echo -e "${CYAN}Or use the quick start script:${NC}"
    echo
    echo -e "  ${GREEN}cd $INSTALL_DIR${NC}"
    echo -e "  ${GREEN}source activate.sh${NC}"
    echo -e "  ${GREEN}./text_loom.py${NC}"
    echo
    echo -e "${CYAN}Available interfaces:${NC}"
    echo -e "  ${GREEN}./text_loom.py -t${NC}           ${YELLOW}# Terminal UI${NC}"
    echo -e "  ${GREEN}./text_loom.py -r${NC}           ${YELLOW}# Python REPL${NC}"
    echo -e "  ${GREEN}./text_loom.py -g${NC}           ${YELLOW}# Web GUI${NC}"
    echo -e "  ${GREEN}./text_loom.py -b -f work.json${NC}  ${YELLOW}# Batch mode${NC}"
    echo
    echo -e "${MAGENTA}${BOLD}Remember to set up your LLM API keys if using Query nodes!${NC}"
    echo
}

# Main installation flow
main() {
    print_header
    check_prerequisites
    clone_repo
    setup_venv
    create_activation_helper
    print_next_steps
}

main