# ChargeX Agent - Autonomous EV Charging Platform

<div align="center">

![ChargeX Agent](https://img.shields.io/badge/ChargeX-Agent-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-18.0-61dafb?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178c6?style=for-the-badge&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.9+-3776ab?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)

*An AI-powered autonomous EV charging platform combining Amazon Bedrock, Coinbase x402 micropayments, and CDP Wallet integration*

</div>

## 🚗⚡ Overview

ChargeX Agent is a cutting-edge autonomous EV charging platform that leverages modern AI and blockchain technologies to provide seamless electric vehicle charging experiences. The platform combines:

- **🤖 Amazon Bedrock AI Agents** for intelligent charging optimization
- **💰 Coinbase x402 SDK** for crypto micropayments  
- **🔗 CDP Wallet Integration** on Base Sepolia testnet
- **🗺️ Interactive Maps** for charging station discovery in Bangalore
- **⚡ Real-time Session Monitoring** with automated 3-hour charging cycles

## 🎯 Key Features

### 🗺️ **Interactive Station Discovery**
- Browse charging stations across Greater Bangalore
- Real-time availability and pricing information
- Interactive map with station details and navigation

### 🤖 **AI-Powered Agent**
- Amazon Bedrock-powered charging assistant
- Intelligent optimization recommendations  
- Natural language interaction for all charging needs

### 💳 **Seamless Crypto Payments**
- x402 SDK integration for USDC micropayments
- CDP Wallet support on Base Sepolia testnet
- Automated payment processing during charging

### ⚡ **Smart Charging Sessions**
- Automated 3-hour charging simulation
- Real-time progress monitoring
- Dynamic pricing based on demand and location

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Python Backend  │    │  AI & Blockchain│
│                 │    │                  │    │                 │
│ ├─ ChargerMap   │◄──►│ ├─ FastAPI       │◄──►│ ├─ Bedrock Agent│
│ ├─ ChargingFlow │    │ ├─ Session Mgmt  │    │ ├─ x402 SDK     │
│ ├─ AgentConsole │    │ ├─ Payment APIs  │    │ ├─ CDP Wallet   │
│ └─ PaymentUI    │    │ └─ Mock Data     │    │ └─ Base Sepolia │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.9+
- **Git** for version control

### 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DhanushKenkiri/Project-Octavius.git
   cd Project-Octavius
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd ..
   npm install
   ```

4. **Configure environment variables**
   ```bash
   # Copy example environment file
   cp backend/.env.example backend/.env
   
   # Edit with your API keys
   # - AWS Bedrock credentials
   # - Coinbase CDP API keys
   # - x402 configuration
   ```

### 🏃‍♂️ Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python simple_main.py
   ```
   Backend will be available at `http://localhost:8000`

2. **Start the frontend development server**
   ```bash
   npm start
   ```
   Frontend will be available at `http://localhost:3000`

## 🎮 Demo Walkthrough

### 1. **🗺️ Explore Charging Stations**
- Visit the **Map** page to see charging stations across Bangalore
- Click on station markers to view details and pricing
- Use search to filter stations by name or location

### 2. **⚡ Start a Charging Session**
- Select an available station from the map
- Initiate a **3-hour charging session** (45 kWh)
- Watch the automated payment flow with x402 integration

### 3. **💬 Interact with ChargeX Agent**
- Visit the **Agent Console** for AI-powered assistance
- Ask questions about charging, payments, or station recommendations
- Experience natural language interaction powered by Amazon Bedrock

### 4. **📊 Monitor Your Session**
- Real-time progress tracking with visual indicators
- Automatic session completion after simulated 3-hour charge
- Transaction history and payment records

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** for modern component design
- **React Router** for navigation
- **Axios** for API communication

### Backend  
- **FastAPI** for high-performance REST APIs
- **Python 3.9+** with async/await support
- **Pydantic** for data validation
- **CORS** enabled for frontend integration

### AI & Blockchain
- **Amazon Bedrock** for AI agent capabilities
- **Coinbase x402 SDK** for micropayments
- **CDP Wallet** integration
- **Base Sepolia** testnet for blockchain operations

## 🌟 Demo Features

> **Note**: This is a demonstration application showcasing the future of autonomous EV charging

- **🔄 Automated Payment Flow**: Simulated x402 USDC payments
- **🗺️ Interactive Maps**: Mock stations across Bangalore with realistic data
- **🤖 AI Assistant**: Bedrock-powered agent for charging optimization  
- **⚡ Real-time Updates**: Live session monitoring with progress tracking
- **📱 Responsive Design**: Works seamlessly on desktop and mobile

## 🔮 Future Roadmap

### Phase 1: Core Platform ✅
- [x] Basic charging station discovery
- [x] Payment flow simulation  
- [x] AI agent integration
- [x] Session management

### Phase 2: Blockchain Integration 🚧
- [ ] Real x402 payment processing
- [ ] CDP Wallet production integration
- [ ] Chainlink price feeds for dynamic pricing
- [ ] Energy credit tokenization

### Phase 3: Advanced Features 🔄
- [ ] Cross-chain payment support
- [ ] Real-time grid data integration
- [ ] Fleet management capabilities  
- [ ] Energy marketplace

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Amazon Bedrock** for AI agent capabilities
- **Coinbase** for x402 SDK and CDP Wallet tools
- **Base** for providing the Sepolia testnet infrastructure
- **Material-UI** for the excellent React component library

---

<div align="center">

**Built with ❤️ for the future of autonomous electric vehicle charging**

[🌐 Live Demo](#) | [📖 Documentation](#) | [🐛 Report Bug](#) | [💡 Request Feature](#)

</div>

## Demo Features

This demo provides a realistic simulation of the ChargeX Agent platform:

- **Interactive Map View**: Browse charging stations across Greater Bangalore with Google Maps integration
- **Automated 3-Hour Charging Sessions**: Initiate a charging session that simulates a full 3-hour charge
- **Simulated x402 Payments**: Experience the crypto payment flow using the USDC token on Base Sepolia testnet
- **Real-time Session Monitoring**: Watch as your charging session progresses with simulated data
- **Agent-assisted Workflow**: The entire charging experience is guided by the ChargeX Agent

## Project Structure

- `frontend/`: React + TypeScript application with Material UI
- `backend/`: Python FastAPI server with Bedrock agent integration and payment processing

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Google Maps API key (for production use)

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
