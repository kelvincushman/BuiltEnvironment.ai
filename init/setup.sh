#!/bin/bash

# BuiltEnvironment.ai Setup Script
# This script initializes the development environment

set -e

echo "========================================="
echo "BuiltEnvironment.ai Setup"
echo "========================================="

# Check for required tools
echo "Checking for required tools..."

command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required but not installed. Aborting." >&2; exit 1; }

echo "✓ Required tools found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
if [ -f "init/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r init/requirements.txt
    echo "✓ Python dependencies installed"
fi

# Install Node dependencies
if [ -f "package.json" ]; then
    echo "Installing Node dependencies..."
    npm install
    echo "✓ Node dependencies installed"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f "init/env.example" ]; then
        echo "Creating .env file from template..."
        cp init/env.example .env
        echo "✓ .env file created - please configure it with your credentials"
    fi
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure your .env file with API keys and credentials"
echo "2. Review init/config.yaml for system configuration"
echo "3. Run 'source venv/bin/activate' to activate the environment"
echo ""
