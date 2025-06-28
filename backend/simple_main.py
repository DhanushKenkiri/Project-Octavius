from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import random
import os
import time
import logging
from dotenv import load_dotenv

# Import our mock payment module and Bedrock agent
try:
    from payment import payment_manager
except ImportError:
    # Create a simple mock payment manager if payment module fails
    class MockPaymentManager:
        def get_payment_requirements(self, kwh_amount, station_id):
            return {
                "payment_id": f"pay-{random.randint(1000, 9999)}",
                "payment_required": {
                    "recipient": "0x1234567890abcdef1234567890abcdef12345678",
                    "network": "Base-Sepolia"
                },
                "payment_url": "mock://payment-url",
                "amount": round(kwh_amount * 0.25, 2),  # Mock USDC price
                "currency": "USDC"
            }
        
        def verify_payment(self, payment_data):
            return {
                "verified": True,
                "tx_hash": f"0x{os.urandom(32).hex()}"
            }
    
    payment_manager = MockPaymentManager()

try:
    from bedrock_rest_api import bedrock_agent
except ImportError:
    # Create a simple mock bedrock agent
    class MockBedrockAgent:
        def query(self, prompt, context=None):
            return {"response": "Mock bedrock response for demo purposes"}
    
    bedrock_agent = MockBedrockAgent()

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models for API requests and responses
class PaymentVerificationRequest(BaseModel):
    proof: Dict[str, Any]
    session_id: str

class ChargingSessionRequest(BaseModel):
    stationId: str
    amount: float = 10.0  # Default to 10 kWh
    wallet_address: Optional[str] = None

class WalletRequest(BaseModel):
    wallet_address: Optional[str] = None

class AgentQueryRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

# Mock data for the demo - Bangalore, India charging stations
stations = [
    {
        "id": "station-001", 
        "name": "ChargeX Indiranagar", 
        "lat": 12.9784,
        "lng": 77.6408, 
        "price": 20.5,
        "available": True,
        "location": "100 Feet Rd, Indiranagar, Bangalore",
        "rate_kwh": 20.5,
        "rate_crypto": 0.25,
        "power_kw": 150
    },
    {
        "id": "station-002", 
        "name": "ChargeX Whitefield Hub", 
        "lat": 12.9697,
        "lng": 77.7499, 
        "price": 22.0, 
        "available": True,
        "location": "ITPL Main Rd, Whitefield, Bangalore",
        "rate_kwh": 22.0,
        "rate_crypto": 0.27,
        "power_kw": 120
    },
    {
        "id": "station-003", 
        "name": "ChargeX Electronic City", 
        "lat": 12.8458,
        "lng": 77.6663, 
        "price": 19.5, 
        "available": False,
        "location": "Phase 1, Electronic City, Bangalore",
        "rate_kwh": 19.5,
        "rate_crypto": 0.24,
        "power_kw": 50
    },
    {
        "id": "station-004", 
        "name": "ChargeX Koramangala", 
        "lat": 12.9338,
        "lng": 77.6341, 
        "price": 21.0, 
        "available": True,
        "location": "80 Feet Rd, 4th Block, Koramangala, Bangalore",
        "rate_kwh": 21.0,
        "rate_crypto": 0.26,
        "power_kw": 100
    },
    {
        "id": "station-005", 
        "name": "ChargeX MG Road", 
        "lat": 12.9758,
        "lng": 77.6096, 
        "price": 23.5, 
        "available": True,
        "location": "MG Road, Central Bangalore",
        "rate_kwh": 23.5,
        "rate_crypto": 0.29,
        "power_kw": 200
    },
    {
        "id": "station-006", 
        "name": "ChargeX Hebbal", 
        "lat": 13.0365,
        "lng": 77.5963, 
        "price": 21.5, 
        "available": True,
        "location": "Bellary Road, Hebbal, Bangalore",
        "rate_kwh": 21.5,
        "rate_crypto": 0.26,
        "power_kw": 150
    },
    {
        "id": "station-007", 
        "name": "ChargeX Jayanagar", 
        "lat": 12.9299,
        "lng": 77.5933, 
        "price": 20.0, 
        "available": True,
        "location": "11th Main Rd, 4th Block, Jayanagar, Bangalore",
        "rate_kwh": 20.0,
        "rate_crypto": 0.24,
        "power_kw": 100
    }
]

transactions = [
    {"id": "tx-001", "station": "Downtown Supercharger", "date": "2025-06-25", "amount": 12.25, "energy": 35.0, "status": "completed"},
    {"id": "tx-002", "station": "West Side EV Station", "date": "2025-06-23", "amount": 9.50, "energy": 25.0, "status": "completed"},
    {"id": "tx-003", "station": "Bay Area Fast Charging", "date": "2025-06-20", "amount": 14.80, "energy": 37.0, "status": "completed"},
]

active_session = None
agent_logs = []

@app.get("/api/discover")
async def discover_stations():
    return {"stations": stations}

@app.post("/api/session/start")
async def start_session(data: ChargingSessionRequest):
    global active_session
    
    station_id = data.stationId
    station = next((s for s in stations if s["id"] == station_id), None)
    
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    if not station["available"]:
        raise HTTPException(status_code=400, detail="Station not available")
    
    # Generate payment requirements using x402
    kwh_estimate = data.amount    
    # Get payment requirements using our payment manager
    payment_req = payment_manager.get_payment_requirements(
        kwh_amount=kwh_estimate,
        station_id=station_id
    )
    
    # Generate session ID
    session_id = f"session-{random.randint(1000, 9999)}"
    
    active_session = {
        "id": session_id,
        "session_id": session_id,  # Added for compatibility with frontend
        "stationId": station_id,
        "stationName": station["name"],
        "startTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "price": station["price"],
        "paymentId": payment_req["payment_id"],
        "status": "awaiting_payment",  # Set to awaiting payment initially
        "currentEnergy": 0.0,
        "currentAmount": 0.0,
        "kwh_delivered": 0.0,  # Added for compatibility with frontend
        "kwh_total": kwh_estimate,  # Total kWh requested
        "time_elapsed": 0,  # Time elapsed in seconds
        "payment": {
            "requirements": payment_req["payment_required"],
            "payment_url": payment_req["payment_url"],
            "amount": payment_req["amount"],
            "currency": payment_req["currency"],
            "recipient": payment_req.get("payment_required", {}).get("recipient", "0x0"),
            "recipient_address": payment_req.get("payment_required", {}).get("recipient", "0x0"),
            "chain": payment_req.get("payment_required", {}).get("network", "Base-Sepolia")
        }
    }
    
    # Log agent activity
    agent_logs.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": "session_start",
        "details": f"Started charging session at {station['name']}"
    })
    
    return active_session

@app.get("/api/session/current")
async def get_current_session():
    if not active_session:
        raise HTTPException(status_code=404, detail="No active session")
        
    # Update session with simulated progress
    if active_session["status"] == "charging":
        # Calculate actual progress based on time elapsed
        # For demo purposes, we'll simulate progress such that a full charge takes about 3 hours
        # but speed up the simulation so updates are visible quickly
          # For a more dynamic demo, simulate elapsed time (1 second real time = 5 minutes simulation time)
        elapsed_increase = 300  # 5 minutes in seconds
        active_session["time_elapsed"] += elapsed_increase
        
        # Calculate power delivered - a 3 hour session should deliver the total kWh
        # So we deliver (total_kwh / 10800) * elapsed_seconds of energy
        kwh_rate = active_session["kwh_total"] / 10800  # kWh per second for a 3-hour session
        kwh_increase = kwh_rate * elapsed_increase
        
        # Update session values
        active_session["currentEnergy"] += kwh_increase
        active_session["kwh_delivered"] += kwh_increase
        active_session["currentAmount"] = round(active_session["kwh_delivered"] * active_session["price"], 2)
          # Ensure we don't exceed the total requested kWh
        if active_session["kwh_delivered"] >= active_session["kwh_total"]:
            active_session["kwh_delivered"] = active_session["kwh_total"]
            active_session["currentEnergy"] = active_session["kwh_total"]
            active_session["status"] = "completed"
            active_session["time_elapsed"] = 10800  # Set to exactly 3 hours (10800 seconds)
            active_session["endTime"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            # Add to transactions
            transactions.append({
                "id": f"tx-{random.randint(1000, 9999)}",
                "station": active_session["stationName"],
                "date": time.strftime("%Y-%m-%d", time.gmtime()),
                "amount": active_session["currentAmount"],
                "energy": active_session["currentEnergy"],
                "status": "completed"
            })
            
            # Log agent activity
            agent_logs.append({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "action": "session_complete",
                "details": f"Completed charging session at {active_session['stationName']}"
            })
    
    return active_session

@app.post("/api/session/stop")
async def stop_session():
    global active_session
    
    if not active_session:
        raise HTTPException(status_code=404, detail="No active session")
    
    active_session["status"] = "completed"
    active_session["endTime"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Add to transactions
    transactions.append({
        "id": f"tx-{random.randint(1000, 9999)}",
        "station": active_session["stationName"],
        "date": time.strftime("%Y-%m-%d", time.gmtime()),
        "amount": active_session["currentAmount"],
        "energy": active_session["currentEnergy"],
        "status": "completed"
    })
    
    # Log agent activity
    agent_logs.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": "session_stop",
        "details": f"Completed charging session at {active_session['stationName']}"
    })
    
    completed_session = active_session
    active_session = None
    
    return completed_session

@app.post("/api/payment/verify")
async def verify_payment(payment_data: PaymentVerificationRequest):
    """Verify a payment using x402 verification"""
    global active_session
    
    if not active_session or active_session["id"] != payment_data.session_id:
        raise HTTPException(status_code=404, detail="No active session with that ID found")
      # For the demo, always verify the payment successfully
    # In a real implementation, we would use the payment manager to verify
    verification_result = {
        "verified": True,
        "tx_hash": f"0x{os.urandom(32).hex()}"
    }
    
    if verification_result["verified"]:
        # Update the active session status
        active_session["status"] = "charging"
        active_session["payment"]["tx_hash"] = verification_result["tx_hash"]
        
        # Set the charging start time
        active_session["chargingStartTime"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        # For demo purposes, log that this is using Base Sepolia testnet
        logger.info("Demo payment verified on Base Sepolia testnet network")
        
        # Log the successful payment
        agent_logs.append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "action": "payment_verified",
            "details": f"Payment verified successfully: {verification_result['tx_hash']}"
        })
        
        # Immediately update the session with initial progress
        # This ensures the UI doesn't get stuck at 0% after payment
        active_session["time_elapsed"] = 60  # Initial 1 minute progress
        active_session["kwh_delivered"] = active_session["kwh_total"] * (60 / 10800)  # Initial kWh delivered
        active_session["currentEnergy"] = active_session["kwh_delivered"]
        active_session["currentAmount"] = round(active_session["kwh_delivered"] * active_session["price"], 2)
        
        return {
            "verified": True,
            "session": active_session,
            "tx_hash": verification_result["tx_hash"]
        }
    else:
        return {
            "verified": False,
            "error": verification_result.get("error", "Payment verification failed"),
            "session": active_session
        }

@app.get("/api/payments")
async def get_payments():
    """Get payment history"""
    return {"transactions": transactions}
    
@app.get("/api/wallet/info")
async def get_wallet_info(wallet_address: str = None):
    """Get CDP wallet information"""
    logger.info(f"Getting wallet info for address: {wallet_address}")
    wallet_info = payment_manager.get_wallet_info(wallet_address)
    return wallet_info

@app.post("/api/agent/query")
async def agent_query(data: AgentQueryRequest):
    """Send a query to the Amazon Bedrock agent"""
    # Call the Bedrock agent
    response = bedrock_agent.invoke_agent(
        prompt=data.prompt,
        session_id=data.session_id
    )
    
    # Log the agent interaction
    agent_logs.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": "agent_query",
        "details": f"User query: {data.prompt}"
    })
    
    return {
        "response": response["response"],
        "session_id": response["session_id"],
        "success": response["success"]
    }

@app.get("/api/agent/logs")
async def get_agent_logs():
    """Get all agent activity logs"""
    return {"logs": agent_logs}

@app.get("/api/agent/recommendation")
async def get_recommendation():
    """Get a charging recommendation from the agent"""
    location = {"lat": 37.7749, "lng": -122.4194}  # Default to San Francisco
    preferences = {"max_price": 0.40, "speed": "fast", "max_distance": 5}
    
    recommendation = bedrock_agent.get_charging_action(
        location=location, 
        battery_level=30,  # Default to 30%
        preferences=preferences
    )
    
    # Log the recommendation
    agent_logs.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": "charging_recommendation",
        "details": f"Agent recommended: {recommendation['action']} at {recommendation['station_id']}"
    })
    
    return recommendation

@app.post("/api/agent/monitor-session")
async def monitor_session():
    """Get a monitoring update from the agent for the current session"""
    if not active_session:
        raise HTTPException(status_code=404, detail="No active session")
    
    current_status = {
        "energy_delivered": active_session["currentEnergy"],
        "time_elapsed": 15,  # Mocked time elapsed
        "current_cost": active_session["currentAmount"],
        "charging_rate": 50  # kW
    }
    
    monitoring = bedrock_agent.monitor_charging_session(
        session_id=active_session["id"],
        current_status=current_status
    )
    
    # Log the monitoring
    agent_logs.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": "session_monitoring",
        "details": f"Agent advice: {monitoring['advice']}"
    })
    
    return monitoring

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)
