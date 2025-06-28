#!/bin/bash
# Run ChargeX Backend Server for Linux/Mac

echo -e "\033[32mStarting ChargeX Agent Backend Server...\033[0m"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "\033[32mActivating virtual environment...\033[0m"
    source venv/bin/activate
fi

# Run server
echo -e "\033[36mRunning server on http://localhost:8000\033[0m"
echo -e "\033[33mPress Ctrl+C to stop the server\033[0m"
python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000
