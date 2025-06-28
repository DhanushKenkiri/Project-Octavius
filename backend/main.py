from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
import os
import time
from dotenv import load_dotenv
import boto3
import random
from bedrock_rest_api import BedrockAgent

# X402 imports
try:
    from x402.types import PaymentRequirements, PaymentRequiredResponse
    from x402.encoding import safe_base64_decode
except ImportError:
    print("Warning: x402 not found. Some features will be unavailable.")

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Bedrock agent
bedrock_agent = BedrockAgent()

# Simulated data - Bangalore charging stations
charging_stations = [
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
    }
]

# Simulated charging sessions
active_sessions = {}
payment_history = []

class ChargingStartRequest(BaseModel):
    station_id: str
    amount_kwh: Optional[float] = 10.0  # Default to 10 kWh
    payment_method: Optional[str] = "crypto"  # 'crypto' or 'card'

class AgentActionRequest(BaseModel):
    query: str = ""
    action_type: str = "general_query"  # charging_recommendation, monitor_session, general_query
    session_id: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    battery_level: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = None
    session_status: Optional[Dict[str, Any]] = None

@app.get("/api/discover")
async def discover_stations():
    """Return list of available charging stations"""
    return {"stations": charging_stations}

@app.post("/api/charge/start")
async def start_charging(request: ChargingStartRequest):
    """Initiate charging session with payment required"""
    # Find the requested charging station
    station = next((s for s in charging_stations if s["id"] == request.station_id), None)
    if not station:
        raise HTTPException(status_code=404, detail="Charging station not found")
    
    if request.payment_method == "crypto":
        # Simulate X402 payment required response
        session_id = f"session-{int(time.time())}"
        active_sessions[session_id] = {
            "station_id": station["id"],
            "start_time": None,  # Will be set when payment confirmed
            "status": "awaiting_payment",
            "kwh_delivered": 0,
            "amount_kwh": request.amount_kwh,
            "rate_crypto": station["rate_crypto"],
            "power_kw": station["power_kw"],
            "payment_required": station["rate_crypto"] * request.amount_kwh
        }
        
        # In a real implementation, we would use x402 middleware here
        # For mock, we'll return the payment details directly
        return {
            "session_id": session_id,
            "status": "awaiting_payment",
            "payment": {
                "amount": round(station["rate_crypto"] * request.amount_kwh, 2),
                "currency": "USDC",
                "recipient_address": "0xSimulatedStationWalletAddress",
                "chain": "base-sepolia",
                "scheme": "exact",
                "token_address": "0xSimulatedUSDCContractAddress"
            }
        }
    else:
        # Traditional credit card payment flow
        session_id = f"session-{int(time.time())}"
        active_sessions[session_id] = {
            "station_id": station["id"],
            "start_time": time.time(),
            "status": "charging",
            "kwh_delivered": 0,
            "amount_kwh": request.amount_kwh,
            "rate_kwh": station["rate_kwh"],
            "power_kw": station["power_kw"]
        }
        return {"session_id": session_id, "status": "charging"}

@app.post("/api/charge/payment")
async def process_payment(request: Request):
    """Simulate X402 payment processing"""
    data = await request.json()
    session_id = data.get("session_id")
    payment_data = data.get("payment", {})
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    if session["status"] != "awaiting_payment":
        raise HTTPException(status_code=400, detail="Session not awaiting payment")
    
    # Record the payment
    tx_hash = f"0x{os.urandom(32).hex()}"  # Simulated transaction hash
    payment = {
        "amount": session["payment_required"],
        "currency": "USDC",
        "timestamp": time.time(),
        "tx_hash": tx_hash,
        "session_id": session_id
    }
    payment_history.append(payment)
    
    # Update session status
    session["status"] = "charging"
    session["start_time"] = time.time()
    
    return {
        "status": "payment_accepted",
        "tx_hash": tx_hash
    }

@app.get("/api/charge/status/{session_id}")
async def get_charging_status(session_id: str):
    """Get current status of charging session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] == "charging":
        # Calculate charging progress
        elapsed_time = time.time() - session["start_time"]
        kwh_per_second = session["power_kw"] / 3600
        kwh_delivered = min(elapsed_time * kwh_per_second, session["amount_kwh"])
        
        session["kwh_delivered"] = round(kwh_delivered, 2)
        
        if kwh_delivered >= session["amount_kwh"]:
            session["status"] = "completed"
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "kwh_delivered": session["kwh_delivered"],
        "kwh_total": session["amount_kwh"],
        "time_elapsed": time.time() - session.get("start_time", time.time()) if session.get("start_time") else 0
    }

@app.get("/api/payments")
async def get_payment_history():
    """Get history of payments"""
    return {"payments": payment_history}

@app.post("/api/agent/action")
async def agent_action(request: AgentActionRequest):
    """Process agent actions using Amazon Bedrock"""
    try:
        if request.action_type == "charging_recommendation":
            # Use the Bedrock agent to get charging recommendations
            response = bedrock_agent.get_charging_action(
                location=request.location,
                battery_level=request.battery_level,
                preferences=request.preferences or {}
            )
        elif request.action_type == "monitor_session":
            # Monitor an ongoing charging session
            response = bedrock_agent.monitor_charging_session(
                session_id=request.session_id,
                current_status=request.session_status or {}
            )
        else:
            # For general queries, use a direct prompt            response = bedrock_agent.invoke_agent(prompt=request.query)
            
        # For fallback or if Bedrock is unavailable/unsuccessful
        if "response" not in response or not response.get("success", False):
            # Mock response for now
            time.sleep(1)  # Simulate processing time
            
            keywords = request.query.lower()
            if "find" in keywords and "station" in keywords:
                return {
                    "action": "find_station",
                    "response": "I've located 2 charging stations nearby. Would you like me to select the most economical option?",
                    "stations": charging_stations
                }
            elif "start" in keywords and "charging" in keywords:
                return {
                    "action": "start_charging",
                    "response": "I'll initiate a charging session at the selected station. Based on your vehicle's battery status, I recommend charging 10 kWh.",
                    "suggested_amount": 10.0
                }
            elif "payment" in keywords or "pay" in keywords:                return {
                    "action": "handle_payment",
                    "response": "I'll process the payment using your CDP wallet with USDC. Current rate is 0.05 USDC per kWh.",
                }
            else:
                return {
                    "action": "general_response",
                    "response": "I'm your ChargeX Agent. I can help you find charging stations, initiate charging sessions, and handle payments automatically."
                }
        
        # If we have a valid Bedrock response, return it
        return response
            
    except Exception as e:
        print(f"Error processing agent action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
