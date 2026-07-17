import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.dashboard.engine import DashboardEngine

@pytest.mark.asyncio
async def test_dashboard_performance_parallel_execution():
    """
    Verifies that the dashboard engine executes downstream module fetches in parallel
    by ensuring the total time is approximately the max of individual delays,
    not the sum of delays.
    """
    mock_db = AsyncMock()
    engine = DashboardEngine(mock_db)
    
    async def m_ov_side_effect(*args, **kwargs):
        await asyncio.sleep(0.1)
        return {"widgets": []}
    
    async def m_pf_side_effect(*args, **kwargs):
        await asyncio.sleep(0.15)
        return {"widgets": []}
        
    async def m_mk_side_effect(*args, **kwargs):
        await asyncio.sleep(0.05)
        return {"widgets": []}
    
    with patch("app.dashboard.overview.OverviewDashboard.get_section", new_callable=AsyncMock) as m_ov, \
         patch("app.dashboard.portfolio.PortfolioDashboard.get_section", new_callable=AsyncMock) as m_pf, \
         patch("app.dashboard.market.MarketDashboard.get_section", new_callable=AsyncMock) as m_mk:
         
         m_ov.side_effect = m_ov_side_effect
         m_pf.side_effect = m_pf_side_effect
         m_mk.side_effect = m_mk_side_effect
         
         import time
         start = time.perf_counter()
         res = await engine.get_dashboard(user_id=1, sections=["overview", "portfolio", "market"])
         elapsed = time.perf_counter() - start
         
         # If sequential, it would take 0.1 + 0.15 + 0.05 = 0.30 seconds
         # If parallel, it should take ~0.15 seconds
         assert elapsed < 0.25 # well under sequential time
         assert elapsed >= 0.15 # at least max time
         
         assert res.overview is not None
         assert res.portfolio is not None
         assert res.market is not None
