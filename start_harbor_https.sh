#!/bin/bash

# Harbor WebRTC Streaming Server - HTTPS Startup Script
# This script starts the server with HTTPS support for production use

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
DEFAULT_PORT="8443"
DEFAULT_WIDTH="320"
DEFAULT_HEIGHT="240"
DEFAULT_FPS="15"
CERT_FILE="cert.pem"
KEY_FILE="key.pem"

# Parse command line arguments
HOST=${1:-$DEFAULT_HOST}
PORT=${2:-$DEFAULT_PORT}
WIDTH=${3:-$DEFAULT_WIDTH}
HEIGHT=${4:-$DEFAULT_HEIGHT}
FPS=${5:-$DEFAULT_FPS}

echo "🔒 Starting Harbor WebRTC Streaming Server (HTTPS)"
echo "=================================================="

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

# Check for SSL certificates
if [[ ! -f "$CERT_FILE" ]] || [[ ! -f "$KEY_FILE" ]]; then
    print_warning "SSL certificates not found. Generating self-signed certificates..."
    
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is required to generate certificates."
        print_status "Install OpenSSL or provide your own cert.pem and key.pem files."
        exit 1
    fi
    
    print_status "Generating self-signed certificate (for testing only)..."
    openssl req -x509 -newkey rsa:4096 -keyout "$KEY_FILE" -out "$CERT_FILE" -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Harbor/OU=Testing/CN=localhost"
    
    print_success "Self-signed certificates generated:"
    print_warning "⚠️  These are for TESTING ONLY. Use proper certificates in production!"
fi

print_status "Using certificates:"
echo "  Certificate: $CERT_FILE"
echo "  Private Key: $KEY_FILE"

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
print_status "HTTPS Server Configuration:"
echo "  Host: ${HOST}"
echo "  Port: ${PORT}"
echo "  Video: ${WIDTH}x${HEIGHT} @ ${FPS} fps"
echo "  SSL Certificate: ${CERT_FILE}"
echo "  SSL Private Key: ${KEY_FILE}"
echo

# Check if port is available
if command -v lsof &> /dev/null; then
    if lsof -i:${PORT} &> /dev/null; then
        print_warning "Port ${PORT} appears to be in use."
        print_status "Continuing anyway (may fail if port is blocked)..."
    fi
fi

# Start the server
print_status "Starting Harbor HTTPS server..."
print_success "Server will be available at: https://localhost:${PORT}"
print_warning "⚠️  You may need to accept the self-signed certificate in your browser"
print_status "Press Ctrl+C to stop the server"
echo

# Run the application with HTTPS
python app.py \
    --host "${HOST}" \
    --port "${PORT}" \
    --width "${WIDTH}" \
    --height "${HEIGHT}" \
    --fps "${FPS}" \
    --cert "${CERT_FILE}" \
    --key "${KEY_FILE}"
