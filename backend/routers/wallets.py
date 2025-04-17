from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.database import get_db
from ..db import models
from ..schemas import WalletCreate, WalletResponse, TokenBalanceResponse
from ..auth import get_current_active_user
from ..utils.encryption import encrypt_data

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.get("/", response_model=List[WalletResponse])
async def get_wallets(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    wallets = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).all()
    return wallets

@router.post("/", response_model=WalletResponse)
async def create_wallet(
    wallet: WalletCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if wallet already exists
    db_wallet = db.query(models.Wallet).filter(
        models.Wallet.user_id == current_user.id,
        models.Wallet.address == wallet.address
    ).first()
    
    if db_wallet:
        raise HTTPException(status_code=400, detail="Wallet already exists")
    
    # Create new wallet
    encrypted_private_key = None
    if wallet.private_key:
        encrypted_private_key = encrypt_data(wallet.private_key)
    
    db_wallet = models.Wallet(
        user_id=current_user.id,
        name=wallet.name,
        address=wallet.address,
        is_active=wallet.is_active,
        encrypted_private_key=encrypted_private_key
    )
    
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    
    return db_wallet

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return wallet

@router.get("/{wallet_id}/balances", response_model=List[TokenBalanceResponse])
async def get_wallet_balances(
    wallet_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id,
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    balances = db.query(models.TokenBalance).filter(
        models.TokenBalance.wallet_id == wallet_id
    ).all()
    
    return balances
