#!/bin/bash
set -e

echo "==================================================="
echo "  Building Vortex BitTorrent Client for Linux"
echo "==================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Generate logo.ico if it doesn't exist
if [ ! -f "resources/logo.ico" ]; then
    echo "Generating logo.ico..."
    python3 -c "from PIL import Image; Image.open('resources/logo.png').save('resources/logo.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])"
fi

# Build the executables using PyInstaller
echo "Building executables..."
pyinstaller --clean vortex.spec

echo
echo "==================================================="
echo "  Build Successful!"
echo "  Executables are located in the 'dist' directory:"
echo "    - dist/Vortex      (GUI)"
echo "    - dist/Vortex-CLI  (CLI)"
echo "==================================================="
echo
