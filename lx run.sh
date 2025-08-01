#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---
print_info() {
    echo "INFO: $1"
}

print_error() {
    echo "ERROR: $1" >&2
    exit 1
}

# --- Main Execution ---
VENV_DIR="venv"
PORT=8001 # The user requested port 8001

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    print_error "Virtual environment '$VENV_DIR' not found. Please run './setup.sh' first."
fi

# Activate the virtual environment
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if uvicorn is installed in the virtual environment
if ! command -v uvicorn &> /dev/null; then
    print_error "'uvicorn' command not found in the virtual environment. Make sure dependencies were installed correctly."
fi

print_info "Starting Uvicorn server on port $PORT..."
print_info "Access the application at http://localhost:$PORT"
print_info "Press Ctrl+C to stop the server."

# Run the uvicorn server
# We run it from the root directory to ensure the frontend is found.
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
