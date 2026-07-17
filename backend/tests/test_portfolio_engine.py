import pytest
from unittest.mock import AsyncMock
from app.models.portfolio import Portfolio, Holding
from app.portfolio.engine import PortfolioEngine
from app.market_data.models import CompanyProfile, StockQuote
from app.core.exceptions import FinPilotException

@pytest.mark.asyncio
async def test_portfolio_engine_analytics(db_session, test_user):
    portfolio = Portfolio(user_id=test_user.id, name="Test Analytics")
    db_session.add(portfolio)
    await db_session.flush()
    
    h1 = Holding(portfolio_id=portfolio.id, ticker_symbol="AAPL", asset_type="Stock", quantity=100, average_buy_price=100, cost_basis=10000)
    db_session.add(h1)
    await db_session.commit()
    
    mock_md = AsyncMock()
    mock_md.get_quote.return_value = StockQuote(
        ticker="AAPL", price=150.0, volume=1000, 
        timestamp=1704067200, change=0, change_percent=0
    )
    mock_md.get_company_profile.return_value = CompanyProfile(
        ticker="AAPL", company_name="Apple Inc.", sector="Technology", 
        industry="Consumer Electronics", country="US", currency="USD", beta=1.2
    )
    
    engine = PortfolioEngine(market_data_service=mock_md)
    
    analytics = await engine.get_portfolio_analytics(db_session, portfolio.id)
    
    assert analytics.performance.portfolio_value == 15000.0
    assert analytics.performance.total_unrealized_gl == 5000.0
    assert analytics.performance.total_return_pct > 0
    assert analytics.allocation.diversification_score >= 0
    
@pytest.mark.asyncio
async def test_portfolio_engine_404(db_session):
    mock_md = AsyncMock()
    engine = PortfolioEngine(market_data_service=mock_md)
    with pytest.raises(FinPilotException) as exc:
        await engine.get_portfolio_analytics(db_session, 9999)
    assert exc.value.status_code == 404
