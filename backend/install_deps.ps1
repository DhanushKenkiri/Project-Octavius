# ChargeX Agent Backend Setup Script for Windows PowerShell

Write-Host "Setting up ChargeX Agent Backend..." -ForegroundColor Green

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
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Check for x402 package
$x402Installed = pip list | Select-String "x402"
if ($x402Installed) {
    Write-Host "x402 package installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Warning: x402 package installation may have failed. Check errors above." -ForegroundColor Yellow
}

Write-Host "Setup completed!" -ForegroundColor Green
Write-Host "To run the server, use: python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan
