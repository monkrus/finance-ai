import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import InsightsSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache
from app.ai.gateway import AIGatewayService # Mod 3

class InsightsDashboard:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Cache AI insights for 600 seconds (10 minutes)
    @DashboardCache.cached(ttl_seconds=600)
    async def get_section(self, user_id: int) -> dict:
        # We invoke the AI Gateway using predefined prompts
        # In a real environment we would pass context here.
        try:
            ai = AIGatewayService()
            insight_task = ai.chat("Generate a single sentence portfolio insight based on current markets.", model="gpt-4")
            insight = await insight_task
        except Exception:
            insight = "Market conditions suggest holding current cash reserves."

        widgets = [
            WidgetBuilder.build(
                title="Daily AI Insight",
                subtitle="Executive Summary",
                value=insight,
                formatted_value=insight,
                icon="brain"
            )
        ]
        
        return {"widgets": [w.model_dump() for w in widgets]}
