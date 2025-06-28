"""
Setup script for ChargeX Agent backend
Ensures proper installation of all dependencies including x402 and CDP SDKs
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        logger.error("Python 3.9 or newer is required")
        return False
    logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    return True

def install_requirements():
    """Install all required packages"""
    req_path = Path(__file__).parent / "requirements.txt"
    if not req_path.exists():
        logger.error("requirements.txt not found")
        return False
    
    logger.info("Installing dependencies from requirements.txt")
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_path)])
        logger.info("Successfully installed dependencies")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def verify_x402_installation():
    """Verify that x402 SDK is properly installed"""
    try:
        import x402
        from x402.types import PaymentRequirements
        logger.info(f"Successfully imported x402 SDK (version: {x402.__version__ if hasattr(x402, '__version__') else 'unknown'})")
        return True
    except ImportError as e:
        logger.error(f"Failed to import x402 SDK: {e}")
        logger.info("Attempting direct installation of x402...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "x402>=0.1.2"])
            import x402
            logger.info(f"Successfully installed and imported x402 SDK")
            return True
        except (subprocess.CalledProcessError, ImportError) as e:
            logger.error(f"Failed to install x402 SDK directly: {e}")
            return False

def verify_cdp_installation():
    """Verify that CDP SDK is properly installed"""
    try:
        import coinbase_wallet_sdk
        logger.info(f"Successfully imported Coinbase Wallet SDK")
        return True
    except ImportError:
        logger.warning("Coinbase Wallet SDK not available. Wallet operations will be simulated.")
        # This is not a critical failure as we can fall back to simulation
        return True

def setup():
    """Run the full setup process"""
    if not check_python_version():
        return False
    
    if not install_requirements():
        return False
    
    x402_ok = verify_x402_installation()
    cdp_ok = verify_cdp_installation()
    
    if x402_ok:
        logger.info("✅ x402 SDK setup successful")
    else:
        logger.warning("⚠️ x402 SDK setup incomplete - payment verification will be simulated")
    
    if cdp_ok:
        logger.info("✅ CDP setup successful or will be simulated")
    else:
        logger.warning("⚠️ CDP setup incomplete - wallet operations will be simulated")
    
    logger.info("Setup complete - run 'python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000' to start the server")
    return True

if __name__ == "__main__":
    setup()
