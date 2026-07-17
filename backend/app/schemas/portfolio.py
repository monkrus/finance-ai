from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Analytics / Metrics ---
class PerformanceMetrics(BaseModel):
    portfolio_value: float
    total_unrealized_gl: float
    total_realized_gl: float
    total_return_pct: float
    daily_return_pct: Optional[float] = None
    ytd_return_pct: Optional[float] = None
    cagr: Optional[float] = None
    time_weighted_return: Optional[float] = None
    max_drawdown: Optional[float] = None

class AllocationMetrics(BaseModel):
    asset_allocation: dict[str, float]
    sector_allocation: dict[str, float]
    industry_allocation: dict[str, float]
    country_allocation: dict[str, float]
    currency_allocation: dict[str, float]
    top_holdings: List[dict]
    diversification_score: float

class RiskMetrics(BaseModel):
    portfolio_beta: float
    portfolio_volatility: Optional[float] = None
    portfolio_sharpe: Optional[float] = None
    portfolio_sortino: Optional[float] = None

class PortfolioAnalytics(BaseModel):
    performance: PerformanceMetrics
    allocation: AllocationMetrics
    risk: RiskMetrics

# --- Transactions ---
class TransactionBase(BaseModel):
    transaction_type: str
    execution_date: datetime
    quantity: float
    price_per_unit: float
    fees: float = 0.0
    taxes: float = 0.0
    currency: str = "USD"
    holding_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    ticker_symbol: Optional[str] = None # For buys/sells where holding ID might not exist yet

class Transaction(TransactionBase):
    id: int
    portfolio_id: int
    total_amount: float

    class Config:
        from_attributes = True

# --- Holdings ---
class HoldingBase(BaseModel):
    ticker_symbol: str
    asset_type: str = "Stock"

class Holding(HoldingBase):
    id: int
    portfolio_id: int
    quantity: float
    average_buy_price: float
    cost_basis: float
    realized_gain_loss: float
    
    # Dynamically calculated fields for Analytics
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_gain_loss: Optional[float] = None
    unrealized_gain_loss_pct: Optional[float] = None
    weight: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None

    class Config:
        from_attributes = True

# --- Portfolios ---
class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None
    currency: str = "USD"
    is_public: bool = False

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    holdings: List[Holding] = []
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True
