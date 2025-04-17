import asyncio
import json
import logging
import websockets
from typing import Dict, List, Set, Callable, Any
import time
from decimal import Decimal
from sqlalchemy.orm import Session
from ..db import models
from ..integrations.jupiter_client import JupiterClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("price_feed")

class PriceFeed:
    def __init__(self, db: Session):
        self.db = db
        self.jupiter_client = JupiterClient()
        self.token_pairs: Set[tuple] = set()  # Set of (input_mint, output_mint) pairs to monitor
        self.price_subscribers: Dict[tuple, List[Callable]] = {}  # Callbacks for price updates
        self.prices: Dict[tuple, Dict] = {}  # Latest prices for each pair
        self.update_interval = 5  # Seconds between price updates
        self.is_running = False
        self.task = None
        logger.info("Initialized Price Feed")
    
    def add_token_pair(self, input_mint: str, output_mint: str):
        """Add a token pair to monitor"""
        pair = (input_mint, output_mint)
        self.token_pairs.add(pair)
        if pair not in self.price_subscribers:
            self.price_subscribers[pair] = []
        logger.info(f"Added token pair to monitor: {input_mint} -> {output_mint}")
    
    def remove_token_pair(self, input_mint: str, output_mint: str):
        """Remove a token pair from monitoring"""
        pair = (input_mint, output_mint)
        if pair in self.token_pairs:
            self.token_pairs.remove(pair)
        if pair in self.price_subscribers:
            del self.price_subscribers[pair]
        if pair in self.prices:
            del self.prices[pair]
        logger.info(f"Removed token pair from monitoring: {input_mint} -> {output_mint}")
    
    def subscribe(self, input_mint: str, output_mint: str, callback: Callable):
        """Subscribe to price updates for a token pair"""
        pair = (input_mint, output_mint)
        if pair not in self.token_pairs:
            self.add_token_pair(input_mint, output_mint)
        
        if pair not in self.price_subscribers:
            self.price_subscribers[pair] = []
        
        self.price_subscribers[pair].append(callback)
        logger.info(f"Added subscriber for {input_mint} -> {output_mint}")
    
    def unsubscribe(self, input_mint: str, output_mint: str, callback: Callable):
        """Unsubscribe from price updates for a token pair"""
        pair = (input_mint, output_mint)
        if pair in self.price_subscribers and callback in self.price_subscribers[pair]:
            self.price_subscribers[pair].remove(callback)
            logger.info(f"Removed subscriber for {input_mint} -> {output_mint}")
    
    async def fetch_prices(self):
        """Fetch prices for all monitored token pairs"""
        for input_mint, output_mint in self.token_pairs:
            try:
                price_data = await self.jupiter_client.get_price(input_mint, output_mint)
                
                if "price" in price_data and price_data["price"] > 0:
                    pair = (input_mint, output_mint)
                    old_price = self.prices.get(pair, {}).get("price", 0)
                    self.prices[pair] = price_data
                    
                    # Calculate price change percentage
                    if old_price > 0:
                        price_change_pct = (price_data["price"] - old_price) / old_price * 100
                        self.prices[pair]["price_change_pct"] = price_change_pct
                    
                    # Notify subscribers
                    if pair in self.price_subscribers:
                        for callback in self.price_subscribers[pair]:
                            try:
                                callback(self.prices[pair])
                            except Exception as e:
                                logger.error(f"Error in price subscriber callback: {str(e)}")
            except Exception as e:
                logger.error(f"Error fetching price for {input_mint} -> {output_mint}: {str(e)}")
    
    async def start(self):
        """Start the price feed"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting price feed")
        
        while self.is_running:
            await self.fetch_prices()
            await asyncio.sleep(self.update_interval)
    
    def stop(self):
        """Stop the price feed"""
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
        logger.info("Stopped price feed")
    
    def start_background_task(self):
        """Start the price feed in the background"""
        if not self.is_running:
            self.task = asyncio.create_task(self.start())
            logger.info("Started price feed in background")
    
    def get_latest_price(self, input_mint: str, output_mint: str) -> Dict:
        """Get the latest price for a token pair"""
        pair = (input_mint, output_mint)
        return self.prices.get(pair, {"price": 0})
    
    async def initialize_from_db(self):
        """Initialize token pairs to monitor from the database"""
        try:
            # Get all tokens
            tokens = self.db.query(models.Token).all()
            
            # Get USDC token for price comparison
            usdc_token = self.db.query(models.Token).filter(models.Token.symbol == "USDC").first()
            if not usdc_token:
                logger.error("USDC token not found in database")
                return
            
            # Add all token/USDC pairs to monitor
            for token in tokens:
                if token.symbol != "USDC":  # Skip USDC/USDC pair
                    self.add_token_pair(token.mint_address, usdc_token.mint_address)
                    self.add_token_pair(usdc_token.mint_address, token.mint_address)
            
            logger.info(f"Initialized {len(self.token_pairs)} token pairs from database")
        except Exception as e:
            logger.error(f"Error initializing token pairs from database: {str(e)}")
