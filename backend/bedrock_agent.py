import os
import json
import boto3
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class BedrockAgent:
    """
    Integration with Amazon Bedrock for AI capabilities in the ChargeX Agent
    """
    
    def __init__(self):
        # Initialize Bedrock client
        self.client = self._initialize_bedrock_client()
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-v2")
        
    def _initialize_bedrock_client(self):
        """Initialize the Amazon Bedrock client"""
        try:
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            region = os.getenv("AWS_REGION", "us-east-1")
            
            if aws_access_key and aws_secret_key:
                return boto3.client(
                    'bedrock-runtime',
                    region_name=region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
            else:
                # Use default credentials
                return boto3.client('bedrock-runtime', region_name=region)
        except Exception as e:
            print(f"Error initializing Bedrock client: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Bedrock is available"""
        return self.client is not None
    
    def invoke_agent(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke the Bedrock agent with a query"""
        if not self.is_available():
            return {"error": "Amazon Bedrock is not available"}
        
        try:
            # Prepare prompt with context
            context_str = ""
            if context:
                context_str = "Context:\n" + json.dumps(context, indent=2) + "\n\n"
            
            # Prepare prompt for different model types
            if "anthropic" in self.model_id:
                prompt = f"\n\nHuman: {context_str}As a ChargeX EV Charging Agent, help with: {query}\n\nAssistant:"
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "prompt": prompt,
                        "max_tokens_to_sample": 500,
                        "temperature": 0.7,
                    })
                )
                result = json.loads(response['body'].read())
                return {
                    "response": result['completion'],
                    "model": self.model_id
                }
            else:
                # Default format for non-Anthropic models
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "inputText": f"{context_str}As a ChargeX EV Charging Agent, help with: {query}",
                        "textGenerationConfig": {
                            "maxTokenCount": 500,
                            "temperature": 0.7,
                        }
                    })
                )
                result = json.loads(response['body'].read())
                return {
                    "response": result.get('results', [{}])[0].get('outputText', ''),
                    "model": self.model_id
                }
                
        except Exception as e:
            print(f"Error invoking Bedrock model: {e}")
            return {"error": str(e)}
    
    def analyze_charging_options(self, stations: List[Dict[str, Any]], 
                                vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Bedrock to analyze and recommend the best charging options
        
        Args:
            stations: List of available charging stations
            vehicle_data: Vehicle data including battery level, range, etc.
            
        Returns:
            Dictionary with recommendations and reasoning
        """
        if not self.is_available() or not stations:
            return {"error": "Cannot analyze options"}
        
        context = {
            "available_stations": stations,
            "vehicle": vehicle_data
        }
        
        query = """
        Based on the available charging stations and vehicle data, recommend the best charging option.
        Consider:
        1. Current battery level vs. desired range
        2. Price per kWh at each station
        3. Power output (kW) and charging speed
        4. Estimated time to reach desired charge level
        
        Provide a clear recommendation with estimated cost and charging time.
        """
        
        return self.invoke_agent(query, context)
    
    def optimize_payment_strategy(self, payment_options: Dict[str, Any], 
                                user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Bedrock to optimize payment strategy based on options and preferences
        
        Args:
            payment_options: Available payment methods and rates
            user_preferences: User preferences for cost, speed, etc.
            
        Returns:
            Dictionary with recommended payment strategy
        """
        if not self.is_available():
            return {"error": "Cannot optimize payment strategy"}
        
        context = {
            "payment_options": payment_options,
            "preferences": user_preferences
        }
        
        query = """
        Based on the available payment options and user preferences, recommend the optimal payment strategy.
        Consider:
        1. Cost efficiency (traditional vs. crypto payment)
        2. User's preferred payment methods
        3. Transaction speed requirements
        4. Available funds in connected wallets
        
        Provide a clear recommendation with reasoning.
        """
        
        return self.invoke_agent(query, context)

# Test the Bedrock integration
if __name__ == "__main__":
    agent = BedrockAgent()
    if agent.is_available():
        print("Bedrock agent is available")
        response = agent.invoke_agent("What are the benefits of using USDC for EV charging payments?")
        print(response.get("response", "No response"))
    else:
        print("Bedrock agent is not available")
