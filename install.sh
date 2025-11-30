#!/bin/bash
set -e

CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
BOLD='\033[1m'
NC='\033[0m'

INSTALL_DIR="${INSTALL_DIR:-Text_Loom}"

fail() {
    echo -e "${RED}✗${NC} $1" >&2
    exit 1
}

step() {
    echo -e "${GREEN}▶${NC} $1"
}

ok() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════╗"
    echo "║      Text Loom Installer v1.0        ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

require() {
    command -v "$1" >/dev/null 2>&1 || fail "$1 not found - install it and retry"
}

check_prerequisites() {
    step "Checking prerequisites..."
    require git
    ok "git found"
    require python3

    local version major minor
    version=$(python3 -c 'import sys; v=sys.version_info; print(f"{v.major}.{v.minor}")')
    major=${version%.*}
    minor=${version#*.}

    [ "$major" -ge 3 ] && [ "$minor" -ge 8 ] || fail "Python 3.8+ required (found $version)"
    ok "Python $version detected"
}

clone_repo() {
    step "Cloning Text_Loom repository..."

    if [ -d "$INSTALL_DIR" ]; then
        local timestamp
        timestamp=$(date +%Y%m%d_%H%M%S)
        warn "Directory exists - installing to ${INSTALL_DIR}_${timestamp}"
        INSTALL_DIR="${INSTALL_DIR}_${timestamp}"
    fi

    git clone https://github.com/kleer001/Text_Loom.git "$INSTALL_DIR" || fail "Clone failed"
    ok "Repository cloned"
}

setup_venv() {
    step "Setting up virtual environment..."

    cd "$INSTALL_DIR" || fail "Cannot cd to $INSTALL_DIR"
    python3 -m venv .venv || fail "venv creation failed"

    # shellcheck disable=SC1091
    source .venv/bin/activate

    step "Upgrading pip..."
    pip install --upgrade pip --quiet

    step "Installing dependencies..."
    [ -f requirements.txt ] || fail "requirements.txt not found"
    pip install -r requirements.txt --quiet || fail "Dependency install failed"
    pip install -e . --quiet || fail "Package install failed"

    ok "Dependencies installed"
}

create_activation_helper() {
    step "Creating activation helper..."

    cat > activate.sh << 'EOL'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
echo "Text_Loom environment activated!"
echo "Run: ./text_loom"
EOL

    chmod +x activate.sh
    ok "Activation helper created"
}

next_steps() {
    echo
    echo -e "${MAGENTA}${BOLD}Installation Complete!${NC}"
    echo
    echo -e "${CYAN}Quick start:${NC}"
    echo -e "  ${GREEN}cd $INSTALL_DIR && source activate.sh && ./text_loom${NC}"
    echo
    echo -e "${CYAN}Available modes:${NC}"
    echo -e "  ${GREEN}./text_loom -t${NC}  ${YELLOW}Terminal UI${NC}"
    echo -e "  ${GREEN}./text_loom -r${NC}  ${YELLOW}Python REPL${NC}"
    echo -e "  ${GREEN}./text_loom -g${NC}  ${YELLOW}Web GUI${NC}"
    echo -e "  ${GREEN}./text_loom -b${NC}  ${YELLOW}Batch mode${NC}"
    echo
    echo -e "${MAGENTA}${BOLD}Set up LLM API keys before using Query nodes${NC}"
    echo
}

main() {
    header
    check_prerequisites
    clone_repo
    setup_venv
    create_activation_helper
    next_steps
}

main