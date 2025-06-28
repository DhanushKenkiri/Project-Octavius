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

# Simulated data
charging_stations = [
    {
        "id": "station-1",
        "name": "ChargeX Station #1",
        "location": "123 Main St",
        "lat": 37.7749,
        "lng": -122.4194,
        "power_level": "Level 2",
        "available": True,
        "price_kwh": 0.35
    },
    {
        "id": "station-2",
        "name": "ChargeX Station #2",
        "location": "456 Market St",
        "lat": 37.7895,
        "lng": -122.3999,
        "power_level": "Level 3",
        "available": True,
        "price_kwh": 0.42
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
    """Start a charging session"""
    station = next((s for s in charging_stations if s["id"] == request.station_id), None)
    
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    if not station["available"]:
        raise HTTPException(status_code=400, detail="Station not available")
    
    session_id = f"session_{int(time.time())}"
    active_sessions[session_id] = {
        "id": session_id,
        "station_id": station["id"],
        "station_name": station["name"],
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "amount_kwh": request.amount_kwh,
        "price_kwh": station["price_kwh"],
        "total_cost": station["price_kwh"] * request.amount_kwh,
        "status": "initiated"
    }
    
    # For X402 payment flow
    if request.payment_method == "crypto":
        return {
            "session_id": session_id,
            "payment_required": True,
            "amount": station["price_kwh"] * request.amount_kwh,
            "currency": "USDC",
            "recipient": "0x1234567890abcdef1234567890abcdef12345678",
            "payment_url": f"/api/charge/{session_id}/pay"
        }
    else:
        # For card payment flow
        active_sessions[session_id]["status"] = "charging"
        return {
            "session_id": session_id,
            "status": "charging",
            "amount": station["price_kwh"] * request.amount_kwh,
            "start_time": active_sessions[session_id]["start_time"]
        }

@app.get("/api/charge/{session_id}")
async def get_charging_session(session_id: str):
    """Get status of a charging session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # Simulate charging progress
    if session["status"] == "charging":
        elapsed = time.time() - time.mktime(time.strptime(session["start_time"], "%Y-%m-%dT%H:%M:%SZ"))
        progress = min(1.0, elapsed / 1800)  # Assume charging takes 30 minutes
        
        session["progress"] = progress
        session["energy_delivered"] = progress * session["amount_kwh"]
        session["current_cost"] = progress * session["total_cost"]
        
        if progress >= 1.0:
            session["status"] = "completed"
            session["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            # Add to payment history
            payment_history.append({
                "id": f"payment_{int(time.time())}",
                "session_id": session_id,
                "amount": session["total_cost"],
                "currency": "USDC",
                "timestamp": session["end_time"],
                "station_name": session["station_name"]
            })
    
    return session

@app.post("/api/charge/{session_id}/x402/pay-required")
async def x402_payment_required(session_id: str, request: Request):
    """Handle X402 payment requirements"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # Simulate X402 payment requirements
    payment_req = PaymentRequirements(
        id="payment_req_" + session_id,
        amount=str(session["total_cost"]),
        memo=f"Charging at {session['station_name']}",
        recipient="0x1234567890abcdef1234567890abcdef12345678",
        required_confirmations=1,
    )
    
    return Response(
        content=json.dumps(payment_req.dict()),
        status_code=402,
        headers={"Content-Type": "application/json"},
    )

@app.post("/api/charge/{session_id}/x402/payment-callback")
async def x402_payment_callback(session_id: str, request: Request):
    """Handle X402 payment callback"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # In a real implementation, we would verify the payment here
    # For demo purposes, just update the session status
    session["status"] = "charging"
    session["start_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Add to payment history
    payment_history.append({
        "id": f"payment_{int(time.time())}",
        "session_id": session_id,
        "amount": session["total_cost"],
        "currency": "USDC",
        "timestamp": session["start_time"],
        "station_name": session["station_name"]
    })
    
    return {"status": "success", "session_id": session_id}

@app.post("/api/charge/{session_id}/stop")
async def stop_charging(session_id: str):
    """Stop a charging session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] != "charging":
        raise HTTPException(status_code=400, detail="Session is not in charging state")
    
    session["status"] = "completed"
    session["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Calculate final cost
    elapsed = time.time() - time.mktime(time.strptime(session["start_time"], "%Y-%m-%dT%H:%M:%SZ"))
    progress = min(1.0, elapsed / 1800)  # Assume charging takes 30 minutes
    session["energy_delivered"] = progress * session["amount_kwh"]
    session["final_cost"] = session["price_kwh"] * session["energy_delivered"]
    
    # Update payment history if needed
    for payment in payment_history:
        if payment["session_id"] == session_id:
            payment["amount"] = session["final_cost"]
    
    return session

@app.get("/api/payments")
async def get_payment_history():
    """Get payment history"""
    return {"payments": payment_history}

@app.post("/api/agent/action")
async def agent_action(request: AgentActionRequest):
    """Process agent actions using Amazon Bedrock"""
    try:
        # Initialize response to None
        response = None
        
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
            # For general queries, use a direct prompt
            response = bedrock_agent.invoke_agent(prompt=request.query)
        
        # For fallback or if Bedrock is unavailable/unsuccessful
        if not response or "response" not in response or not response.get("success", False):
            # Mock response for now
            time.sleep(1)  # Simulate processing time
            
            keywords = request.query.lower() if request.query else ""
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
            elif "payment" in keywords or "pay" in keywords:
                return {
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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
