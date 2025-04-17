from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.database import get_db
from ..db import models
from ..schemas import TradeResponse
from ..auth import get_current_active_user

router = APIRouter(prefix="/trades", tags=["Trades"])

@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user's wallets
    wallets = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).all()
    wallet_ids = [wallet.id for wallet in wallets]
    
    # Get trades for user's wallets
    trades = db.query(models.Trade).filter(
        models.Trade.wallet_id.in_(wallet_ids)
    ).order_by(models.Trade.created_at.desc()).all()
    
    return trades

@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user's wallets
    wallets = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).all()
    wallet_ids = [wallet.id for wallet in wallets]
    
    # Get trade
    trade = db.query(models.Trade).filter(
        models.Trade.id == trade_id,
        models.Trade.wallet_id.in_(wallet_ids)
    ).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return trade
