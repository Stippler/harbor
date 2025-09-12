#!/bin/bash

# Harbor WebRTC Streaming Server - Startup Script
# This script activates the conda environment and starts the server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
ENV_NAME="harbor"
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8080"
DEFAULT_WIDTH="160"
DEFAULT_HEIGHT="120"
DEFAULT_FPS="30"

# Parse command line arguments
HOST=${1:-$DEFAULT_HOST}
PORT=${2:-$DEFAULT_PORT}
WIDTH=${3:-$DEFAULT_WIDTH}
HEIGHT=${4:-$DEFAULT_HEIGHT}
FPS=${5:-$DEFAULT_FPS}

echo "🌊 Starting Harbor WebRTC Streaming Server"
echo "=========================================="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    print_error "Conda is not installed. Please run setup_environment.sh first."
    exit 1
fi

# Check if environment exists
if ! conda info --envs | grep -q "^${ENV_NAME} "; then
    print_error "Environment '${ENV_NAME}' does not exist."
    print_status "Please run: ./setup_environment.sh"
    exit 1
fi

print_status "Activating conda environment: ${ENV_NAME}"

# Source conda and activate environment
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}

# Verify environment is active
if [[ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]]; then
    print_error "Failed to activate environment: ${ENV_NAME}"
    exit 1
fi

print_success "Environment activated: ${CONDA_DEFAULT_ENV}"

# Display configuration
print_status "Server Configuration:"
echo "  Host: ${HOST}"
echo "  Port: ${PORT}"
echo "  Video: ${WIDTH}x${HEIGHT} @ ${FPS} fps"
echo

# Check if port is available
if command -v lsof &> /dev/null; then
    if lsof -i:${PORT} &> /dev/null; then
        print_warning "Port ${PORT} appears to be in use."
        print_status "Continuing anyway (may fail if port is blocked)..."
    fi
fi

# Start the server
print_status "Starting Harbor server..."
print_success "Server will be available at: http://localhost:${PORT}"
print_status "Press Ctrl+C to stop the server"
echo

# Run the application
python app.py \
    --host "${HOST}" \
    --port "${PORT}" \
    --width "${WIDTH}" \
    --height "${HEIGHT}" \
    --fps "${FPS}"
