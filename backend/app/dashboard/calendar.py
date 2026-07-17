import asyncio
from app.dashboard.schemas import CalendarSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache

class CalendarDashboard:
    def __init__(self):
        pass

    # Cache calendar for 600 seconds (10 minutes)
    @DashboardCache.cached(ttl_seconds=600)
    async def get_section(self) -> dict:
        # Mock fetching calendar events
        widgets = [
            WidgetBuilder.build(
                title="Upcoming Earnings",
                subtitle="AAPL",
                value="Oct 26",
                formatted_value="Oct 26, 2023",
                icon="calendar"
            )
        ]
        return {"widgets": [w.model_dump() for w in widgets]}
