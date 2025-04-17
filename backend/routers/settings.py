from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..db.database import get_db
from ..db import models
from ..schemas import SettingResponse, SettingUpdate
from ..auth import get_current_active_user

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/", response_model=Dict[str, Any])
async def get_settings(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get all settings for user
    settings = db.query(models.Setting).filter(models.Setting.user_id == current_user.id).all()
    
    # Convert to dictionary
    settings_dict = {}
    for setting in settings:
        settings_dict[setting.category] = setting.settings
    
    return settings_dict

@router.get("/{category}", response_model=Dict[str, Any])
async def get_category_settings(
    category: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get settings for category
    setting = db.query(models.Setting).filter(
        models.Setting.user_id == current_user.id,
        models.Setting.category == category
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Settings for category '{category}' not found")
    
    return setting.settings

@router.put("/{category}", response_model=Dict[str, Any])
async def update_category_settings(
    category: str,
    setting_update: SettingUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get settings for category
    setting = db.query(models.Setting).filter(
        models.Setting.user_id == current_user.id,
        models.Setting.category == category
    ).first()
    
    if not setting:
        # Create new settings
        setting = models.Setting(
            user_id=current_user.id,
            category=category,
            settings=setting_update.settings
        )
        db.add(setting)
    else:
        # Update existing settings
        setting.settings = setting_update.settings
    
    db.commit()
    db.refresh(setting)
    
    return setting.settings
