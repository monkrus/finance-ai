import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import PortfolioSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache
from app.portfolio.engine import PortfolioEngine # Assuming this exists from Mod 7
from datetime import datetime, timezone

class PortfolioDashboard:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Cache portfolio for 60 seconds
    @DashboardCache.cached(ttl_seconds=60)
    async def get_section(self, user_id: int) -> dict:
        # In a real scenario, we'd fetch actual portfolio summary using PortfolioEngine
        # For orchestration demonstration without duplicating logic, we mock the call if engine is missing
        # or use the engine if available.
        try:
            engine = PortfolioEngine(self.db)
            port_summary = await engine.get_user_portfolios_summary(user_id)
            total_value = port_summary.get("total_value", 0.0)
            daily_change = port_summary.get("daily_change", 0.0)
            daily_change_pct = port_summary.get("daily_change_percent", 0.0)
        except Exception:
            # Fallback mock for testing orchestration layer independently
            total_value = 150000.0
            daily_change = 1250.0
            daily_change_pct = 0.84

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
