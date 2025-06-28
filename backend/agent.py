import os
import json
import time
import httpx
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

try:
    from eth_account import Account
    from x402.clients.httpx import x402HttpxClient
    from coinbase_agentkit import AgentKit, AgentKitConfig, CdpWalletProvider, CdpWalletProviderConfig
except ImportError:
    print("Warning: Required packages not found. Please install x402, eth-account, and coinbase-agentkit.")

# Load environment variables
load_dotenv()

class ChargeXAgent:
    """
    ChargeX Agent: An autonomous agent that manages EV charging with crypto micropayments
    """
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.http_client = httpx.Client(timeout=30.0)
        
        # CDP Wallet setup (would connect to real CDP wallet in production)
        self.setup_wallet()
        
        # Charging session state
        self.current_session = None
        self.active_station = None

    def setup_wallet(self):
        """Initialize CDP wallet for payment"""
        try:
            # In a real implementation, we would use actual CDP keys from environment
            cdp_key_id = os.getenv("CDP_API_KEY_ID", "")
            cdp_key_secret = os.getenv("CDP_API_KEY_SECRET", "")
            
            if cdp_key_id and cdp_key_secret:
                wallet_provider = CdpWalletProvider(CdpWalletProviderConfig(
                    api_key_id=cdp_key_id,
                    api_key_secret=cdp_key_secret,
                    network_id="base-sepolia"  # Use base-mainnet for production
                ))
                self.agent_kit = AgentKit(AgentKitConfig(wallet_provider=wallet_provider))
                print("CDP wallet provider initialized")
            else:
                # For demo, create a local private key (not secure for production)
                self.private_key = "0x" + os.urandom(32).hex()
                self.account = Account.from_key(self.private_key)
                print(f"Demo wallet created with address: {self.account.address}")
        except Exception as e:
            print(f"Warning: Wallet setup failed - {e}")
            # Fallback to simulated wallet
            self.private_key = "0x" + os.urandom(32).hex()
            self.account = Account.from_key(self.private_key)
            print(f"Simulated wallet created with address: {self.account.address}")

    def discover_stations(self) -> List[Dict[str, Any]]:
        """Discover nearby charging stations"""
        try:
            response = self.http_client.get(f"{self.api_url}/api/discover")
            response.raise_for_status()
            return response.json().get("stations", [])
        except Exception as e:
            print(f"Error discovering stations: {e}")
            return []

    def select_best_station(self, stations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the best charging station based on availability and price"""
        if not stations:
            return None
            
        # Filter available stations
        available_stations = [s for s in stations if s.get("available", False)]
        if not available_stations:
            return None
            
        # Sort by crypto rate (lowest first)
        sorted_stations = sorted(available_stations, key=lambda s: s.get("rate_crypto", float("inf")))
        return sorted_stations[0] if sorted_stations else None

    async def start_charging_session(self, station_id: str, amount_kwh: float = 10.0) -> Dict[str, Any]:
        """Initiate a charging session with the selected station"""
        try:
            response = self.http_client.post(
                f"{self.api_url}/api/charge/start",
                json={
                    "station_id": station_id,
                    "amount_kwh": amount_kwh,
                    "payment_method": "crypto"
                }
            )
            response.raise_for_status()
            session_data = response.json()
            self.current_session = session_data
            return session_data
        except Exception as e:
            print(f"Error starting charging session: {e}")
            return {"error": str(e)}

    async def handle_payment(self, session_id: str, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle crypto payment for charging session"""
        try:
            # In a real implementation, we'd use x402HttpxClient to handle payment
            # For demo purposes, we simulate the payment
            
            # With x402 and a real wallet, it would look like:
            # async with x402HttpxClient(account=self.account, base_url=self.api_url) as client:
            #     response = await client.post("/api/charge/payment", json={"session_id": session_id})
            #     return await response.json()
            
            # Simulation for demo:
            response = self.http_client.post(
                f"{self.api_url}/api/charge/payment",
                json={
                    "session_id": session_id,
                    "payment": {
                        "amount": payment_details["amount"],
                        "currency": payment_details["currency"],
                        "sender_address": getattr(self, "account", {}).address if hasattr(self, "account") else "0xSimulatedWalletAddress",
                        "recipient_address": payment_details["recipient_address"]
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error processing payment: {e}")
            return {"error": str(e)}

    async def monitor_charging_session(self, session_id: str) -> None:
        """Monitor a charging session until completion"""
        try:
            while True:
                response = self.http_client.get(f"{self.api_url}/api/charge/status/{session_id}")
                response.raise_for_status()
                status_data = response.json()
                
                print(f"Charging status: {status_data['status']}")
                print(f"Progress: {status_data['kwh_delivered']:.2f} kWh of {status_data['kwh_total']:.2f} kWh")
                
                if status_data["status"] == "completed":
                    print("Charging session completed!")
                    break
                    
                if status_data["status"] == "error":
                    print(f"Error in charging session: {status_data.get('error', 'Unknown error')}")
                    break
                    
                # Wait before next status check
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"Error monitoring charging session: {e}")

    async def full_charging_flow(self, desired_kwh: float = 10.0) -> Dict[str, Any]:
        """Run the complete charging flow from discovery to completion"""
        result = {
            "success": False,
            "logs": []
        }
        
        try:
            # Step 1: Discover charging stations
            result["logs"].append("Discovering charging stations...")
            stations = self.discover_stations()
            
            if not stations:
                result["logs"].append("No charging stations found.")
                return result
                
            result["logs"].append(f"Found {len(stations)} charging stations.")
            
            # Step 2: Select best station
            best_station = self.select_best_station(stations)
            if not best_station:
                result["logs"].append("No available charging stations.")
                return result
                
            self.active_station = best_station
            result["logs"].append(f"Selected station: {best_station['name']} ({best_station['rate_crypto']} USDC/kWh)")
            
            # Step 3: Start charging session
            result["logs"].append(f"Initiating charging session for {desired_kwh} kWh...")
            session_data = await self.start_charging_session(best_station["id"], desired_kwh)
            
            if "error" in session_data:
                result["logs"].append(f"Failed to start charging: {session_data['error']}")
                return result
                
            session_id = session_data["session_id"]
            result["logs"].append(f"Session initiated with ID: {session_id}")
            
            # Step 4: Handle payment if required
            if session_data["status"] == "awaiting_payment":
                payment_details = session_data["payment"]
                result["logs"].append(f"Payment required: {payment_details['amount']} {payment_details['currency']}")
                
                payment_result = await self.handle_payment(session_id, payment_details)
                
                if "error" in payment_result:
                    result["logs"].append(f"Payment failed: {payment_result['error']}")
                    return result
                    
                result["logs"].append(f"Payment successful. Transaction: {payment_result.get('tx_hash', 'N/A')}")
            
            # Step 5: Monitor charging session
            result["logs"].append("Monitoring charging progress...")
            await self.monitor_charging_session(session_id)
            
            # Success!
            result["success"] = True
            result["logs"].append("Charging flow completed successfully.")
            
        except Exception as e:
            result["logs"].append(f"Error in charging flow: {e}")
            
        return result

# If running directly, simulate a charging flow
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = ChargeXAgent()
        result = await agent.full_charging_flow(10.0)
        
        print("\n=== ChargeX Agent Results ===")
        for log in result["logs"]:
            print(log)
        print(f"Success: {result['success']}")
    
    asyncio.run(main())
