"""
Amazon Bedrock REST API integration for ChargeX Agent
This module handles the communication with Amazon Bedrock using direct REST API calls
"""

import boto3
import json
import os
import logging
import requests
import uuid
from typing import Dict, Any, Optional, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockAgent:
    """
    Class to handle Amazon Bedrock Agent integrations via REST API
    """
    def __init__(self):
        """Initialize the Bedrock agent with credentials from environment variables"""
        self.region = os.getenv("BEDROCK_REGION", "ap-south-1")
        self.agent_id = os.getenv("BEDROCK_AGENT_ID", "DEMOAGENTID")
        self.agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
        self.api_key = os.getenv("BEDROCK_API_KEY", "")
        self.endpoint = os.getenv("BEDROCK_ENDPOINT", "https://2ymatsf0jk.execute-api.ap-south-1.amazonaws.com/prod")
        
        # Set up AWS session if AWS credentials are available
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            self.session = boto3.Session(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
                region_name=self.region
            )
            
            # Initialize Bedrock clients
            self.bedrock = self.session.client('bedrock-runtime')
            self.bedrock_agent = self.session.client('bedrock-agent-runtime')
            self.using_boto = True
            logger.info("BedrockAgent initialized with boto3")
        else:
            # We'll use direct REST API calls with the API key
            self.using_boto = False
            logger.info("BedrockAgent initialized with direct REST API")

    def invoke_agent(self, prompt: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Invoke the Bedrock agent using the provided prompt and return the response
        
        Args:
            prompt: The user prompt to process
            session_id: Optional session ID for continuing conversations
            
        Returns:
            Dictionary containing the agent response
        """
        try:
            # If no session ID provided, create a new session
            if session_id is None:
                session_id = str(uuid.uuid4())
            
            if self.using_boto:
                # Use boto3 client
                response = self.bedrock_agent.invoke_agent(
                    agentId=self.agent_id,
                    agentAliasId=self.agent_alias_id,
                    sessionId=session_id,
                    inputText=prompt
                )
                
                # Process the response
                completion = ""
                for event in response["completion"]:
                    if "chunk" in event:
                        completion += event["chunk"]["bytes"].decode('utf-8')
                        
                return {
                    "response": completion,
                    "session_id": session_id,
                    "success": True
                }
            else:
                # Use direct REST API call
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key
                }
                
                payload = {
                    "inputText": prompt,
                    "sessionId": session_id,
                    "agentAliasId": self.agent_alias_id,
                    "enableTrace": True
                }
                
                url = f"{self.endpoint}/agents/{self.agent_id}/aliases/{self.agent_alias_id}/sessions/{session_id}/text"
                
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": result.get("completion", "No response from agent"),
                        "session_id": session_id,
                        "success": True
                    }
                else:
                    logger.error(f"Error from Bedrock API: {response.status_code} - {response.text}")
                    return {
                        "response": f"Error: API returned status code {response.status_code}",
                        "success": False
                    }
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock agent: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "success": False
            }
    
    def get_charging_action(self, location: Dict[str, float], battery_level: float, 
                           preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use the Bedrock agent to determine the best charging action based on location,
        battery level, and user preferences.
        
        Args:
            location: Dict with lat and lng coordinates
            battery_level: Current battery level percentage
            preferences: User preferences for charging
            
        Returns:
            Dictionary containing agent's recommendation
        """
        # Construct a prompt for the agent
        prompt = f"""
        I need to charge my EV. Here's my current situation:
        - Current location: Latitude {location['lat']}, Longitude {location['lng']}
        - Current battery level: {battery_level}%
        - Max price willing to pay: ${preferences.get('max_price', 0.40)}/kWh
        - Preferred charging speed: {preferences.get('speed', 'fast')}
        - Maximum distance willing to travel: {preferences.get('max_distance', 5)} miles
        
        What's the optimal charging strategy? Consider availability, price, and convenience.
        """
        
        # Invoke the agent
        response = self.invoke_agent(prompt)
        
        # For demo purposes, if we don't have a real agent, provide a simulated response
        if not response["success"] or not self.agent_id:
            return self._simulated_charging_response(location, battery_level, preferences)
            
        return {
            "action": "charge",
            "station_id": "station-001",  # Extract this from the agent response in real implementation
            "reasoning": response["response"],
            "estimated_cost": 12.50,
            "estimated_time": 35
        }
    
    def monitor_charging_session(self, session_id: str, current_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use the Bedrock agent to monitor and provide insights during a charging session
        
        Args:
            session_id: The ID of the current charging session
            current_status: The current status of the charging session
            
        Returns:
            Dictionary containing agent's recommendation
        """
        # Construct a prompt for the agent
        prompt = f"""
        I'm currently charging my EV. Here's the current status:
        - Session ID: {session_id}
        - Current energy delivered: {current_status.get('energy_delivered', 0)} kWh
        - Time elapsed: {current_status.get('time_elapsed', 0)} minutes
        - Current cost: ${current_status.get('current_cost', 0)} 
        - Charging rate: {current_status.get('charging_rate', 0)} kW
        
        Should I continue charging or stop now? Please provide advice.
        """
        
        # Invoke the agent
        response = self.invoke_agent(prompt)
        
        # For demo purposes, if we don't have a real agent, provide a simulated response
        if not response["success"] or not self.agent_id:
            return self._simulated_monitoring_response(session_id, current_status)
            
        return {
            "action": "continue",
            "reasoning": response["response"],
            "estimated_remaining_time": 15,
            "advice": "Continue charging to reach optimal battery level."
        }
    
    def _simulated_charging_response(self, location: Dict[str, float], battery_level: float, 
                                    preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a simulated charging recommendation for demo purposes"""
        return {
            "action": "charge",
            "station_id": "station-001",
            "reasoning": f"Based on your battery level of {battery_level}% and location, I recommend the Downtown Supercharger which has good availability and a rate of $0.35/kWh.",
            "estimated_cost": 12.50,
            "estimated_time": 35
        }
    
    def _simulated_monitoring_response(self, session_id: str, current_status: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a simulated monitoring recommendation for demo purposes"""
        energy_delivered = current_status.get('energy_delivered', 0)
        
        if energy_delivered >= 30:
            action = "stop"
            advice = "You've charged enough for your needs. I recommend stopping now to optimize cost."
        else:
            action = "continue"
            advice = "Continue charging to reach optimal battery level for your journey."
        
        return {
            "action": action,
            "reasoning": f"Analyzed your charging session {session_id}.",
            "estimated_remaining_time": max(0, 40 - current_status.get('time_elapsed', 0)),
            "advice": advice
        }

# Create a singleton instance
bedrock_agent = BedrockAgent()
