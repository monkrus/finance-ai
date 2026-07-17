import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import NewsSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache
from app.news.engine import NewsIntelligenceEngine # Mod 8

class NewsDashboard:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Cache news for 300 seconds (5 minutes)
    @DashboardCache.cached(ttl_seconds=300)
    async def get_section(self, user_id: int) -> dict:
        try:
            engine = NewsIntelligenceEngine(self.db)
            # Parallel fetch
            breaking_task = engine.get_recent_news(limit=3, article_type="Breaking")
            portfolio_task = engine.get_portfolio_news(user_id=user_id, limit=5)
            breaking, portfolio = await asyncio.gather(breaking_task, portfolio_task)
        except Exception:
            breaking = []
            portfolio = []

        widgets = []
        # We just summarize counts or top headline for the widget overview
        widgets.append(WidgetBuilder.build(
            title="Breaking News",
            subtitle=breaking[0].headline if breaking else "No breaking news",
            value=len(breaking),
            formatted_value=f"{len(breaking)} Updates",
            icon="newspaper"
        ))

        return {"widgets": [w.model_dump() for w in widgets]}
