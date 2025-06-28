#!/bin/bash
# ChargeX Agent Backend Setup Script for Linux/Mac

echo -e "\033[32mSetting up ChargeX Agent Backend...\033[0m"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo -e "\033[32mFound Python: $(python3 --version)\033[0m"
else
    echo -e "\033[31mPython not found. Please install Python 3.8 or newer.\033[0m"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\033[32mCreating virtual environment...\033[0m"
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo -e "\033[32mActivating virtual environment...\033[0m"
source venv/bin/activate

# Upgrade pip
echo -e "\033[32mUpgrading pip...\033[0m"
pip install --upgrade pip

# Install dependencies
echo -e "\033[32mInstalling dependencies...\033[0m"
pip install -r requirements.txt

# Check for x402 package
if pip list | grep -q "x402"; then
    echo -e "\033[32mx402 package installed successfully!\033[0m"
else
    echo -e "\033[33mWarning: x402 package installation may have failed. Check errors above.\033[0m"
fi

echo -e "\033[32mSetup completed!\033[0m"
echo -e "\033[36mTo run the server, use: python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000\033[0m"
