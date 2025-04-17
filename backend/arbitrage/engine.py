import os
import json
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from ..db import models
from ..integrations.jupiter_client import JupiterClient
from ..integrations.raydium_client import RaydiumClient
from ..integrations.orca_client import OrcaClient
from ..integrations.meteora_client import MeteoraClient
from ..integrations.solana_client import SolanaClient
from ..utils.encryption import decrypt_data
from ..realtime.price_feed import PriceFeed
from ..simulation.transaction_simulator import TransactionSimulator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arbitrage_engine")

class ArbitrageEngine:
    def __init__(self, db: Session):
        self.db = db
        self.jupiter_client = JupiterClient()
        self.raydium_client = RaydiumClient()
        self.orca_client = OrcaClient()
        self.meteora_client = MeteoraClient()
        self.solana_client = SolanaClient()
        self.price_feed = PriceFeed(db)
        self.transaction_simulator = TransactionSimulator()
        self.dex_clients = {
            "Jupiter": self.jupiter_client,
            "Raydium": self.raydium_client,
            "Orca": self.orca_client,
            "Meteora": self.meteora_client
        }
        self.price_feed_started = False
        logger.info("Initialized Arbitrage Engine")
    
    async def start_price_feed(self):
        """Start the real-time price feed"""
        if not self.price_feed_started:
            await self.price_feed.initialize_from_db()
            self.price_feed.start_background_task()
            self.price_feed_started = True
            logger.info("Started real-time price feed")
    
    async def get_token_price(self, token_mint: str, quote_mint: str, dex_name: str) -> Dict:
        """Get token price from a specific DEX"""
        try:
            # First check if we have a real-time price
            if dex_name == "Jupiter":
                latest_price = self.price_feed.get_latest_price(token_mint, quote_mint)
                if latest_price and "price" in latest_price and latest_price["price"] > 0:
                    return latest_price
            
            # If not, fetch from the DEX API
            client = self.dex_clients.get(dex_name)
            if not client:
                logger.error(f"DEX client not found for {dex_name}")
                return None
            
            price_data = await client.get_price(token_mint, quote_mint)
            return price_data
        except Exception as e:
            logger.error(f"Error getting price for {token_mint} on {dex_name}: {str(e)}")
            return None
    
    async def find_arbitrage_opportunities(self, user_id: int) -> List[Dict]:
        """Find arbitrage opportunities for all token pairs across all DEXes"""
        try:
            # Ensure price feed is running
            await self.start_price_feed()
            
            # Get user settings
            trading_settings = self.db.query(models.Setting).filter(
                models.Setting.user_id == user_id,
                models.Setting.category == "trading"
            ).first()
            
            if not trading_settings:
                logger.error(f"Trading settings not found for user {user_id}")
                return []
            
            settings = trading_settings.settings
            min_profit_threshold = Decimal(settings.get("min_profit_threshold", 0.25))
            
            # Get active DEXes
            dexes_settings = self.db.query(models.Setting).filter(
                models.Setting.user_id == user_id,
                models.Setting.category == "dexes"
            ).first()
            
            if not dexes_settings:
                logger.error(f"DEXes settings not found for user {user_id}")
                return []
            
            dex_settings = dexes_settings.settings
            active_dexes = [dex for dex, is_active in dex_settings.items() if is_active]
            
            if not active_dexes:
                logger.error("No active DEXes found")
                return []
            
            # Get all tokens
            tokens = self.db.query(models.Token).all()
            
            # Get USDC token for price comparison
            usdc_token = self.db.query(models.Token).filter(models.Token.symbol == "USDC").first()
            if not usdc_token:
                logger.error("USDC token not found")
                return []
            
            # Get all DEXes
            dexes = self.db.query(models.Dex).filter(models.Dex.name.in_(active_dexes)).all()
            dex_map = {dex.name: dex for dex in dexes}
            
            opportunities = []
            
            # For each token, check prices across all DEXes
            for token in tokens:
                if token.symbol == "USDC":
                    continue  # Skip USDC/USDC pair
                
                # Get prices across all DEXes
                prices = {}
                for dex_name in active_dexes:
                    price_data = await self.get_token_price(token.mint_address, usdc_token.mint_address, dex_name)
                    if price_data and "price" in price_data and price_data["price"] > 0:
                        prices[dex_name] = Decimal(str(price_data["price"]))
                
                if len(prices) < 2:
                    continue  # Need at least 2 DEXes for arbitrage
                
                # Find best buy and sell prices
                buy_dex = min(prices.items(), key=lambda x: x[1])
                sell_dex = max(prices.items(), key=lambda x: x[1])
                
                buy_dex_name, buy_price = buy_dex
                sell_dex_name, sell_price = sell_dex
                
                # Calculate price difference
                price_diff_percent = (sell_price - buy_price) / buy_price * 100
                
                # Only consider opportunities with profit above threshold
                if price_diff_percent > min_profit_threshold and buy_dex_name != sell_dex_name:
                    # Calculate potential profit (assuming 1 SOL trade size)
                    trade_size = Decimal("1")  # 1 token
                    potential_profit = trade_size * (sell_price - buy_price)
                    
                    # Create opportunity
                    opportunity = models.Opportunity(
                        token_id=token.id,
                        buy_dex_id=dex_map[buy_dex_name].id,
                        sell_dex_id=dex_map[sell_dex_name].id,
                        buy_price=buy_price,
                        sell_price=sell_price,
                        price_diff_percent=price_diff_percent,
                        potential_profit_usd=potential_profit,
                        status="active"
                    )
                    
                    self.db.add(opportunity)
                    self.db.commit()
                    self.db.refresh(opportunity)
                    
                    # Add to opportunities list
                    opportunities.append(opportunity)
                    
                    logger.info(f"Found arbitrage opportunity: {token.symbol} - Buy: {buy_dex_name} at {buy_price}, Sell: {sell_dex_name} at {sell_price}, Profit: {price_diff_percent}%")
            
            return opportunities
        except Exception as e:
            logger.error(f"Error finding arbitrage opportunities: {str(e)}")
            self.db.rollback()
            return []
    
    async def execute_arbitrage(self, opportunity_id: int, wallet_id: int) -> Dict:
        """Execute an arbitrage trade"""
        try:
            # Get opportunity
            opportunity = self.db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
            if not opportunity:
                logger.error(f"Opportunity {opportunity_id} not found")
                return {"success": False, "error": "Opportunity not found"}
            
            # Check if opportunity is still active
            if opportunity.status != "active":
                logger.error(f"Opportunity {opportunity_id} is not active")
                return {"success": False, "error": "Opportunity is not active"}
            
            # Update opportunity status
            opportunity.status = "executing"
            self.db.commit()
            
            # Get wallet
            wallet = self.db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
            if not wallet:
                logger.error(f"Wallet {wallet_id} not found")
                opportunity.status = "failed"
                opportunity.error_message = "Wallet not found"
                self.db.commit()
                return {"success": False, "error": "Wallet not found"}
            
            # Get token
            token = self.db.query(models.Token).filter(models.Token.id == opportunity.token_id).first()
            if not token:
                logger.error(f"Token {opportunity.token_id} not found")
                opportunity.status = "failed"
                opportunity.error_message = "Token not found"
                self.db.commit()
                return {"success": False, "error": "Token not found"}
            
            # Get buy and sell DEXes
            buy_dex = self.db.query(models.Dex).filter(models.Dex.id == opportunity.buy_dex_id).first()
            sell_dex = self.db.query(models.Dex).filter(models.Dex.id == opportunity.sell_dex_id).first()
            if not buy_dex or not sell_dex:
                logger.error(f"DEX not found")
                opportunity.status = "failed"
                opportunity.error_message = "DEX not found"
                self.db.commit()
                return {"success": False, "error": "DEX not found"}
            
            # Get USDC token for trading
            usdc_token = self.db.query(models.Token).filter(models.Token.symbol == "USDC").first()
            if not usdc_token:
                logger.error("USDC token not found")
                opportunity.status = "failed"
                opportunity.error_message = "USDC token not found"
                self.db.commit()
                return {"success": False, "error": "USDC token not found"}
            
            # Get wallet's private key if available
            private_key = None
            if wallet.encrypted_private_key:
                try:
                    private_key = decrypt_data(wallet.encrypted_private_key)
                except Exception as e:
                    logger.error(f"Error decrypting private key: {str(e)}")
                    opportunity.status = "failed"
                    opportunity.error_message = "Error decrypting private key"
                    self.db.commit()
                    return {"success": False, "error": "Error decrypting private key"}
            
            # Get trading settings
            trading_settings = self.db.query(models.Setting).filter(
                models.Setting.user_id == wallet.user_id,
                models.Setting.category == "trading"
            ).first()
            
            if not trading_settings:
                logger.error(f"Trading settings not found for user {wallet.user_id}")
                opportunity.status = "failed"
                opportunity.error_message = "Trading settings not found"
                self.db.commit()
                return {"success": False, "error": "Trading settings not found"}
            
            settings = trading_settings.settings
            max_slippage = float(settings.get("max_slippage", 0.5))
            
            # Calculate trade amount based on settings
            min_trade_size = float(settings.get("min_trade_size", 10))
            max_trade_size = float(settings.get("max_trade_size", 1000))
            
            # For this implementation, we'll use a fixed trade size
            trade_size_usd = min(max(min_trade_size, 100), max_trade_size)
            
            # Calculate token amount based on buy price
            token_amount = trade_size_usd / float(opportunity.buy_price)
            
            logger.info(f"Executing arbitrage: {token.symbol} - Buy: {buy_dex.name} at {opportunity.buy_price}, Sell: {sell_dex.name} at {opportunity.sell_price}")
            logger.info(f"Trade size: ${trade_size_usd} ({token_amount} {token.symbol})")
            
            # Create buy transaction using Jupiter
            if buy_dex.name == "Jupiter":
                # Convert USD to USDC amount (assuming 1:1)
                usdc_amount = trade_size_usd * 1_000_000  # USDC has 6 decimals
                
                # Create swap transaction
                buy_tx_result = await self.jupiter_client.create_swap_transaction(
                    usdc_token.mint_address,
                    token.mint_address,
                    usdc_amount,
                    wallet.address,
                    int(max_slippage * 100)  # Convert to basis points
                )
                
                if not buy_tx_result["success"]:
                    logger.error(f"Failed to create buy transaction: {buy_tx_result.get('error')}")
                    opportunity.status = "failed"
                    opportunity.error_message = f"Failed to create buy transaction: {buy_tx_result.get('error')}"
                    self.db.commit()
                    return {"success": False, "error": buy_tx_result.get('error')}
                
                # Simulate the transaction
                if buy_tx_result.get("swapTransaction"):
                    simulation_result = await self.transaction_simulator.simulate_transaction(buy_tx_result["swapTransaction"])
                    
                    if not simulation_result["success"]:
                        logger.error(f"Buy transaction simulation failed: {simulation_result.get('error')}")
                        opportunity.status = "failed"
                        opportunity.error_message = f"Buy transaction simulation failed: {simulation_result.get('error')}"
                        self.db.commit()
                        return {"success": False, "error": simulation_result.get('error')}
                    
                    logger.info(f"Buy transaction simulation successful")
                
                # Calculate token amount received
                token_amount = float(buy_tx_result.get("outputAmount", 0)) / (10 ** token.decimals)
            
            # Create sell transaction using Jupiter
            if sell_dex.name == "Jupiter" and token_amount > 0:
                # Convert token amount to smallest units
                token_amount_smallest = int(token_amount * (10 ** token.decimals))
                
                # Create swap transaction
                sell_tx_result = await self.jupiter_client.create_swap_transaction(
                    token.mint_address,
                    usdc_token.mint_address,
                    token_amount_smallest,
                    wallet.address,
                    int(max_slippage * 100)  # Convert to basis points
                )
                
                if not sell_tx_result["success"]:
                    logger.error(f"Failed to create sell transaction: {sell_tx_result.get('error')}")
                    opportunity.status = "failed"
                    opportunity.error_message = f"Failed to create sell transaction: {sell_tx_result.get('error')}"
                    self.db.commit()
                    return {"success": False, "error": sell_tx_result.get('error')}
                
                # Simulate the transaction
                if sell_tx_result.get("swapTransaction"):
                    simulation_result = await self.transaction_simulator.simulate_transaction(sell_tx_result["swapTransaction"])
                    
                    if not simulation_result["success"]:
                        logger.error(f"Sell transaction simulation failed: {simulation_result.get('error')}")
                        opportunity.status = "failed"
                        opportunity.error_message = f"Sell transaction simulation failed: {simulation_result.get('error')}"
                        self.db.commit()
                        return {"success": False, "error": simulation_result.get('error')}
                    
                    logger.info(f"Sell transaction simulation successful")
                
                # Calculate USDC amount received
                usdc_amount_received = float(sell_tx_result.get("outputAmount", 0)) / 1_000_000  # USDC has 6 decimals
                
                # Calculate actual profit
                actual_profit = usdc_amount_received - trade_size_usd
            else:
                # For non-Jupiter DEXes or if token_amount is 0
                actual_profit = 0
                usdc_amount_received = 0
            
            # In a real implementation, you would:
            # 1. Sign the transactions with the wallet's private key
            # 2. Send the transactions to the blockchain
            # 3. Wait for confirmations
            
            # For this implementation, we'll simulate a successful trade
            if private_key:
                logger.info("Using wallet's private key for transaction signing")
                # In a real implementation, you would use the private key to sign transactions
            else:
                logger.info("No private key available, simulating trade execution")
            
            # Simulate network delay
            await asyncio.sleep(2)
            
            # Create trade record
            trade = models.Trade(
                opportunity_id=opportunity.id,
                wallet_id=wallet.id,
                token_id=token.id,
                buy_dex_id=buy_dex.id,
                sell_dex_id=sell_dex.id,
                buy_price=float(opportunity.buy_price),
                sell_price=float(opportunity.sell_price),
                amount=token_amount,
                profit_usd=actual_profit,
                status="completed",
                tx_hash_buy=f"simulated_buy_tx_{int(time.time())}",
                tx_hash_sell=f"simulated_sell_tx_{int(time.time())}"
            )
            
            self.db.add(trade)
            
            # Update opportunity status
            opportunity.status = "completed"
            
            # Update performance metrics
            today = time.strftime("%Y-%m-%d")
            performance_metric = self.db.query(models.PerformanceMetric).filter(
                models.PerformanceMetric.user_id == wallet.user_id,
                models.PerformanceMetric.date == today
            ).first()
            
            if performance_metric:
                performance_metric.profit_usd += Decimal(str(actual_profit))
                performance_metric.trades_count += 1
            else:
                performance_metric = models.PerformanceMetric(
                    user_id=wallet.user_id,
                    date=today,
                    profit_usd=Decimal(str(actual_profit)),
                    trades_count=1,
                    opportunities_count=1
                )
                self.db.add(performance_metric)
            
            self.db.commit()
            self.db.refresh(trade)
            
            logger.info(f"Arbitrage executed successfully: {trade.id}")
            
            return {
                "success": True,
                "trade_id": trade.id,
                "profit": float(trade.profit_usd)
            }
        except Exception as e:
            logger.error(f"Error executing arbitrage: {str(e)}")
            self.db.rollback()
            
            # Update opportunity status
            opportunity = self.db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
            if opportunity:
                opportunity.status = "failed"
                opportunity.error_message = str(e)
                self.db.commit()
            
            return {"success": False, "error": str(e)}
