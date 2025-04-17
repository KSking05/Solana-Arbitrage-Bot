from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Wallet schemas
class WalletBase(BaseModel):
    name: str
    address: str
    is_active: bool = True

class WalletCreate(WalletBase):
    private_key: Optional[str] = None

class WalletResponse(WalletBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Token (cryptocurrency) schemas
class TokenBase(BaseModel):
    symbol: str
    name: str
    mint_address: str
    decimals: int
    logo_url: Optional[str] = None

class TokenCreate(TokenBase):
    pass

class TokenResponse(TokenBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# DEX schemas
class DexBase(BaseModel):
    name: str
    api_url: Optional[str] = None
    is_active: bool = True

class DexCreate(DexBase):
    pass

class DexResponse(DexBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Opportunity schemas
class OpportunityBase(BaseModel):
    token_id: int
    buy_dex_id: int
    sell_dex_id: int
    buy_price: Decimal
    sell_price: Decimal
    price_diff_percent: Decimal
    potential_profit_usd: Decimal
    status: str

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityResponse(OpportunityBase):
    id: int
    created_at: datetime
    token: TokenResponse
    buy_dex: DexResponse
    sell_dex: DexResponse

    class Config:
        orm_mode = True

# Trade schemas
class TradeBase(BaseModel):
    opportunity_id: Optional[int] = None
    wallet_id: int
    token_id: int
    buy_dex_id: int
    sell_dex_id: int
    buy_price: Decimal
    sell_price: Decimal
    amount: Decimal
    profit_usd: Decimal
    status: str
    tx_hash_buy: Optional[str] = None
    tx_hash_sell: Optional[str] = None
    error_message: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class TradeResponse(TradeBase):
    id: int
    created_at: datetime
    token: TokenResponse
    buy_dex: DexResponse
    sell_dex: DexResponse

    class Config:
        orm_mode = True

# Settings schemas
class SettingBase(BaseModel):
    category: str
    settings: Dict[str, Any]

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    settings: Dict[str, Any]

class SettingResponse(SettingBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Token balance schemas
class TokenBalanceBase(BaseModel):
    wallet_id: int
    token_id: int
    balance: Decimal

class TokenBalanceCreate(TokenBalanceBase):
    pass

class TokenBalanceResponse(TokenBalanceBase):
    id: int
    last_updated_at: datetime
    token: TokenResponse

    class Config:
        orm_mode = True

# API key schemas
class ApiKeyBase(BaseModel):
    service: str
    key: str

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyResponse(BaseModel):
    id: int
    user_id: int
    service: str
    created_at: datetime

    class Config:
        orm_mode = True

# Performance metric schemas
class PerformanceMetricBase(BaseModel):
    date: date
    profit_usd: Decimal
    trades_count: int
    opportunities_count: int
    avg_response_time_ms: Optional[int] = None

class PerformanceMetricCreate(PerformanceMetricBase):
    pass

class PerformanceMetricResponse(PerformanceMetricBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Dashboard response schemas
class DashboardStats(BaseModel):
    total_profit: Decimal
    active_opportunities: int
    trades_executed: int
    avg_response_time_ms: int

class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_opportunities: List[OpportunityResponse]
    recent_trades: List[TradeResponse]
    performance_data: List[Dict[str, Any]]

# Bot status schemas
class BotStatusUpdate(BaseModel):
    active: bool

class BotStatusResponse(BaseModel):
    active: bool
    last_updated: datetime

# Trade execution schemas
class TradeExecution(BaseModel):
    opportunity_id: str
