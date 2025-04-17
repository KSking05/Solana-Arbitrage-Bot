import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
import os
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jupiter_client")

class JupiterClient:
    def __init__(self):
        # Using the free Jupiter API
        self.base_url = "https://quote-api.jup.ag/v6"
        logger.info("Initialized Jupiter Client with free API")
    
    async def get_price(self, input_mint: str, output_mint: str, amount: float = 1000000) -> Dict:
        """
        Get price for a token pair using Jupiter's quote API
        amount is in the smallest unit (e.g., lamports for SOL)
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Use the quote endpoint to get price information
                url = f"{self.base_url}/quote"
                params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(int(amount)),
                    "slippageBps": 50  # 0.5% slippage
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Jupiter API error: {error_text}")
                        return {"price": 0, "error": error_text}
                    
                    data = await response.json()
                    
                    # Calculate price from the quote
                    if "outAmount" in data and "inAmount" in data:
                        out_amount = int(data["outAmount"])
                        in_amount = int(data["inAmount"])
                        
                        if in_amount > 0:
                            price = out_amount / in_amount
                            return {
                                "price": price,
                                "outAmount": out_amount,
                                "inAmount": in_amount,
                                "marketInfos": data.get("marketInfos", []),
                                "priceImpactPct": data.get("priceImpactPct", 0)
                            }
                    
                    logger.error(f"Invalid response from Jupiter API: {data}")
                    return {"price": 0, "error": "Invalid response"}
        except Exception as e:
            logger.error(f"Error getting price from Jupiter: {str(e)}")
            return {"price": 0, "error": str(e)}
    
    async def get_routes(self, input_mint: str, output_mint: str, amount: float = 1000000) -> List[Dict]:
        """
        Get all available routes for a token pair
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/quote"
                params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(int(amount)),
                    "slippageBps": 50,
                    "onlyDirectRoutes": False
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Jupiter API error: {error_text}")
                        return []
                    
                    data = await response.json()
                    routes = []
                    
                    if "routesInfos" in data:
                        routes = data["routesInfos"]
                    elif "marketInfos" in data:
                        # If routesInfos is not available, use marketInfos
                        routes = [{"marketInfos": data["marketInfos"], "outAmount": data.get("outAmount")}]
                    
                    return routes
        except Exception as e:
            logger.error(f"Error getting routes from Jupiter: {str(e)}")
            return []
    
    async def create_swap_transaction(self, input_mint: str, output_mint: str, amount: float, 
                                     user_public_key: str, slippage_bps: int = 50) -> Dict:
        """
        Create a swap transaction using Jupiter's swap API
        """
        try:
            # Step 1: Get the route first
            async with aiohttp.ClientSession() as session:
                quote_url = f"{self.base_url}/quote"
                quote_params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(int(amount)),
                    "slippageBps": slippage_bps
                }
                
                async with session.get(quote_url, params=quote_params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Jupiter quote API error: {error_text}")
                        return {"success": False, "error": error_text}
                    
                    quote_data = await response.json()
                
                # Step 2: Create the swap transaction
                swap_url = f"{self.base_url}/swap"
                swap_payload = {
                    "quoteResponse": quote_data,
                    "userPublicKey": user_public_key,
                    "wrapUnwrapSOL": True
                }
                
                async with session.post(swap_url, json=swap_payload) as swap_response:
                    if swap_response.status != 200:
                        error_text = await swap_response.text()
                        logger.error(f"Jupiter swap API error: {error_text}")
                        return {"success": False, "error": error_text}
                    
                    swap_data = await swap_response.json()
                    
                    return {
                        "success": True,
                        "swapTransaction": swap_data.get("swapTransaction"),
                        "inputAmount": amount,
                        "outputAmount": quote_data.get("outAmount"),
                        "price": float(quote_data.get("outAmount", 0)) / float(amount) if float(amount) > 0 else 0
                    }
        except Exception as e:
            logger.error(f"Error creating swap transaction: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def simulate_swap(self, input_mint: str, output_mint: str, amount: float) -> Dict:
        """
        Simulate a swap to get accurate output amount and price impact
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/quote"
                params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(int(amount)),
                    "slippageBps": 50,
                    "onlyDirectRoutes": False
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Jupiter API error: {error_text}")
                        return {"success": False, "error": error_text}
                    
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "inputAmount": amount,
                        "outputAmount": int(data.get("outAmount", 0)),
                        "price": float(data.get("outAmount", 0)) / float(amount) if float(amount) > 0 else 0,
                        "priceImpactPct": data.get("priceImpactPct", 0),
                        "marketInfos": data.get("marketInfos", [])
                    }
        except Exception as e:
            logger.error(f"Error simulating swap: {str(e)}")
            return {"success": False, "error": str(e)}
