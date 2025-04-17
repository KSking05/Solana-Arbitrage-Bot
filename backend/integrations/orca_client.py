import os
import json
import asyncio
from typing import Dict, List, Optional, Tuple
import httpx
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orca_client")

# Load environment variables
load_dotenv()

class OrcaClient:
    def __init__(self):
        self.base_url = "https://api.orca.so"
        logger.info("Initialized Orca client")
    
    async def get_pools(self) -> List[Dict]:
        """Get all Orca pools"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/pools")
                
                if response.status_code != 200:
                    logger.error(f"Error getting pools: {response.text}")
                    return []
                
                return response.json()
        except Exception as e:
            logger.error(f"Error getting Orca pools: {str(e)}")
            return []
    
    async def get_price(self, input_mint: str, output_mint: str, amount: float = 1.0) -> Dict:
        """Get price for a token pair"""
        try:
            # For Orca, we'll use a simplified approach since their API might be different
            # In a real implementation, you would use their specific API endpoints
            
            # For now, we'll simulate a price with a small variation from the "market price"
            # This is just for demonstration purposes
            
            # Assume SOL/USDC price is around $100
            if input_mint == "So11111111111111111111111111111111111111112" and output_mint == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
                price = 99.75  # Slightly lower than market
                output_amount = amount * price
            elif input_mint == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" and output_mint == "So11111111111111111111111111111111111111112":
                price = 1 / 99.75
                output_amount = amount * price
            else:
                # For other pairs, use a default price (this would be replaced with actual API calls)
                price = 1.0
                output_amount = amount
            
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
