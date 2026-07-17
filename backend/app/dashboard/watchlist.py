import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import WatchlistSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache

class WatchlistDashboard:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Cache watchlist for 30 seconds
    @DashboardCache.cached(ttl_seconds=30)
    async def get_section(self, user_id: int) -> dict:
        # Mock fetching watchlist tickers and aggregating
        widgets = [
            WidgetBuilder.build(
                title="AAPL",
                subtitle="Apple Inc.",
                value=150.0,
                formatted_value="$150.00",
                change=1.5,
                change_percent=1.0,
                icon="smartphone"
            )
        ]
        return {"widgets": [w.model_dump() for w in widgets]}
