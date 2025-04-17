from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from ..db.database import get_db
from ..db import models
from ..auth import get_current_active_user
from ..risk.manager import RiskManager

router = APIRouter(prefix="/risk", tags=["Risk Management"])

@router.get("/trade/{opportunity_id}", response_model=Dict)
async def assess_trade_risk(
    opportunity_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    risk_manager = RiskManager(db)
    risk_assessment = risk_manager.assess_trade_risk(current_user.id, opportunity_id)
    return risk_assessment

@router.get("/portfolio", response_model=Dict)
async def assess_portfolio_risk(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    risk_manager = RiskManager(db)
    portfolio_risk = risk_manager.check_portfolio_risk(current_user.id)
    return portfolio_risk
