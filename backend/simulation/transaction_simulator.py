import logging
import aiohttp
import json
import base64
from typing import Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("transaction_simulator")

class TransactionSimulator:
    def __init__(self):
        # Use a public RPC endpoint for Solana
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        logger.info(f"Initialized Transaction Simulator with RPC: {self.rpc_url}")
    
    async def simulate_transaction(self, transaction_base64: str) -> Dict[str, Any]:
        """
        Simulate a transaction using Solana's simulateTransaction RPC method
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "simulateTransaction",
                    "params": [
                        transaction_base64,
                        {
                            "encoding": "base64",
                            "commitment": "confirmed",
                            "accounts": {
                                "encoding": "base64",
                                "addresses": []
                            },
                            "sigVerify": False
                        }
                    ]
                }
                
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"RPC error: {error_text}")
                        return {"success": False, "error": error_text}
                    
                    data = await response.json()
                    
                    if "error" in data:
                        logger.error(f"Simulation error: {data['error']}")
                        return {"success": False, "error": data["error"]}
                    
                    result = data.get("result", {})
                    
                    # Check for errors in the simulation
                    if "err" in result and result["err"] is not None:
                        logger.error(f"Transaction would fail: {result['err']}")
                        return {
                            "success": False,
                            "error": f"Transaction would fail: {result['err']}",
                            "logs": result.get("logs", [])
                        }
                    
                    # Extract useful information from the simulation
                    return {
                        "success": True,
                        "logs": result.get("logs", []),
                        "accounts": result.get("accounts", []),
                        "unitsConsumed": result.get("unitsConsumed", 0)
                    }
        except Exception as e:
            logger.error(f"Error simulating transaction: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def estimate_transaction_fee(self, transaction_base64: str) -> Dict[str, Any]:
        """
        Estimate the transaction fee using simulation
        """
        try:
            simulation_result = await self.simulate_transaction(transaction_base64)
            
            if not simulation_result["success"]:
                return simulation_result
            
            # Get the latest fee schedule
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getFees",
                    "params": []
                }
                
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"RPC error: {error_text}")
                        return {"success": False, "error": error_text}
                    
                    data = await response.json()
                    
                    if "error" in data:
                        logger.error(f"Fee estimation error: {data['error']}")
                        return {"success": False, "error": data["error"]}
                    
                    result = data.get("result", {})
                    
                    # Calculate fee based on units consumed
                    units_consumed = simulation_result.get("unitsConsumed", 0)
                    lamports_per_cu = result.get("feeCalculator", {}).get("lamportsPerSignature", 5000) / 100000
                    estimated_fee = int(units_consumed * lamports_per_cu)
                    
                    return {
                        "success": True,
                        "estimated_fee_lamports": estimated_fee,
                        "estimated_fee_sol": estimated_fee / 1_000_000_000,  # Convert to SOL
                        "units_consumed": units_consumed
                    }
        except Exception as e:
            logger.error(f"Error estimating transaction fee: {str(e)}")
            return {"success": False, "error": str(e)}
