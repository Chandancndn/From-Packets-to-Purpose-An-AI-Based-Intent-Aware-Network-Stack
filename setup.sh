#!/bin/bash

# Intent-Aware Network Stack Setup Script
# This script sets up the entire project environment

set -e

echo "=========================================="
echo "Intent-Aware Network Stack Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux (required for QoS features)
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "Not running on Linux. QoS features (tc/iptables) will be simulated."
fi

# Check for required tools
print_info "Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_info "Python version: $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
print_info "Node.js version: $NODE_VERSION"

# Check for Wireshark/Tshark
if command -v tshark &> /dev/null; then
    print_info "Tshark is installed"
else
    print_warning "Tshark not found. Will use simulated packet capture."
    print_warning "To install: sudo apt-get install tshark (Ubuntu/Debian)"
    print_warning "           sudo yum install wireshark (RHEL/CentOS)"
    print_warning "           brew install wireshark (macOS)"
fi

echo ""
print_info "Setting up backend..."
echo "=========================================="

# Create virtual environment
if [ ! -d "backend/venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv backend/venv
fi

# Activate virtual environment
source backend/venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo ""
print_info "Setting up frontend..."
echo "=========================================="

# Install npm dependencies
cd frontend
if [ ! -d "node_modules" ]; then
    print_info "Installing npm packages..."
    npm install
fi
cd ..

echo ""
print_info "Creating model directory..."
mkdir -p models/trained_models

echo ""
print_info "Setup complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "  1. Start the backend:"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     python -m app.main"
echo ""
echo "  2. In a new terminal, start the frontend:"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "  3. Open your browser and navigate to:"
echo "     http://localhost:5173"
echo ""
echo "Or use Docker Compose (recommended):"
echo "     docker-compose up -d"
echo ""
echo "=========================================="