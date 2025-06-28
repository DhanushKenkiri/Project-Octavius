# 🏗️ Project Structure

```
Project-Octavius/
├── 📁 backend/                     # Python FastAPI Backend
│   ├── 🐍 simple_main.py          # Main FastAPI server
│   ├── 🤖 agent.py                # Legacy agent module
│   ├── 🤖 bedrock_agent.py        # Amazon Bedrock integration
│   ├── 🌐 bedrock_rest_api.py     # Bedrock REST API handler
│   ├── 💳 payment.py              # x402 & CDP wallet integration
│   ├── 📋 requirements.txt        # Python dependencies
│   ├── ⚙️ .env                    # Environment configuration
│   ├── 🔧 install_deps.sh         # Dependency installer
│   └── 🚀 run_server.sh           # Server startup script
│
├── 📁 src/                         # React Frontend Source
│   ├── 📁 components/              # Reusable React Components
│   │   └── 🧭 Navigation.tsx      # Main navigation component
│   │
│   ├── 📁 pages/                   # Main Application Pages
│   │   ├── 🏠 Dashboard.tsx       # Main dashboard view
│   │   ├── 🗺️ ChargerMap.tsx      # Interactive station map
│   │   ├── ⚡ ChargingSession.tsx  # Charging flow & monitoring
│   │   ├── 💰 PaymentHistory.tsx  # Transaction history
│   │   └── 🤖 AgentConsole.tsx    # AI agent chat interface
│   │
│   ├── 🎨 App.tsx                 # Main React application
│   ├── 🚀 index.tsx               # Application entry point
│   └── 📱 App.css                 # Global styles
│
├── 📁 public/                      # Static Assets
│   ├── 🖼️ index.html              # HTML template
│   ├── 🎯 favicon.ico             # App icon
│   └── 📋 manifest.json           # PWA manifest
│
├── 📋 package.json                 # Frontend dependencies & scripts
├── 📋 package-lock.json            # Locked dependency versions
├── 📚 README.md                    # Project documentation
├── 🚫 .gitignore                   # Git ignore rules
├── 🔧 setup.bat                    # Windows setup script
├── 🔧 setup.sh                     # Unix setup script
└── ⚙️ .env                        # Frontend environment variables

```

## 📁 Directory Descriptions

### 🔙 Backend (`/backend/`)
**Python FastAPI server handling AI agents, payments, and blockchain integration**

- `simple_main.py` - Main FastAPI application with all API endpoints
- `bedrock_agent.py` - Amazon Bedrock AI agent integration  
- `payment.py` - Coinbase x402 and CDP wallet payment processing
- `requirements.txt` - All Python dependencies (FastAPI, boto3, x402, etc.)

### 🎨 Frontend (`/src/`)
**React + TypeScript application with Material-UI components**

#### Pages:
- **Dashboard** - Overview of charging stations, battery status, wallet balance
- **ChargerMap** - Interactive map of Bangalore charging stations
- **ChargingSession** - Step-by-step charging flow with payment integration
- **PaymentHistory** - Transaction history and wallet management
- **AgentConsole** - AI-powered chat interface using Amazon Bedrock

#### Components:
- **Navigation** - Main app navigation with routing

## 🚀 Getting Started

### Quick Start (Windows)
```bash
# Run setup script
setup.bat

# Start backend (Terminal 1)
cd backend
python simple_main.py

# Start frontend (Terminal 2)  
npm start
```

### Quick Start (Unix/Linux/Mac)
```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Start backend (Terminal 1)
cd backend  
python simple_main.py

# Start frontend (Terminal 2)
npm start
```

## 🌟 Key Features by File

| File | Primary Features |
|------|------------------|
| `ChargerMap.tsx` | 🗺️ Station discovery, interactive map, Bangalore locations |
| `ChargingSession.tsx` | ⚡ 3-hour charging simulation, x402 payments, progress tracking |
| `AgentConsole.tsx` | 🤖 Bedrock AI chat, natural language queries, smart responses |
| `Dashboard.tsx` | 📊 Overview, quick actions, station listings |
| `PaymentHistory.tsx` | 💰 Transaction history, wallet management, USDC tracking |
| `simple_main.py` | 🔗 All API endpoints, session management, payment processing |
| `bedrock_agent.py` | 🧠 AI agent logic, AWS Bedrock integration |
| `payment.py` | 💳 x402 SDK, CDP wallet, Base Sepolia integration |

## 🔧 Configuration Files

- **`.env`** - AWS credentials, Coinbase keys, x402 config
- **`package.json`** - React dependencies, Material-UI, TypeScript
- **`requirements.txt`** - FastAPI, boto3, x402-python, web3

## 🎯 Ready for Hackathon Tracks

This structure supports multiple hackathon tracks:
- ✅ **DeFi & Tokenization** - Energy credit tokenization ready
- ✅ **Cross-Chain** - Base Sepolia + CCIP expansion ready  
- ✅ **Amazon Bedrock AI** - Full AI agent integration
- ✅ **Avalanche** - Multi-chain deployment ready
