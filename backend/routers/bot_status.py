from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from ..db.database import get_db
from ..db import models
from ..schemas import BotStatusUpdate, BotStatusResponse
from ..auth import get_current_active_user
from ..arbitrage.engine import ArbitrageEngine
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_status")

router = APIRouter(prefix="/bot", tags=["Bot Status"])

# Global bot status
bot_status = {
    "active": False,
    "last_updated": datetime.now()
}

# Background task for continuous arbitrage scanning
async def continuous_scan(user_id: int, db: Session):
    engine = ArbitrageEngine(db)
    
    while bot_status["active"]:
        try:
            logger.info("Scanning for arbitrage opportunities...")
            await engine.find_arbitrage_opportunities(user_id)
            
            # Get trading settings
            trading_settings = db.query(models.Setting).filter(
                models.Setting.user_id == user_id,
                models.Setting.category == "trading"
            ).first()
            
            if trading_settings and trading_settings.settings.get("auto_execute", False):
                # Get active opportunities
                opportunities = db.query(models.Opportunity).filter(
                    models.Opportunity.status == "active"
                ).all()
                
                # Get user's wallet
                wallet = db.query(models.Wallet).filter(
                    models.Wallet.user_id == user_id,
                    models.Wallet.is_active == True
                ).first()
                
                if wallet and opportunities:
                    # Execute the most profitable opportunity
                    most_profitable = max(opportunities, key=lambda o: o.price_diff_percent)
                    logger.info(f"Auto-executing opportunity {most_profitable.id}")
                    await engine.execute_arbitrage(most_profitable.id, wallet.id)
            
            # Wait before next scan
            await asyncio.sleep(5)  # 5 seconds between scans
        except Exception as e:
            logger.error(f"Error in continuous scan: {str(e)}")
            await asyncio.sleep(10)  # Wait longer on error

@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(
    current_user: models.User = Depends(get_current_active_user)
):
    return BotStatusResponse(
        active=bot_status["active"],
        last_updated=bot_status["last_updated"]
    )

@router.post("/status", response_model=BotStatusResponse)
async def update_bot_status(
    status_update: BotStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    bot_status["active"] = status_update.active
    bot_status["last_updated"] = datetime.now()
    
    if status_update.active:
        # Start continuous scanning in the background
        background_tasks.add_task(continuous_scan, current_user.id, db)
        logger.info("Bot activated")
    else:
        logger.info("Bot deactivated")
    
    return BotStatusResponse(
        active=bot_status["active"],
        last_updated=bot_status["last_updated"]
    )
