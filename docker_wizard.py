#!/usr/bin/env python3
"""
Text Loom Docker Setup Wizard

Interactive wizard to help configure and launch Text Loom in Docker.
Checks LLM connectivity, helps set up environment variables, and launches containers.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Add src to path for importing core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.findLLM import find_local_LLM, load_config
    FINDLLM_AVAILABLE = True
except ImportError:
    FINDLLM_AVAILABLE = False
    print("Warning: Could not import findLLM module")

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None


def check_docker_installation() -> Tuple[bool, bool]:
    """Check if Docker and Docker Compose are installed"""
    docker_installed = check_command_exists("docker")
    compose_installed = check_command_exists("docker-compose") or check_command_exists("docker") and check_command_exists("compose")
    return docker_installed, compose_installed


def detect_local_llms() -> List[str]:
    """Use findLLM to detect available local LLM services"""
    if not FINDLLM_AVAILABLE:
        print_warning("findLLM module not available, skipping auto-detection")
        return []

    try:
        # Temporarily suppress findLLM output
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            active_llm = find_local_LLM(choose=False)

        # Parse the output to get all detected LLMs
        output = f.getvalue()
        detected = []

        # Check config for all available LLM platforms
        config = load_config()
        for section in config.sections():
            if section != 'DEFAULT':
                detected.append(section)

        return detected
    except Exception as e:
        print_warning(f"Error detecting LLMs: {e}")
        return []


def get_user_choice(prompt: str, options: List[str], allow_back: bool = False) -> int:
    """Display numbered menu and get user choice"""
    print(f"\n{Colors.BOLD}{prompt}{Colors.ENDC}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    if allow_back:
        print(f"  0. Back to previous menu")

    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.ENDC}").strip()
            choice_num = int(choice)
            if allow_back and choice_num == 0:
                return 0
            if 1 <= choice_num <= len(options):
                return choice_num
            print_error(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n")
            sys.exit(0)


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no response from user"""
    default_str = "Y/n" if default else "y/N"
    while True:
        try:
            response = input(f"{Colors.BOLD}{prompt} [{default_str}]: {Colors.ENDC}").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print_error("Please enter 'y' or 'n'")
        except KeyboardInterrupt:
            print("\n")
            sys.exit(0)


def get_input(prompt: str, default: str = "", required: bool = False) -> str:
    """Get text input from user"""
    default_hint = f" [{default}]" if default else ""
    while True:
        try:
            response = input(f"{Colors.BOLD}{prompt}{default_hint}: {Colors.ENDC}").strip()
            if not response and default:
                return default
            if response or not required:
                return response
            print_error("This field is required")
        except KeyboardInterrupt:
            print("\n")
            sys.exit(0)


def setup_env_file(detected_llms: List[str]) -> Dict[str, str]:
    """Guide user through setting up .env file"""
    print_header("Environment Configuration")

    env_vars = {}

    # Check if .env already exists
    if os.path.exists(".env"):
        if get_yes_no("A .env file already exists. Do you want to modify it?", False):
            # Load existing values
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
        else:
            print_info("Using existing .env file")
            return env_vars

    # LLM Location selection
    llm_location_choice = get_user_choice(
        "Where will your LLM run?",
        [
            "Local LLM on my host machine (already running)",
            "Run Ollama inside Docker container",
            "Cloud API (OpenAI, Claude, Gemini, etc.)",
            "Skip configuration (I'll set this up later)"
        ]
    )

    if llm_location_choice == 1:
        # Local LLM on host
        print_info("\nNote: Docker will need to use 'host.docker.internal' to access your host machine")

        if detected_llms:
            print_success(f"\nDetected {len(detected_llms)} LLM platform(s) in settings.cfg:")
            for llm in detected_llms:
                print(f"  • {llm}")

            if len(detected_llms) == 1:
                selected_llm = detected_llms[0]
                if get_yes_no(f"\nUse {selected_llm}?", True):
                    env_vars["ACTIVE_LLM"] = selected_llm
                else:
                    env_vars["ACTIVE_LLM"] = get_input("Enter your LLM platform name", "Ollama")
            else:
                llm_choice = get_user_choice(
                    "Which LLM would you like to use?",
                    detected_llms + ["Other (enter manually)"]
                )
                if llm_choice <= len(detected_llms):
                    env_vars["ACTIVE_LLM"] = detected_llms[llm_choice - 1]
                else:
                    env_vars["ACTIVE_LLM"] = get_input("Enter your LLM platform name", "Ollama")
        else:
            print_info("No local LLMs detected. You can still configure manually.")
            env_vars["ACTIVE_LLM"] = get_input("Enter your LLM platform name", "Ollama")

        env_vars["LLM_MODEL"] = get_input("Enter your model name", "llama3:latest")
        print_warning("\nRemember to update src/core/settings.cfg after starting Docker:")
        print_info("  Change 'localhost' URLs to 'host.docker.internal'")

    elif llm_location_choice == 2:
        # Ollama in Docker
        print_info("The Ollama service will be enabled in docker-compose.yml")
        env_vars["ACTIVE_LLM"] = "Ollama"
        env_vars["LLM_MODEL"] = get_input("Enter model to use", "llama3:latest")
        env_vars["OLLAMA_IN_DOCKER"] = "true"
        print_info("\nAfter starting, you'll need to pull the model:")
        print(f"  docker exec -it textloom-ollama ollama pull {env_vars['LLM_MODEL']}")

    elif llm_location_choice == 3:
        # Cloud LLM
        cloud_choice = get_user_choice(
            "Which cloud LLM service?",
            ["OpenAI (ChatGPT)", "Anthropic (Claude)", "Perplexity", "Google (Gemini)"]
        )

        if cloud_choice == 1:
            env_vars["ACTIVE_LLM"] = "ChatGPT"
            env_vars["OPENAI_API_KEY"] = get_input("Enter your OpenAI API key", required=True)
            env_vars["LLM_MODEL"] = get_input("Enter model name", "gpt-4")
        elif cloud_choice == 2:
            env_vars["ACTIVE_LLM"] = "Claude"
            env_vars["ANTHROPIC_API_KEY"] = get_input("Enter your Anthropic API key", required=True)
            env_vars["LLM_MODEL"] = get_input("Enter model name", "claude-3-5-sonnet-20240620")
        elif cloud_choice == 3:
            env_vars["ACTIVE_LLM"] = "Perplexity"
            env_vars["PERPLEXITY_API_KEY"] = get_input("Enter your Perplexity API key", required=True)
            env_vars["LLM_MODEL"] = get_input("Enter model name", "pplx-7b-chat")
        elif cloud_choice == 4:
            env_vars["ACTIVE_LLM"] = "Gemini"
            env_vars["GOOGLE_API_KEY"] = get_input("Enter your Google API key", required=True)
            env_vars["LLM_MODEL"] = get_input("Enter model name", "gemini-1.5-pro")

    # Save .env file
    if env_vars:
        with open(".env", "w") as f:
            f.write("# Text Loom Docker Environment Configuration\n")
            f.write("# Generated by docker_wizard.py\n\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print_success(".env file created successfully")

    return env_vars


def check_and_modify_compose(env_vars: Dict[str, str]) -> bool:
    """Modify docker-compose.yml based on user choices"""
    if env_vars.get("OLLAMA_IN_DOCKER") == "true":
        print_info("Configuring docker-compose.yml to include Ollama service...")
        # Read the docker-compose.yml
        with open("docker-compose.yml", "r") as f:
            content = f.read()

        # Uncomment Ollama service
        content = content.replace("# ollama:", "ollama:")
        content = content.replace("#   image: ollama/ollama", "  image: ollama/ollama")
        content = content.replace("#   container_name:", "  container_name:")
        content = content.replace("#   ports:", "  ports:")
        content = content.replace('#     - "11434:11434"', '    - "11434:11434"')
        content = content.replace("#   volumes:", "  volumes:")
        content = content.replace("#     - ollama-data:", "    - ollama-data:")
        content = content.replace("#   restart:", "  restart:")
        content = content.replace("# ollama-data:", "ollama-data:")

        with open("docker-compose.yml", "w") as f:
            f.write(content)

        print_success("docker-compose.yml updated to include Ollama")
        return True
    return False


def start_docker_services(use_ollama: bool = False):
    """Start Docker containers"""
    print_header("Starting Docker Services")

    try:
        print_info("Building and starting containers...")
        cmd = ["docker-compose", "up", "-d", "--build"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print_success("Docker containers started successfully!")

            # If Ollama, offer to pull model
            if use_ollama:
                if get_yes_no("\nWould you like to pull an Ollama model now?", True):
                    model = get_input("Enter model name to pull", "llama3")
                    print_info(f"Pulling {model}... (this may take a while)")
                    pull_cmd = ["docker", "exec", "textloom-ollama", "ollama", "pull", model]
                    subprocess.run(pull_cmd)

            print("\n" + "="*60)
            print_success("Text Loom is now running!")
            print_info("Access the API at: http://localhost:8000")
            print_info("API Documentation: http://localhost:8000/api/v1/docs")
            print("\n" + "="*60)

            print_info("\nUseful commands:")
            print("  • View logs: docker-compose logs -f")
            print("  • Stop services: docker-compose down")
            print("  • Restart: docker-compose restart")

        else:
            print_error("Failed to start Docker containers")
            print(result.stderr)
            return False

    except Exception as e:
        print_error(f"Error starting Docker: {e}")
        return False

    return True


def main():
    """Main wizard flow"""
    print_header("Text Loom Docker Setup Wizard")
    print("This wizard will help you configure and launch Text Loom in Docker\n")

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Step 1: Check Docker installation
    print_header("Step 1: Checking Prerequisites")
    docker_ok, compose_ok = check_docker_installation()

    if not docker_ok:
        print_error("Docker is not installed or not in PATH")
        print_info("Please install Docker from: https://docs.docker.com/get-docker/")
        sys.exit(1)
    print_success("Docker is installed")

    if not compose_ok:
        print_error("Docker Compose is not installed")
        print_info("Please install Docker Compose from: https://docs.docker.com/compose/install/")
        sys.exit(1)
    print_success("Docker Compose is installed")

    # Step 2: Detect configured LLM platforms
    print_header("Step 2: Detecting LLM Platforms")
    print_info("Checking src/core/settings.cfg for configured LLM platforms...")

    detected_llms = detect_local_llms()

    if detected_llms:
        print_success(f"Found {len(detected_llms)} LLM platform(s) in configuration:")
        for llm in detected_llms:
            print(f"  • {llm}")
        print_info("\nThe wizard will help you select and configure one of these.")
    else:
        print_warning("Could not detect LLM platforms from settings.cfg")
        print_info("You can still configure manually or use cloud LLMs")

    # Step 3: Configuration
    print_header("Step 3: Configuration")

    config_choice = get_user_choice(
        "How would you like to proceed?",
        [
            "Quick start (use defaults, configure later)",
            "Custom configuration (guided setup)",
            "Exit wizard"
        ]
    )

    if config_choice == 3:
        print_info("Exiting wizard. You can run it again anytime with: python3 docker_wizard.py")
        sys.exit(0)

    env_vars = {}
    use_ollama_docker = False

    if config_choice == 2:
        # Custom configuration
        env_vars = setup_env_file(detected_llms)
        use_ollama_docker = env_vars.get("OLLAMA_IN_DOCKER") == "true"

        if use_ollama_docker:
            check_and_modify_compose(env_vars)
    else:
        # Quick start
        print_info("Using default configuration (Ollama on host machine)")
        print_info("You can customize later by editing .env and src/core/settings.cfg")

    # Step 4: Launch
    if get_yes_no("\nReady to launch Text Loom in Docker?", True):
        start_docker_services(use_ollama_docker)
    else:
        print_info("Setup complete. Start manually with: docker-compose up -d")

    print_info("\nFor help, see the README.md or visit: https://github.com/kleer001/Text_Loom")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
