import pytest
from unittest.mock import AsyncMock, patch
from app.dashboard.engine import DashboardEngine
from app.dashboard.schemas import DashboardResponse

@pytest.mark.asyncio
async def test_dashboard_engine_all_sections():
    mock_db = AsyncMock()
    engine = DashboardEngine(mock_db)
    
    # We will patch the individual dashboard modules to return mock data instantly
    with patch("app.dashboard.overview.OverviewDashboard.get_section", new_callable=AsyncMock) as m_ov, \
         patch("app.dashboard.portfolio.PortfolioDashboard.get_section", new_callable=AsyncMock) as m_pf, \
         patch("app.dashboard.market.MarketDashboard.get_section", new_callable=AsyncMock) as m_mk, \
         patch("app.dashboard.news.NewsDashboard.get_section", new_callable=AsyncMock) as m_nw, \
         patch("app.dashboard.wealth.WealthDashboard.get_section", new_callable=AsyncMock) as m_wl, \
         patch("app.dashboard.watchlist.WatchlistDashboard.get_section", new_callable=AsyncMock) as m_wt, \
         patch("app.dashboard.calendar.CalendarDashboard.get_section", new_callable=AsyncMock) as m_cl, \
         patch("app.dashboard.insights.InsightsDashboard.get_section", new_callable=AsyncMock) as m_in:
         
         m_ov.return_value = {"widgets": []}
         m_pf.return_value = {"widgets": []}
         m_mk.return_value = {"widgets": []}
         m_nw.return_value = {"widgets": []}
         m_wl.return_value = {"widgets": []}
         m_wt.return_value = {"widgets": []}
         m_cl.return_value = {"widgets": []}
         m_in.return_value = {"widgets": []}
         
         res = await engine.get_dashboard(user_id=1)
         
         assert isinstance(res, DashboardResponse)
         assert res.overview is not None
         assert res.portfolio is not None
         assert res.market is not None
         assert res.news is not None
         assert res.wealth is not None
         assert res.watchlist is not None
         assert res.calendar is not None
         assert res.insights is not None
         
         assert len(res.overview.widgets) == 0

@pytest.mark.asyncio
async def test_dashboard_engine_partial_sections():
    mock_db = AsyncMock()
    engine = DashboardEngine(mock_db)
    
    with patch("app.dashboard.overview.OverviewDashboard.get_section", new_callable=AsyncMock) as m_ov, \
         patch("app.dashboard.portfolio.PortfolioDashboard.get_section", new_callable=AsyncMock) as m_pf:
         
         m_ov.return_value = {"widgets": []}
         
         # Request only overview
         res = await engine.get_dashboard(user_id=1, sections=["overview"])
         
         assert res.overview is not None
         assert res.portfolio is None # Should not be fetched
         assert not m_pf.called

@pytest.mark.asyncio
async def test_dashboard_engine_graceful_degradation():
    mock_db = AsyncMock()
    engine = DashboardEngine(mock_db)
    
    with patch("app.dashboard.overview.OverviewDashboard.get_section", new_callable=AsyncMock) as m_ov:
         # Simulate an exception in one of the upstream modules
         m_ov.side_effect = Exception("Upstream API Down")
         
         res = await engine.get_dashboard(user_id=1, sections=["overview"])
         
         # The dashboard should catch this via asyncio.gather(return_exceptions=True) and return empty
         assert res.overview is not None
         assert len(res.overview.widgets) == 0
