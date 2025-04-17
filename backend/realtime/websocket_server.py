import asyncio
import json
import logging
import websockets
from typing import Dict, Set, Any
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..realtime.price_feed import PriceFeed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket_server")

class WebSocketServer:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.price_feed = None
        self.db = None
        logger.info("Initialized WebSocket Server")
    
    async def register(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new client"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
    
    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a client"""
        self.clients.remove(websocket)
        logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def send_to_clients(self, message: Dict[str, Any]):
        """Send a message to all connected clients"""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_str) for client in self.clients],
            return_exceptions=True
        )
    
    async def price_update_callback(self, price_data: Dict[str, Any]):
        """Callback for price updates"""
        await self.send_to_clients({
            "type": "price_update",
            "data": price_data
        })
    
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle a client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(websocket, data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {message}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    async def process_message(self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]):
        """Process a message from a client"""
        message_type = data.get("type")
        
        if message_type == "subscribe":
            # Subscribe to price updates
            token_pair = data.get("token_pair")
            if token_pair and "input_mint" in token_pair and "output_mint" in token_pair:
                input_mint = token_pair["input_mint"]
                output_mint = token_pair["output_mint"]
                
                if self.price_feed:
                    self.price_feed.subscribe(input_mint, output_mint, self.price_update_callback)
                    
                    # Send initial price if available
                    initial_price = self.price_feed.get_latest_price(input_mint, output_mint)
                    if initial_price and "price" in initial_price:
                        await websocket.send(json.dumps({
                            "type": "price_update",
                            "data": initial_price
                        }))
                
                await websocket.send(json.dumps({
                    "type": "subscription_success",
                    "token_pair": token_pair
                }))
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid token pair"
                }))
        
        elif message_type == "unsubscribe":
            # Unsubscribe from price updates
            token_pair = data.get("token_pair")
            if token_pair and "input_mint" in token_pair and "output_mint" in token_pair:
                input_mint = token_pair["input_mint"]
                output_mint = token_pair["output_mint"]
                
                if self.price_feed:
                    self.price_feed.unsubscribe(input_mint, output_mint, self.price_update_callback)
                
                await websocket.send(json.dumps({
                    "type": "unsubscription_success",
                    "token_pair": token_pair
                }))
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid token pair"
                }))
        
        else:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }))
    
    async def start(self, host: str = "0.0.0.0", port: int = 8765):
        """Start the WebSocket server"""
        # Initialize database session
        self.db = next(get_db())
        
        # Initialize price feed
        self.price_feed = PriceFeed(self.db)
        await self.price_feed.initialize_from_db()
        self.price_feed.start_background_task()
        
        # Start WebSocket server
        server = await websockets.serve(self.handle_client, host, port)
        logger.info(f"WebSocket server started on {host}:{port}")
        
        return server
