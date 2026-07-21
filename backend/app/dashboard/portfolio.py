import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import PortfolioSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache
from app.portfolio.engine import PortfolioEngine
from app.market_data.service import MarketDataService
from datetime import datetime, timezone

class PortfolioDashboard:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Cache portfolio for 60 seconds
    @DashboardCache.cached(ttl_seconds=60)
    async def get_section(self, user_id: int) -> dict:
        # get_user_portfolios_summary only needs market data (perf/alloc/risk
        # engines), not the analysis engine.
        engine = PortfolioEngine(market_data_service=MarketDataService())
        try:
            # Reuse the request session; the engine runs sections sequentially so
            # there is no concurrent access (a second session would collide on
            # SQLite's single connection).
            port_summary = await engine.get_user_portfolios_summary(self.db, user_id)
            total_value = port_summary.get("total_value", 0.0)
            daily_change = port_summary.get("daily_change", 0.0)
            daily_change_pct = port_summary.get("daily_change_percent", 0.0)
        except Exception:
            # Degrade to zero (empty state) rather than a fake figure if valuation fails.
            total_value = 0.0
            daily_change = 0.0
            daily_change_pct = 0.0

        widgets = []
        widgets.append(WidgetBuilder.build(
            title="Total Portfolio Value",
            value=total_value,
            formatted_value=f"${total_value:,.2f}",
            change=daily_change,
            change_percent=daily_change_pct,
            icon="pie-chart"
        ))

        return {"widgets": [w.model_dump() for w in widgets]}
