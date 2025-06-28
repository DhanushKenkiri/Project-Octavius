# ChargeX Agent Backend Installation and Run Script for Windows
# Ensures proper installation of dependencies and starts the server

# Create and activate a virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv venv
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Run the setup script to install dependencies
Write-Host "Running setup script to install dependencies..." -ForegroundColor Green
python setup.py

# Check for x402 specifically
Write-Host "Checking for x402 SDK..." -ForegroundColor Green
python -c "try: import x402; print('x402 SDK found:', x402.__version__ if hasattr(x402, '__version__') else 'unknown'); except ImportError: print('x402 SDK not found - installing...'); exit(1)" 2>$null

# Install x402 directly if needed
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing x402 SDK directly..." -ForegroundColor Yellow
    pip install x402==0.1.2
    
    # Verify installation
    python -c "try: import x402; print('Successfully installed x402 SDK:', x402.__version__ if hasattr(x402, '__version__') else 'unknown'); except ImportError: print('Failed to install x402 SDK'); exit(1)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Failed to install x402 SDK. Payment verification will be simulated." -ForegroundColor Red
    }
}

# Check installed packages
Write-Host "Installed packages:" -ForegroundColor Cyan
pip list

# Start the server
Write-Host "Starting the server..." -ForegroundColor Green
Write-Host "API will be available at http://localhost:8000" -ForegroundColor Cyan
python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000
