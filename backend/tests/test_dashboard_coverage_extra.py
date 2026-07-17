import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.dashboard.market import MarketDashboard
from app.dashboard.portfolio import PortfolioDashboard
from app.dashboard.news import NewsDashboard
from app.dashboard.cache import DashboardCache
from pydantic import BaseModel

class DummyModel(BaseModel):
    title: str

@pytest.mark.asyncio
async def test_market_dashboard_exception_in_list():
    dash = MarketDashboard()
    
    # An object that raises exception on attribute access
    class BadData:
        @property
        def value(self):
            raise Exception("Bad property")
            
    with patch("app.market_data.service.MarketDataService.get_market_indices", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [BadData()]
        res = await dash.get_section()
        assert len(res["widgets"]) == 0

@pytest.mark.asyncio
async def test_portfolio_dashboard_success_path():
    dash = PortfolioDashboard(AsyncMock())
    with patch("app.portfolio.engine.PortfolioEngine.get_user_portfolios_summary", new_callable=AsyncMock, create=True) as mock_get:
        mock_get.return_value = {
            "total_value": 200000.0,
            "daily_change": 1500.0,
            "daily_change_percent": 0.75
        }
        res = await dash.get_section(user_id=1)
        assert len(res["widgets"]) == 1
        assert res["widgets"][0]["value"] == 200000.0

@pytest.mark.asyncio
async def test_news_dashboard_success_path():
    dash = NewsDashboard(AsyncMock())
    with patch("app.news.engine.NewsIntelligenceEngine.get_recent_news", new_callable=AsyncMock, create=True) as mock_recent, \
         patch("app.news.engine.NewsIntelligenceEngine.get_portfolio_news", new_callable=AsyncMock, create=True) as mock_port:
         
        mock_recent_item = MagicMock()
        mock_recent_item.headline = "Breaking"
        mock_recent.return_value = [mock_recent_item]
        mock_port.return_value = []
        
        res = await dash.get_section(user_id=1)
        assert len(res["widgets"]) == 1
        assert res["widgets"][0]["value"] == 1
        
@pytest.mark.asyncio
async def test_cache_pydantic_model():
    class DummyCacheObj:
        @DashboardCache.cached(ttl_seconds=10)
        async def get_model(self):
            return DummyModel(title="test")
            
        @DashboardCache.cached(ttl_seconds=10)
        async def get_model_list(self):
            return [DummyModel(title="test1")]
            
    with patch("app.dashboard.cache.get_redis_client", return_value=AsyncMock()):
        obj = DummyCacheObj()
        await obj.get_model()
        await obj.get_model_list()
