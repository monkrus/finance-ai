import pytest
from app.schemas.portfolio import Holding
from app.market_data.models import CompanyProfile
from app.portfolio.performance import PerformanceEngine
from app.portfolio.allocation import AllocationEngine
from app.portfolio.risk import PortfolioRiskEngine
from app.portfolio.benchmark import BenchmarkEngine

@pytest.fixture
def mock_profiles():
    return {
        "AAPL": CompanyProfile(ticker="AAPL", company_name="Apple", sector="Technology", industry="Consumer Electronics", beta=1.2, price=150.0),
        "MSFT": CompanyProfile(ticker="MSFT", company_name="Microsoft", sector="Technology", industry="Software", beta=1.1, price=300.0),
        "NVDA": CompanyProfile(ticker="NVDA", company_name="NVIDIA", sector="Technology", industry="Semiconductors", beta=1.8, price=400.0),
        "RELIANCE": CompanyProfile(ticker="RELIANCE", company_name="Reliance", sector="Energy", industry="Oil & Gas", beta=1.0, price=2500.0),
        "TCS": CompanyProfile(ticker="TCS", company_name="TCS", sector="Technology", industry="IT Services", beta=0.8, price=3500.0),
    }

def test_single_stock_portfolio(mock_profiles):
    holdings = [
        Holding(
            id=1, portfolio_id=1, ticker_symbol="AAPL", quantity=10, 
            average_buy_price=100.0, cost_basis=1000.0, realized_gain_loss=0.0,
            current_price=150.0, market_value=1500.0, unrealized_gain_loss=500.0,
            unrealized_gain_loss_pct=50.0, sector="Technology", industry="Consumer Electronics",
            asset_type="Stock"
        )
    ]
    
    # 1. Performance
    perf = PerformanceEngine().compute(holdings)
    assert perf.portfolio_value == 1500.0
    assert perf.total_return_pct == 50.0
    
    # 2. Allocation
    alloc = AllocationEngine().compute(holdings, 1500.0)
    assert alloc.sector_allocation["Technology"] == 1.0
    assert alloc.diversification_score == 0.0 # Single stock HHI = 1.0 -> (1 - 1) * 100 = 0
    
    # 3. Risk
    risk = PortfolioRiskEngine().compute(holdings, mock_profiles, 1500.0)
    assert risk.portfolio_beta == 1.2
    
    # 4. Benchmark
    bench = BenchmarkEngine().compare(perf)
    assert bench["benchmark_return_pct"] is None
    
def test_diversified_portfolio(mock_profiles):
    holdings = [
        Holding(id=1, portfolio_id=1, ticker_symbol="AAPL", quantity=10, average_buy_price=100, cost_basis=1000.0, market_value=1500.0, current_price=150, unrealized_gain_loss=500.0, unrealized_gain_loss_pct=50, realized_gain_loss=0.0, sector="Technology", asset_type="Stock"),
        Holding(id=2, portfolio_id=1, ticker_symbol="RELIANCE", quantity=1, average_buy_price=2000, cost_basis=2000.0, market_value=2500.0, current_price=2500, unrealized_gain_loss=500.0, unrealized_gain_loss_pct=25, realized_gain_loss=0.0, sector="Energy", asset_type="Stock"),
        Holding(id=3, portfolio_id=1, ticker_symbol="TCS", quantity=1, average_buy_price=3000, cost_basis=3000.0, market_value=3500.0, current_price=3500, unrealized_gain_loss=500.0, unrealized_gain_loss_pct=16.66, realized_gain_loss=0.0, sector="Technology", asset_type="Stock"),
    ]
    total_val = 1500.0 + 2500.0 + 3500.0 # 7500.0
    
    perf = PerformanceEngine().compute(holdings)
    assert perf.portfolio_value == 7500.0
    assert perf.total_return_pct == ((7500.0 - 6000.0) / 6000.0) * 100.0 # 25%
    
    alloc = AllocationEngine().compute(holdings, 7500.0)
    assert abs(alloc.sector_allocation["Technology"] - ((1500.0 + 3500.0) / 7500.0)) < 0.001
    assert abs(alloc.sector_allocation["Energy"] - (2500.0 / 7500.0)) < 0.001
    assert alloc.diversification_score > 0.0 # Should be somewhat diversified
    
    risk = PortfolioRiskEngine().compute(holdings, mock_profiles, 7500.0)
    expected_beta = (1.2 * (1500/7500)) + (1.0 * (2500/7500)) + (0.8 * (3500/7500))
    assert abs(risk.portfolio_beta - expected_beta) < 0.01

def test_high_concentration_portfolio(mock_profiles):
    holdings = [
        Holding(id=1, portfolio_id=1, ticker_symbol="NVDA", quantity=100, average_buy_price=200, cost_basis=20000.0, current_price=400, market_value=40000.0, unrealized_gain_loss=20000.0, unrealized_gain_loss_pct=100, realized_gain_loss=0.0, sector="Technology", asset_type="Stock"),
        Holding(id=2, portfolio_id=1, ticker_symbol="MSFT", quantity=1, average_buy_price=250, cost_basis=250.0, current_price=300, market_value=300.0, unrealized_gain_loss=50.0, unrealized_gain_loss_pct=20, realized_gain_loss=0.0, sector="Technology", asset_type="Stock"),
    ]
    total_val = 40300.0
    alloc = AllocationEngine().compute(holdings, total_val)
    # HHI should be very close to 1.0 (approx 0.98), so diversification score should be very low (approx 2)
    assert alloc.diversification_score < 10.0
    
def test_loss_making_portfolio(mock_profiles):
    holdings = [
        Holding(id=1, portfolio_id=1, ticker_symbol="AAPL", quantity=10, average_buy_price=200, cost_basis=2000.0, current_price=150, market_value=1500.0, unrealized_gain_loss=-500.0, unrealized_gain_loss_pct=-25, realized_gain_loss=0.0, sector="Technology", asset_type="Stock"),
    ]
    perf = PerformanceEngine().compute(holdings)
    assert perf.total_unrealized_gl == -500.0
    assert perf.total_return_pct == -25.0

def test_empty_portfolio():
    alloc = AllocationEngine().compute([], 0.0)
    assert alloc.diversification_score == 0.0

def test_zero_market_value_holding():
    holdings = [
        Holding(id=1, portfolio_id=1, ticker_symbol="AAPL", quantity=10, average_buy_price=200, cost_basis=2000.0, current_price=0, market_value=0.0, unrealized_gain_loss=-2000.0, unrealized_gain_loss_pct=-100, realized_gain_loss=0.0, sector="Technology", asset_type="Stock"),
    ]
    alloc = AllocationEngine().compute(holdings, 1000.0) # total_value > 0 to bypass first check
    assert len(alloc.sector_allocation) == 0
