#!/bin/bash

# ADO RAG Setup Script for Linux/Mac
# This script helps set up the development environment

echo "================================"
echo "  ADO RAG Setup Script"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "Found: $PYTHON_VERSION"

# Check if Python version is 3.10+
MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$MAJOR" -lt 3 ] || [ "$MAJOR" -eq 3 -a "$MINOR" -lt 10 ]; then
    echo "ERROR: Python 3.10 or higher is required"
    exit 1
fi

echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    read -p "Virtual environment already exists. Recreate? (y/N): " response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        rm -rf venv
        python3 -m venv venv
        echo "Virtual environment recreated"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo "pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "(This may take a few minutes)"
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "Dependencies installed successfully"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created"
    echo ""
    echo "IMPORTANT: Please edit .env file with your Azure credentials"
    echo "Required values:"
    echo "  - ADO_ORGANIZATION"
    echo "  - ADO_PROJECT_NAME"
    echo "  - ADO_PAT"
    echo "  - AZURE_OPENAI_ENDPOINT"
    echo "  - AZURE_OPENAI_KEY"
    echo "  - AZURE_SEARCH_ENDPOINT"
    echo "  - AZURE_SEARCH_KEY"
    echo ""
    read -p "Open .env file for editing now? (Y/n): " openEditor
    if [ "$openEditor" != "n" ] && [ "$openEditor" != "N" ]; then
        ${EDITOR:-nano} .env
    fi
else
    echo ".env file already exists"
fi

echo ""
echo "================================"
echo "  Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Ensure .env file is configured with your credentials"
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the application with:"
echo "   streamlit run app.py"
echo ""
echo "For detailed instructions, see QUICKSTART.md"
echo ""

# Offer to run the application
read -p "Would you like to run the application now? (y/N): " runNow
if [ "$runNow" = "y" ] || [ "$runNow" = "Y" ]; then
    echo ""
    echo "Starting ADO RAG application..."
    echo ""
    streamlit run app.py
fi
