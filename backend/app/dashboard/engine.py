import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.dashboard.schemas import DashboardResponse
from app.dashboard.overview import OverviewDashboard
from app.dashboard.portfolio import PortfolioDashboard
from app.dashboard.market import MarketDashboard
from app.dashboard.news import NewsDashboard
from app.dashboard.wealth import WealthDashboard
from app.dashboard.watchlist import WatchlistDashboard
from app.dashboard.calendar import CalendarDashboard
from app.dashboard.insights import InsightsDashboard

class DashboardEngine:
    """
    Central orchestration facade for the Dashboard.
    Collects, combines, and caches data from all underlying modules.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_dashboard(self, user_id: int, sections: Optional[List[str]] = None) -> DashboardResponse:
        """
        Executes requests to the requested dashboard sections in parallel using asyncio.gather.
        """
        # If no sections specified, load all
        all_sections = ["overview", "portfolio", "market", "news", "wealth", "watchlist", "calendar", "insights"]
        if not sections:
            sections = all_sections
            
        tasks = []
        
        # We append tasks in order to unpack them later.
        if "overview" in sections:
            tasks.append(OverviewDashboard(self.db).get_section(user_id))
        if "portfolio" in sections:
            tasks.append(PortfolioDashboard(self.db).get_section(user_id))
        if "market" in sections:
            tasks.append(MarketDashboard().get_section())
        if "news" in sections:
            tasks.append(NewsDashboard(self.db).get_section(user_id))
        if "wealth" in sections:
            tasks.append(WealthDashboard(self.db).get_section(user_id))
        if "watchlist" in sections:
            tasks.append(WatchlistDashboard(self.db).get_section(user_id))
        if "calendar" in sections:
            tasks.append(CalendarDashboard().get_section())
        if "insights" in sections:
            tasks.append(InsightsDashboard(self.db).get_section(user_id))
            
        # Parallel execution of all orchestrator tasks
        # asyncio.gather will run these concurrently, reducing total latency to max(task_latency)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        response_kwargs = {}
        idx = 0
        
        for section_name in sections:
            res = results[idx]
            if isinstance(res, Exception):
                # Graceful degradation: if a section fails, we just don't include it (or include empty)
                # We can log the error here.
                res = {"widgets": []}
            response_kwargs[section_name] = res
            idx += 1
            
        return DashboardResponse(**response_kwargs)
