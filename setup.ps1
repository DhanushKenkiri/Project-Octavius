# ChargeX Agent Setup Script for Windows PowerShell

Write-Host "Setting up ChargeX Agent (Full Stack)..." -ForegroundColor Green

# Setup Backend
Write-Host "Setting up backend..." -ForegroundColor Green
cd backend

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8 or newer." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
. .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Return to root directory
cd ..

# Setup Frontend
Write-Host "Setting up frontend..." -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Please install Node.js 16 or newer." -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Green
npm install

Write-Host "Setup completed!" -ForegroundColor Green
Write-Host "To run the backend server: cd backend && python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan
Write-Host "To run the frontend: npm start" -ForegroundColor Cyan
