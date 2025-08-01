#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---
print_info() {
    echo "INFO: $1"
}

print_success() {
    echo "SUCCESS: $1"
}

print_error() {
    echo "ERROR: $1" >&2
    exit 1
}

# --- Sanity Checks ---
print_info "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 and try again."
fi

print_info "Checking for pip..."
if ! command -v pip3 &> /dev/null; then
    # Some systems have pip installed as 'pip' instead of 'pip3'
    if ! command -v pip &> /dev/null; then
        print_error "pip is not installed. Please install pip for Python 3 and try again."
    fi
    PIP_COMMAND="pip"
else
    PIP_COMMAND="pip3"
fi

# --- Main Setup ---
VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    print_info "Virtual environment '$VENV_DIR' already exists. Skipping creation."
else
    print_info "Creating virtual environment in '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
fi

print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

print_info "Installing dependencies from requirements.txt..."
$PIP_COMMAND install -r requirements.txt

print_success "Setup complete!"
echo ""
print_info "To activate the virtual environment in your current shell, run:"
print_info "source $VENV_DIR/bin/activate"
echo ""
print_info "After activation, you can run the application using the 'run.sh' script:"
print_info "./run.sh"
