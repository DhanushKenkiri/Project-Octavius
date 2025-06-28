# Run ChargeX Backend Server for Windows PowerShell

Write-Host "Starting ChargeX Agent Backend Server..." -ForegroundColor Green

# Activate virtual environment if it exists
if (Test-Path -Path "venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    . .\venv\Scripts\Activate.ps1
}

# Run server
Write-Host "Running server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000
