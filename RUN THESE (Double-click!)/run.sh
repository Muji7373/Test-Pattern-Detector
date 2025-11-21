#!/bin/bash
# Easy launcher for Test Pattern Detector
# Just double-click or run: ./run.sh

clear

echo "========================================================================"
echo "           🔍 TEST PATTERN DETECTOR - EASY MODE"
echo "========================================================================"
echo ""
echo "Starting the easy-to-use interface..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Please install Python 3.7 or higher from python.org"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Make sure easy_tool.py is executable
chmod +x easy_tool.py 2>/dev/null

# Run the easy tool
python3 easy_tool.py

echo ""
echo "Thank you for using Test Pattern Detector!"
echo ""