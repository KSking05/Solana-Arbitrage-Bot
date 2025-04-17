from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..db.database import get_db
from ..db import models
from ..schemas import OpportunityResponse, TradeExecution
from ..auth import get_current_active_user
from ..arbitrage.engine import ArbitrageEngine

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get active opportunities
    opportunities = db.query(models.Opportunity).filter(
        models.Opportunity.status == "active"
    ).order_by(models.Opportunity.price_diff_percent.desc()).all()
    
    return opportunities

@router.post("/scan", response_model=List[OpportunityResponse])
async def scan_opportunities(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Create arbitrage engine
    engine = ArbitrageEngine(db)
    
    # Scan for opportunities in the background
    background_tasks.add_task(engine.find_arbitrage_opportunities, current_user.id)
    
    # Return existing active opportunities
    opportunities = db.query(models.Opportunity).filter(
        models.Opportunity.status == "active"
    ).order_by(models.Opportunity.price_diff_percent.desc()).all()
    
    return opportunities

@router.post("/execute", status_code=status.HTTP_202_ACCEPTED)
async def execute_opportunity(
    trade_execution: TradeExecution,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get opportunity
    opportunity = db.query(models.Opportunity).filter(
        models.Opportunity.id == int(trade_execution.opportunity_id)
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    if opportunity.status != "active":
        raise HTTPException(status_code=400, detail="Opportunity is not active")
    
    # Get user's wallet
    wallet = db.query(models.Wallet).filter(
        models.Wallet.user_id == current_user.id,
        models.Wallet.is_active == True
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="No active wallet found")
    
    # Create arbitrage engine
    engine = ArbitrageEngine(db)
    
    # Execute arbitrage in the background
    background_tasks.add_task(engine.execute_arbitrage, int(trade_execution.opportunity_id), wallet.id)
    
    return {"message": "Arbitrage execution started"}
