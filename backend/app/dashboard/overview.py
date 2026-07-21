import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import OverviewSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache
from app.dashboard.wealth import WealthDashboard
from app.dashboard.portfolio import PortfolioDashboard
from app.dashboard.market import MarketDashboard
from app.dashboard.news import NewsDashboard

class OverviewDashboard:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Cache overview for 60 seconds
    @DashboardCache.cached(ttl_seconds=60)
    async def get_section(self, user_id: int) -> dict:
        wealth_dash = WealthDashboard(self.db)
        portfolio_dash = PortfolioDashboard(self.db)
        
        # Sequential: both use the same request session, unsafe to run
        # concurrently (see engine.py). Cached, so latency is a non-issue.
        w_data = await wealth_dash.get_section(user_id)
        p_data = await portfolio_dash.get_section(user_id)
        
        widgets = []
        
        # Extract net worth from wealth widgets
        for w in w_data.get("widgets", []):
            if w.get("title") == "Net Worth":
                widgets.append(w)
            if w.get("title") == "Financial Health":
                widgets.append(w)
                
        # Extract portfolio value from portfolio widgets
        for w in p_data.get("widgets", []):
            if w.get("title") == "Total Portfolio Value":
                widgets.append(w)
        
        return {"widgets": widgets}
