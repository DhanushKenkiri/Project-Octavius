"""
CDP Wallet and x402 payment integration for ChargeX Agent
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from x402.types import PaymentRequirements, PaymentRequiredResponse
    from x402.encoding import safe_base64_decode
    X402_AVAILABLE = True
except ImportError:
    logger.warning("x402 package not found. Some payment features will be unavailable.")
    X402_AVAILABLE = False

class PaymentManager:
    """
    Class to handle CDP Wallet and x402 payment integrations
    """
    
    def __init__(self):
        """Initialize the payment manager with configuration from environment variables"""
        # CDP Wallet Configuration
        self.cdp_wallet_address = os.getenv("CDP_WALLET_ADDRESS")
        self.cdp_network = os.getenv("CDP_NETWORK_NAME", "Base-Sepolia")
        self.cdp_network_rpc = os.getenv("CDP_NETWORK_RPC", "https://sepolia.base.org")
        self.cdp_network_chain_id = int(os.getenv("CDP_NETWORK_CHAIN_ID", "84532"))
        
        # x402 Configuration
        self.x402_private_key = os.getenv("X402_PRIVATE_KEY")
        self.x402_public_key = os.getenv("X402_PUBLIC_KEY")
        self.x402_payment_token = os.getenv("X402_PAYMENT_TOKEN_CONTRACT")
        self.x402_payment_controller = os.getenv("X402_PAYMENT_CONTROLLER")
        
        # Default configuration
        self.default_currency = os.getenv("DEFAULT_CURRENCY", "USDC")
        self.charging_rate = float(os.getenv("CHARGING_RATE_MULTIPLIER", "0.35"))
        
        logger.info(f"PaymentManager initialized for network {self.cdp_network}")
        
    def get_wallet_info(self) -> Dict[str, Any]:
        """Get CDP wallet information"""
        return {
            "address": self.cdp_wallet_address,
            "network": self.cdp_network,
            "balance": 75.45,  # Mocked for demo purposes
        }
        
    def create_payment_request(self, amount: float, recipient: str = None) -> Dict[str, Any]:
        """
        Create a payment request using x402 protocol
        
        Args:
            amount: The amount to request in USDC
            recipient: Recipient address (defaults to station owner address)
            
        Returns:
            Dictionary with payment request details
        """
        if not X402_AVAILABLE:
            # Mock response for demo
            return {
                "payment_url": f"x402://pay?amount={amount}&recipient={recipient or '0x123'}&token={self.x402_payment_token}",
                "payment_id": f"pay-{hash(f'{amount}-{recipient}')}"[:14],
                "amount": amount,
                "currency": self.default_currency,
                "recipient": recipient or "0x36B0D0d2cc1458903dc05Ec189Ea798D5221626e",
                "chain": self.cdp_network,
            }
            
        try:
            # Real x402 implementation would go here
            # This is simplified for demo purposes
            payment_requirements = PaymentRequirements(
                amount=str(amount),
                payment_token=self.x402_payment_token,
                recipient=recipient or "0x36B0D0d2cc1458903dc05Ec189Ea798D5221626e",
                network_chain_id=self.cdp_network_chain_id,
            )
            
            # Generate payment URL (mocked)
            payment_url = f"x402://pay?amount={amount}&recipient={recipient}&token={self.x402_payment_token}"
            payment_id = f"pay-{hash(f'{amount}-{recipient}')}"[:14]
            
            return {
                "payment_url": payment_url,
                "payment_id": payment_id,
                "amount": amount,
                "currency": self.default_currency,
                "recipient": recipient or "0x36B0D0d2cc1458903dc05Ec189Ea798D5221626e",
                "chain": self.cdp_network,
            }
        except Exception as e:
            logger.error(f"Error creating payment request: {e}")
            raise
            
    def process_payment(self, payment_id: str, amount: float) -> Dict[str, Any]:
        """
        Process a payment (mocked for the demo)
        
        Args:
            payment_id: The payment ID to process
            amount: The amount being paid
            
        Returns:
            Dictionary with payment result details
        """
        # For demo purposes, we'll simulate a successful payment
        tx_hash = f"0x{''.join(['0123456789abcdef'[hash(payment_id + str(i)) % 16] for i in range(64)])}"
        
        return {
            "status": "completed",
            "tx_hash": tx_hash,
            "amount": amount,
            "currency": self.default_currency,
            "timestamp": 1719578400,  # June 27, 2025
        }
        
    def calculate_charging_cost(self, kwh: float) -> float:
        """
        Calculate the cost of charging based on kWh and current rate
        
        Args:
            kwh: The amount of energy in kilowatt-hours
            
        Returns:
            The cost in USDC
        """
        return round(kwh * self.charging_rate, 2)
        
    def get_payment_history(self) -> list:
        """
        Get payment history (mocked for the demo)
        
        Returns:
            List of payment records
        """
        # Mock data for the demo
        return [
            {
                "amount": 12.25,
                "currency": "USDC",
                "timestamp": 1719578400,  # June 27, 2025
                "tx_hash": "0x8f7d325c19736d3d4c7e65feb84373c26be485eebd6baecd5da985dbc5fb0943",
                "session_id": "session-7952"
            },
            {
                "amount": 9.50,
                "currency": "USDC",
                "timestamp": 1719405600,  # June 25, 2025
                "tx_hash": "0x3a7b5d87c4e7f8a9d2b3c6f1d5e4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6",
                "session_id": "session-5234"
            },
            {
                "amount": 14.80,
                "currency": "USDC",
                "timestamp": 1719232800,  # June 23, 2025
                "tx_hash": "0x9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c",
                "session_id": "session-4127"
            }
        ]
