#!/bin/bash
# US Phone Number Generator - Build Script for Linux/Mac

echo ""
echo "============================================"
echo "US PHONE NUMBER GENERATOR - Build Script"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Install it using: sudo apt-get install python3"
    exit 1
fi

echo "[✓] Python found"
python3 --version
echo ""

# Install dependencies
echo "[*] Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[✓] Dependencies installed"
echo ""

# Clean previous builds
if [ -d "dist" ]; then
    echo "[*] Cleaning previous builds..."
    rm -rf dist build
    rm -f *.spec 2>/dev/null
fi

# Build the EXE
echo "[*] Building executable..."
echo "This may take a minute..."
echo ""

pyinstaller gui_app.spec

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed"
    exit 1
fi

echo ""
echo "============================================"
echo "[✓] BUILD SUCCESSFUL!"
echo "============================================"
echo ""
echo "Your executable is ready:"
echo "Location: dist/USPhoneNumberGenerator"
echo ""
echo "You can now run: ./dist/USPhoneNumberGenerator"
echo ""
