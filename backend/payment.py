"""
Payment module for ChargeX Agent using x402 and Coinbase Developer Platform SDK.
Based on the latest documentation from https://github.com/coinbase/x402
"""

import os
import logging
from typing import Dict, Any, Optional
import time
import uuid
import json
import requests

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import x402 for payment verification
try:
    import x402
    from x402 import PaymentRequest, PaymentVerification
    HAS_X402 = True
    logger.info("Successfully imported x402 SDK")
except ImportError as e:
    logger.warning(f"x402 package not installed. Payment verification will be simulated. Error: {e}")
    HAS_X402 = False

# Import CDP SDK for wallet operations
try:
    from cdp import Cdp, Wallet, WalletData
    HAS_CDP = True
    logger.info("CDP SDK successfully imported")
except ImportError as e:
    logger.warning(f"CDP SDK not available, simulating CDP wallet operations. Error: {e}")
    HAS_CDP = False

class PaymentManager:
    """
    Handles payments and verifications using x402 and CDP
    """
    
    def __init__(self):
        """Initialize payment manager from environment variables"""
        # Get configuration from environment
        self.api_key = os.getenv("COINBASE_API_KEY")
        self.api_secret = os.getenv("COINBASE_API_SECRET")
        self.x402_verification_key = os.getenv("X402_VERIFICATION_KEY")
        self.x402_api_url = os.getenv("X402_API_URL", "https://api.x402.coinbase.com/v1")
        self.cdp_wallet_api_url = os.getenv("COINBASE_WALLET_API_URL", "https://api.wallet.coinbase.com/wallet/v1")
        self.network = {
            "name": os.getenv("NETWORK_NAME", "Base-Sepolia"),
            "rpc": os.getenv("NETWORK_RPC", "https://sepolia.base.org"),
            "chain_id": int(os.getenv("NETWORK_CHAIN_ID", "84532"))
        }
        self.token_contract = os.getenv("TOKEN_CONTRACT", "0x036CbD53842c5426634e7929541eC2318f3dCF7e")
        self.default_currency = os.getenv("DEFAULT_CURRENCY", "USDC")
        self.charging_rate = float(os.getenv("CHARGING_RATE_PER_KWH", "0.35"))
        self.enable_fallback = os.getenv("ENABLE_FALLBACK_MODE", "false").lower() == "true"
        
        # Initialize CDP client if available
        self.cdp_client = None
        if HAS_CDP and self.api_key and self.api_secret:
            try:
                Cdp.configure(self.api_key, self.api_secret)
                logger.info("CDP client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize CDP client: {e}")
                if not self.enable_fallback:
                    raise
        else:
            logger.warning("CDP API credentials missing or SDK unavailable, using demo mode")
          # Log x402 configuration
        if HAS_X402:
            if self.x402_verification_key:
                logger.info("x402 verification key found, x402 payment verification enabled")
            else:
                logger.warning("x402 verification key missing, verification will be simulated")
        
        logger.info(f"PaymentManager initialized for network: {self.network['name']} (Chain ID: {self.network['chain_id']})")
        logger.info(f"Fallback mode: {'enabled' if self.enable_fallback else 'disabled'}")
        
    def get_payment_requirements(self, kwh_amount: float, station_id: str) -> Dict[str, Any]:
        """
        Generate payment requirements for a charging session using real x402
        
        Args:
            kwh_amount: Amount of kWh to charge
            station_id: ID of the charging station
            
        Returns:
            Dictionary with payment requirements
        """
        # Calculate payment amount based on charging rate
        amount = round(kwh_amount * self.charging_rate, 2)
        
        # Generate a unique ID for this payment requirement
        payment_id = f"pay-{uuid.uuid4().hex[:8]}"
        
        try:
            if HAS_X402:
                logger.info(f"Creating real x402 payment requirements for {amount} {self.default_currency}")
                
                # Create a unique recipient address for this station (demo purposes)
                recipient_address = f"0x{station_id.zfill(40)}"  # Proper address format
                
                # Create x402 payment request
                payment_request = PaymentRequest(
                    amount=amount,
                    token=self.token_contract,
                    recipient=recipient_address,
                    network=self.network["name"],
                    memo=f"ChargeX session for {kwh_amount} kWh at station {station_id}"
                )
                
                # Generate the payment URL
                payment_url = x402.create_payment_url(payment_request)
                
                logger.info(f"Successfully created x402 payment requirements")
                
                return {
                    "payment_request": payment_request.to_dict(),
                    "payment_url": payment_url,
                    "amount": amount,
                    "currency": self.default_currency,
                    "station_id": station_id,
                    "payment_id": payment_id,
                    "recipient": recipient_address,
                    "network": self.network["name"]
                }
            
            raise Exception("x402 SDK not available")
                
        except Exception as e:
            logger.error(f"Error creating x402 payment requirements: {e}")
            
            if not self.enable_fallback:
                raise RuntimeError(f"Payment system unavailable: {e}")
        
        # Fallback or simulation mode
        logger.info("Using fallback/simulation mode for payment requirements")
        recipient_address = f"0x{station_id.zfill(40)}"
        return {
            "payment_request": {
                "token": self.token_contract,
                "amount": str(amount),
                "recipient": recipient_address,
                "network": self.network["name"],
                "nonce": str(int(time.time())),
                "expires_at": str(int(time.time() + 3600))  # 1 hour from now
            },
            "payment_url": f"https://wallet.coinbase.com/pay?amount={amount}&token=USDC&network={self.network['name']}",
            "amount": amount,
            "currency": self.default_currency,
            "station_id": station_id,
            "payment_id": payment_id,
            "recipient": recipient_address,
            "network": self.network["name"]
        }
      def verify_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a payment using real x402 verification
        
        Args:
            payment_data: Dictionary containing the payment proof
            
        Returns:
            Dictionary with verification result
        """
        logger.info(f"Verifying payment: {json.dumps(payment_data, default=str)[:100]}...")
        
        try:
            if HAS_X402 and self.x402_verification_key and not self.x402_verification_key.startswith("demo"):
                # Extract proof from payment data
                proof = payment_data.get("proof", {})
                
                logger.info(f"Using real x402 SDK to verify payment")
                
                # Use x402 to verify the payment
                verification = PaymentVerification(
                    proof=proof,
                    verification_key=self.x402_verification_key
                )
                
                verification_result = verification.verify()
                
                if verification_result.verified:
                    logger.info(f"Payment verified successfully: {verification_result.transaction_hash}")
                    return {
                        "verified": True,
                        "tx_hash": verification_result.transaction_hash,
                        "amount": verification_result.amount,
                        "token": verification_result.token,
                        "timestamp": verification_result.timestamp,
                        "details": verification_result.to_dict() if hasattr(verification_result, "to_dict") else {}
                    }
                else:
                    logger.warning("Payment verification failed")
                    return {
                        "verified": False,
                        "error": "Payment verification failed",
                        "details": verification_result.to_dict() if hasattr(verification_result, "to_dict") else {}
                    }
            
            raise Exception("x402 SDK or real verification key not available")
                
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            
            if not self.enable_fallback:
                return {
                    "verified": False,
                    "error": f"Error during verification: {str(e)}"
                }
        
        # For demo purposes, simulate successful verification in fallback mode
        logger.info("Using simulated payment verification (fallback mode)")
        
        # Always verify in demo mode to ensure the flow is not interrupted
        simulated_tx_hash = payment_data.get("proof", {}).get("tx_hash", f"0x{uuid.uuid4().hex}")
        logger.info(f"Simulated payment verification successful: {simulated_tx_hash}")
        
        return {
            "verified": True,
            "tx_hash": simulated_tx_hash,
            "amount": payment_data.get("amount", "10.0"),
            "token": self.default_currency,
            "timestamp": int(time.time()),
            "details": {
                "mode": "simulation",
                "timestamp": int(time.time()),
                "amount": payment_data.get("amount", "10.0"),
                "token": self.default_currency
            }
        }
      def get_wallet_info(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get real CDP wallet information
        
        Args:
            wallet_address: Optional wallet address to check
            
        Returns:
            Dictionary with wallet information
        """
        if not wallet_address:
            wallet_address = "0x1234567890123456789012345678901234567890"  # Default demo address
        
        try:
            if HAS_CDP and self.api_key and self.api_secret:
                logger.info(f"Getting real CDP wallet info for address: {wallet_address}")
                
                # Use the real CDP SDK
                try:
                    # Create a wallet instance or get existing one
                    wallet = Wallet.fetch(wallet_address)
                    
                    # Get balance information
                    balance_info = wallet.balance(self.default_currency)
                    
                    return {
                        "address": wallet_address,
                        "network": self.network["name"],
                        "balance": {
                            self.default_currency: str(balance_info.amount),
                            "ETH": "0.5"  # Placeholder for demo
                        },
                        "supports_x402": True,
                        "wallet_id": wallet.id if hasattr(wallet, 'id') else None
                    }
                    
                except Exception as e:
                    logger.warning(f"CDP wallet fetch failed: {e}, falling back to simulation")
                    if not self.enable_fallback:
                        raise
            
            raise Exception("CDP SDK or credentials not available")
                
        except Exception as e:
            logger.error(f"Error getting wallet info: {e}")
            
            if not self.enable_fallback:
                raise RuntimeError(f"Wallet service unavailable: {e}")
        
        # Fallback or simulation mode
        logger.info("Using simulated wallet info (fallback mode)")
        return {
            "address": wallet_address,
            "network": self.network["name"],
            "balance": {
                self.default_currency: "100.00",
                "ETH": "0.5"
            },
            "supports_x402": True,
            "mode": "simulation"
        }
    
    def create_wallet(self) -> Dict[str, Any]:
        """
        Create a new CDP wallet
        
        Returns:
            Dictionary with new wallet information
        """
        try:
            if HAS_CDP and self.api_key and self.api_secret:
                logger.info("Creating new CDP wallet")
                
                # Create a new wallet using CDP SDK
                wallet = Wallet.create()
                
                return {
                    "wallet_id": wallet.id,
                    "address": wallet.default_address.address_id,
                    "network": self.network["name"],
                    "created": True
                }
            
            raise Exception("CDP SDK not available")
            
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            
            if not self.enable_fallback:
                raise RuntimeError(f"Wallet creation failed: {e}")
            
            # Fallback simulation
            logger.info("Using simulated wallet creation")
            return {
                "wallet_id": f"wallet-{uuid.uuid4().hex[:8]}",
                "address": f"0x{uuid.uuid4().hex[:40]}",
                "network": self.network["name"],
                "created": True,
                "mode": "simulation"
            }

# Create a singleton instance for easy import
payment_manager = PaymentManager()
