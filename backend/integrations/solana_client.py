import os
import base58
import json
import asyncio
from typing import Dict, List, Optional, Tuple
import httpx
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("solana_client")

# Load environment variables
load_dotenv()

# Get Solana RPC URL from environment variable
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

class SolanaClient:
    def __init__(self, rpc_url: str = None):
        self.rpc_url = rpc_url or SOLANA_RPC_URL
        # We'll use direct RPC calls instead of the solana-py library
        logger.info(f"Initialized Solana client with RPC URL: {self.rpc_url}")
    
    async def get_balance(self, wallet_address: str) -> float:
        """Get SOL balance for a wallet"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [wallet_address]
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Error getting balance: {response.text}")
                    return 0
                
                data = response.json()
                if "result" in data and "value" in data["result"]:
                    balance_lamports = data["result"]["value"]
                    balance_sol = balance_lamports / 10**9  # Convert lamports to SOL
                    return balance_sol
                
                logger.error(f"Invalid response format: {data}")
                return 0
        except Exception as e:
            logger.error(f"Error getting balance for {wallet_address}: {str(e)}")
            return 0
    
    async def get_token_balance(self, wallet_address: str, token_mint: str) -> float:
        """Get token balance for a wallet"""
        try:
            # Use a public API to get token balances
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://public-api.solscan.io/account/tokens",
                    params={"account": wallet_address}
                )
                
                if response.status_code != 200:
                    logger.error(f"Error getting token balance: {response.text}")
                    return 0
                
                tokens = response.json()
                for token in tokens:
                    if token.get("tokenAddress") == token_mint:
                        decimals = int(token.get("decimals", 0))
                        balance = float(token.get("tokenAmount", {}).get("uiAmount", 0))
                        return balance
                
                return 0
        except Exception as e:
            logger.error(f"Error getting token balance for {wallet_address}, token {token_mint}: {str(e)}")
            return 0
    
    async def send_transaction(self, transaction_base64: str) -> Dict:
        """Send a transaction to the Solana blockchain"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            transaction_base64,
                            {"encoding": "base64", "preflightCommitment": "confirmed"}
                        ]
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Error sending transaction: {response.text}")
                    return {"success": False, "error": response.text}
                
                data = response.json()
                if "error" in data:
                    logger.error(f"Transaction error: {data['error']}")
                    return {"success": False, "error": data["error"]}
                
                return {"success": True, "signature": data.get("result")}
        except Exception as e:
            logger.error(f"Error sending transaction: {str(e)}")
            return {"success": False, "error": str(e)}
