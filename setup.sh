#!/bin/bash
# ChargeX Agent Setup Script for Linux/Mac

echo -e "\033[32mSetting up ChargeX Agent (Full Stack)...\033[0m"

# Setup Backend
echo -e "\033[32mSetting up backend...\033[0m"
cd backend

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
echo -e "\033[32mInstalling backend dependencies...\033[0m"
pip install -r requirements.txt

# Return to root directory
cd ..

# Setup Frontend
echo -e "\033[32mSetting up frontend...\033[0m"

# Check if Node.js is installed
if command -v node &>/dev/null; then
    echo -e "\033[32mFound Node.js: $(node --version)\033[0m"
else
    echo -e "\033[31mNode.js not found. Please install Node.js 16 or newer.\033[0m"
    exit 1
fi

# Install frontend dependencies
echo -e "\033[32mInstalling frontend dependencies...\033[0m"
npm install

echo -e "\033[32mSetup completed!\033[0m"
echo -e "\033[36mTo run the backend server: cd backend && python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000\033[0m"
echo -e "\033[36mTo run the frontend: npm start\033[0m"
