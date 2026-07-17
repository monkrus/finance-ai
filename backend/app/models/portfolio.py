from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    currency = Column(String, default="USD", nullable=False)
    is_public = Column(Integer, default=0, nullable=False) # 0=False, 1=True
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    ticker_symbol = Column(String, index=True, nullable=False)
    asset_type = Column(String, default="Stock", nullable=False) # Stock, ETF, Mutual Fund, Cash
    quantity = Column(Float, nullable=False, default=0.0)
    average_buy_price = Column(Float, nullable=False, default=0.0)
    cost_basis = Column(Float, nullable=False, default=0.0)
    realized_gain_loss = Column(Float, nullable=False, default=0.0)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    transactions = relationship("Transaction", back_populates="holding", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    holding_id = Column(Integer, ForeignKey("holdings.id"), nullable=True) # Null for raw cash deposit/withdraw
    
    transaction_type = Column(String, nullable=False) # BUY, SELL, DIVIDEND, SPLIT, BONUS, DEPOSIT, WITHDRAWAL, FEE, TAX
    execution_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    quantity = Column(Float, nullable=False, default=0.0)
    price_per_unit = Column(Float, nullable=False, default=0.0)
    fees = Column(Float, nullable=False, default=0.0)
    taxes = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0) # Quantity * Price + Fees + Taxes (or - for sells)
    currency = Column(String, default="USD", nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    holding = relationship("Holding", back_populates="transactions")
