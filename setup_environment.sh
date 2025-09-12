#!/bin/bash

# Harbor WebRTC Streaming Server - Environment Setup Script
# This script creates a conda environment and installs all dependencies

set -e  # Exit on any error

echo "🚀 Setting up Harbor WebRTC Streaming Environment"
echo "================================================="

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

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    print_error "Conda is not installed. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

print_status "Conda found: $(conda --version)"

# Check if environment already exists
ENV_NAME="harbor"
if conda info --envs | grep -q "^${ENV_NAME} "; then
    print_warning "Environment '${ENV_NAME}' already exists."
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing environment..."
        conda env remove -n ${ENV_NAME} -y
    else
        print_status "Using existing environment..."
    fi
fi

# Create or update environment
if conda info --envs | grep -q "^${ENV_NAME} "; then
    print_status "Updating existing environment from environment.yml..."
    conda env update -n ${ENV_NAME} -f environment.yml
else
    print_status "Creating new conda environment from environment.yml..."
    conda env create -f environment.yml
fi

print_success "Environment '${ENV_NAME}' is ready!"

# Activate environment and install additional pip dependencies
print_status "Activating environment and installing additional dependencies..."

# Source conda and activate environment
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}

# Verify Python installation
print_status "Python version: $(python --version)"
print_status "Pip version: $(pip --version)"

# Install any additional pip dependencies
print_status "Installing pip dependencies from requirements.txt..."
pip install -r requirements.txt

# Verify key imports
print_status "Verifying key dependencies..."

python -c "
import sys
import pkg_resources

# Check required packages
required_packages = [
    'aiohttp',
    'aiortc', 
    'av',
    'numpy'
]

missing_packages = []
for package in required_packages:
    try:
        pkg_resources.get_distribution(package)
        print(f'✅ {package}: OK')
    except pkg_resources.DistributionNotFound:
        missing_packages.append(package)
        print(f'❌ {package}: MISSING')

if missing_packages:
    print(f'\\n❌ Missing packages: {missing_packages}')
    sys.exit(1)
else:
    print('\\n✅ All required packages are installed!')
"

if [ $? -eq 0 ]; then
    print_success "All dependencies verified successfully!"
else
    print_error "Some dependencies are missing. Please check the output above."
    exit 1
fi

# Test import of Harbor modules
print_status "Testing Harbor module imports..."
python -c "
try:
    from harbor import create_app
    from harbor.led import LedController
    from harbor.video import CameraStreamTrack
    from harbor.webrtc import offer_handler
    from harbor.websocket import websocket_handler
    from harbor.client import index_handler
    print('✅ All Harbor modules imported successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Harbor modules test passed!"
else
    print_error "Harbor module imports failed."
    exit 1
fi

echo
print_success "🎉 Environment setup complete!"
echo
echo "To use the environment:"
echo "  conda activate ${ENV_NAME}"
echo
echo "To start the Harbor server:"
echo "  python app.py --host 0.0.0.0 --port 8080"
echo
echo "Then open your browser to: http://localhost:8080"
echo
print_warning "Note: This setup includes demo mode for testing without Pi hardware."
print_warning "For Raspberry Pi deployment, uncomment picamera2 and gpiozero in requirements.txt"
