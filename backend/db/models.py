from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Date, Text, Numeric, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    wallets = relationship("Wallet", back_populates="user")
    settings = relationship("Setting", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")
    performance_metrics = relationship("PerformanceMetric", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String)
    address = Column(String)
    is_active = Column(Boolean, default=True)
    encrypted_private_key = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="wallets")
    token_balances = relationship("TokenBalance", back_populates="wallet")
    trades = relationship("Trade", back_populates="wallet")

    __table_args__ = (UniqueConstraint('user_id', 'address', name='_user_address_uc'),)

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String)
    name = Column(String)
    mint_address = Column(String, unique=True, index=True)
    decimals = Column(Integer)
    logo_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    token_balances = relationship("TokenBalance", back_populates="token")
    opportunities = relationship("Opportunity", back_populates="token")
    trades = relationship("Trade", back_populates="token")

class Dex(Base):
    __tablename__ = "dexes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    api_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    buy_opportunities = relationship("Opportunity", foreign_keys="Opportunity.buy_dex_id", back_populates="buy_dex")
    sell_opportunities = relationship("Opportunity", foreign_keys="Opportunity.sell_dex_id", back_populates="sell_dex")
    buy_trades = relationship("Trade", foreign_keys="Trade.buy_dex_id", back_populates="buy_dex")
    sell_trades = relationship("Trade", foreign_keys="Trade.sell_dex_id", back_populates="sell_dex")

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"))
    buy_dex_id = Column(Integer, ForeignKey("dexes.id"))
    sell_dex_id = Column(Integer, ForeignKey("dexes.id"))
    buy_price = Column(Numeric(24, 12))
    sell_price = Column(Numeric(24, 12))
    price_diff_percent = Column(Numeric(10, 6))
    potential_profit_usd = Column(Numeric(18, 6))
    status = Column(String)  # active, executing, completed, expired, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    token = relationship("Token", back_populates="opportunities")
    buy_dex = relationship("Dex", foreign_keys=[buy_dex_id], back_populates="buy_opportunities")
    sell_dex = relationship("Dex", foreign_keys=[sell_dex_id], back_populates="sell_opportunities")
    trades = relationship("Trade", back_populates="opportunity")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    token_id = Column(Integer, ForeignKey("tokens.id"))
    buy_dex_id = Column(Integer, ForeignKey("dexes.id"))
    sell_dex_id = Column(Integer, ForeignKey("dexes.id"))
    buy_price = Column(Numeric(24, 12))
    sell_price = Column(Numeric(24, 12))
    amount = Column(Numeric(24, 12))
    profit_usd = Column(Numeric(18, 6))
    status = Column(String)  # completed, failed, pending
    tx_hash_buy = Column(String, nullable=True)
    tx_hash_sell = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    opportunity = relationship("Opportunity", back_populates="trades")
    wallet = relationship("Wallet", back_populates="trades")
    token = relationship("Token", back_populates="trades")
    buy_dex = relationship("Dex", foreign_keys=[buy_dex_id], back_populates="buy_trades")
    sell_dex = relationship("Dex", foreign_keys=[sell_dex_id], back_populates="sell_trades")

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    category = Column(String)  # general, trading, dexes, notifications, advanced
    settings = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="settings")

    __table_args__ = (UniqueConstraint('user_id', 'category', name='_user_category_uc'),)

class TokenBalance(Base):
    __tablename__ = "token_balances"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"))
    token_id = Column(Integer, ForeignKey("tokens.id"))
    balance = Column(Numeric(24, 12), default=0)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    wallet = relationship("Wallet", back_populates="token_balances")
    token = relationship("Token", back_populates="token_balances")

    __table_args__ = (UniqueConstraint('wallet_id', 'token_id', name='_wallet_token_uc'),)

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    service = Column(String)
    encrypted_key = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="api_keys")

    __table_args__ = (UniqueConstraint('user_id', 'service', name='_user_service_uc'),)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date)
    profit_usd = Column(Numeric(18, 6), default=0)
    trades_count = Column(Integer, default=0)
    opportunities_count = Column(Integer, default=0)
    avg_response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="performance_metrics")

    __table_args__ = (UniqueConstraint('user_id', 'date', name='_user_date_uc'),)
