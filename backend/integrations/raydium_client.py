import os
import json
import asyncio
from typing import Dict, List, Optional, Tuple
import httpx
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("raydium_client")

# Load environment variables
load_dotenv()

class RaydiumClient:
    def __init__(self):
        self.base_url = "https://api.raydium.io/v2"
        logger.info("Initialized Raydium client")
    
    async def get_pools(self) -> List[Dict]:
        """Get all Raydium pools"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/main/pools")
                
                if response.status_code != 200:
                    logger.error(f"Error getting pools: {response.text}")
                    return []
                
                return response.json()
        except Exception as e:
            logger.error(f"Error getting Raydium pools: {str(e)}")
            return []
    
    async def get_price(self, input_mint: str, output_mint: str, amount: float = 1.0) -> Dict:
        """Get price for a token pair"""
        try:
            # First, get all pools
            pools = await self.get_pools()
            
            # Find the pool for the token pair
            pool = None
            for p in pools:
                if (p.get("baseMint") == input_mint and p.get("quoteMint") == output_mint) or \
                   (p.get("baseMint") == output_mint and p.get("quoteMint") == input_mint):
                    pool = p
                    break
            
            if not pool:
                logger.error(f"Pool not found for {input_mint} -> {output_mint}")
                return None
            
            # Calculate price based on pool data
            if pool.get("baseMint") == input_mint:
                price = float(pool.get("price", 0))
                output_amount = amount * price
            else:
                price = 1 / float(pool.get("price", 1))
                output_amount = amount * price
            
            return {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "inAmount": amount,
                "outAmount": output_amount,
                "price": price
            }
        except Exception as e:
            logger.error(f"Error getting price for {input_mint} -> {output_mint}: {str(e)}")
            return None
