from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from ..db.database import get_db
from ..db import models
from ..schemas import DashboardResponse, DashboardStats
from ..auth import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user's wallets
    wallets = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).all()
    wallet_ids = [wallet.id for wallet in wallets]
    
    # Get total profit
    total_profit = db.query(models.Trade).filter(
        models.Trade.wallet_id.in_(wallet_ids),
        models.Trade.status == "completed"
    ).with_entities(
        db.func.sum(models.Trade.profit_usd)
    ).scalar() or Decimal("0")
    
    # Get active opportunities count
    active_opportunities = db.query(models.Opportunity).filter(
        models.Opportunity.status == "active"
    ).count()
    
    # Get trades executed count
    trades_executed = db.query(models.Trade).filter(
        models.Trade.wallet_id.in_(wallet_ids)
    ).count()
    
    # Get average response time (mock data for now)
    avg_response_time_ms = 238
    
    # Get recent opportunities
    recent_opportunities = db.query(models.Opportunity).filter(
        models.Opportunity.status == "active"
    ).order_by(models.Opportunity.created_at.desc()).limit(5).all()
    
    # Get recent trades
    recent_trades = db.query(models.Trade).filter(
        models.Trade.wallet_id.in_(wallet_ids)
    ).order_by(models.Trade.created_at.desc()).limit(5).all()
    
    # Get performance data for the last 30 days
    performance_data = []
    today = datetime.now().date()
    
    for i in range(30):
        date = today - timedelta(days=i)
        
        # Get metrics for the day
        metrics = db.query(models.PerformanceMetric).filter(
            models.PerformanceMetric.user_id == current_user.id,
            models.PerformanceMetric.date == date
        ).first()
        
        if metrics:
            performance_data.append({
                "date": date.strftime("%m/%d"),
                "profit": float(metrics.profit_usd),
                "trades": metrics.trades_count,
                "opportunities": metrics.opportunities_count
            })
        else:
            # Generate mock data if no metrics exist
            base_profit = 50 + (30 - i) * 5 + (30 - i) % 10
            trades = 10 + (30 - i) // 3
            opportunities = trades * 2
            
            performance_data.append({
                "date": date.strftime("%m/%d"),
                "profit": base_profit,
                "trades": trades,
                "opportunities": opportunities
            })
    
    # Reverse to get chronological order
    performance_data.reverse()
    
    # Create dashboard response
    dashboard = DashboardResponse(
        stats=DashboardStats(
            total_profit=total_profit,
            active_opportunities=active_opportunities,
            trades_executed=trades_executed,
            avg_response_time_ms=avg_response_time_ms
        ),
        recent_opportunities=recent_opportunities,
        recent_trades=recent_trades,
        performance_data=performance_data
    )
    
    return dashboard
