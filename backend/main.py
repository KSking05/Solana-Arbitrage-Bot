from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, wallets, opportunities, trades, settings, dashboard, bot_status, risk
from backend.db.database import get_db, Base, engine
from sqlalchemy.orm import Session
from backend.realtime.websocket_server import WebSocketServer
import logging
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("arbitrage_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("arbitrage_bot")

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")

# Create FastAPI app
app = FastAPI(title="Solana Arbitrage Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket server
websocket_server = WebSocketServer()

# Include routers
app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(opportunities.router)
app.include_router(trades.router)
app.include_router(settings.router)
app.include_router(dashboard.router)
app.include_router(bot_status.router)
app.include_router(risk.router)

@app.get("/")
async def root():
    return {"message": "Solana Arbitrage Bot API"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

@app.on_event("startup")
async def startup_event():
    # Start WebSocket server
    try:
        websocket_port = int(os.getenv("WEBSOCKET_PORT", 8765))
        asyncio.create_task(websocket_server.start(port=websocket_port))
        logger.info(f"WebSocket server starting on port {websocket_port}")
    except Exception as e:
        logger.error(f"Failed to start WebSocket server: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
