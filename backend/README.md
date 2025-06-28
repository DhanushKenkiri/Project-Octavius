# ChargeX Agent Backend

This backend implements a RESTful API for the ChargeX Agent demo, featuring integration with Coinbase's x402 for crypto micropayments and Amazon Bedrock for agent capabilities.

## Requirements

- Python 3.9 or newer
- x402 SDK (installed via pip)
- Coinbase Developer Platform SDK (if available)

## Installation

1. First, make sure you have Python 3.9+ installed on your system

2. Clone this repository and navigate to the backend directory:
   ```
   cd chargex-agent/backend
   ```

3. Run the setup script to install all dependencies:
   ```
   python setup.py
   ```
   
   The setup script will:
   - Check your Python version
   - Install all required packages from requirements.txt
   - Verify the x402 SDK installation
   - Verify the Coinbase Developer Platform SDK installation

## Configuration

Edit the `.env` file to configure your environment:

```
# ChargeX Agent Environment Variables

# Amazon Bedrock Configuration
BEDROCK_API_KEY="your-api-key"
BEDROCK_ENDPOINT="https://bedrock-runtime.us-east-1.amazonaws.com"
BEDROCK_REGION="us-east-1"
BEDROCK_AGENT_ID="your-agent-id" 
BEDROCK_AGENT_ALIAS_ID="your-agent-alias-id"

# Coinbase Developer Platform Configuration
COINBASE_API_KEY="your-coinbase-api-key"
COINBASE_API_SECRET="your-coinbase-api-secret"

# x402 Configuration
X402_VERIFICATION_KEY="your-x402-verification-key"

# Base Sepolia Testnet Configuration
NETWORK_RPC="https://sepolia.base.org"
NETWORK_CHAIN_ID=84532
NETWORK_NAME="Base-Sepolia"
TOKEN_CONTRACT="0x036CbD53842c5426634e7929541eC2318f3dCF7e" # USDC on Base Sepolia

# Charging Configuration
DEFAULT_CURRENCY="USDC"
CHARGING_RATE_PER_KWH=0.35
```

## Running the Server

Start the server using Uvicorn:

```bash
python -m uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Endpoints

- `/api/discover` - List available charging stations
- `/api/session/start` - Start a charging session
- `/api/session/current` - Get current session status
- `/api/session/stop` - Stop current charging session
- `/api/payment/verify` - Verify a payment using x402
- `/api/wallet/info` - Get wallet information
- `/api/agent/query` - Query the Bedrock agent
- `/api/agent/recommendation` - Get charging recommendations
- `/api/agent/monitor-session` - Monitor an active charging session

## Troubleshooting

If you encounter issues with the x402 SDK, ensure that:

1. You have the latest version of the SDK installed:
   ```
   pip install x402==0.1.2
   ```

2. Your Python environment matches the requirements in requirements.txt

3. You have set the X402_VERIFICATION_KEY in your .env file

4. Check the logs for detailed error messages

If the x402 SDK is not available, the application will fall back to simulated payment verification for demonstration purposes.
