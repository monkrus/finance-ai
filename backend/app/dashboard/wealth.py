import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import WealthSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache
from app.wealth.networth import NetWorthEngine
from app.wealth.cashflow import CashFlowEngine
from app.wealth.budget import BudgetEngine
from app.wealth.goals import GoalEngine
from app.wealth.planning import WealthPlanningEngine
from datetime import datetime, timezone

class WealthDashboard:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Cache wealth for 60 seconds
    @DashboardCache.cached(ttl_seconds=60)
    async def get_section(self, user_id: int) -> dict:
        now = datetime.now(timezone.utc)
        
        # Instantiate engines
        nw_eng = NetWorthEngine(self.db)
        cf_eng = CashFlowEngine(self.db)
        bg_eng = BudgetEngine(self.db)
        gl_eng = GoalEngine(self.db)
        pl_eng = WealthPlanningEngine(self.db)
        
        # Execute in parallel
        nw_task = nw_eng.calculate_net_worth(user_id)
        cf_task = cf_eng.calculate_monthly_cashflow(user_id, now.year, now.month)
        bg_task = bg_eng.calculate_budget_utilization(user_id, now.year, now.month)
        gl_task = gl_eng.calculate_goals_progress(user_id)
        pl_task = pl_eng.calculate_wealth_plan(user_id)
        
        nw, cf, bg, gl, pl = await asyncio.gather(nw_task, cf_task, bg_task, gl_task, pl_task)
        
        # Build widgets
        widgets = []
        
        widgets.append(WidgetBuilder.build(
            title="Net Worth",
            value=nw.get("net_worth", 0.0),
            formatted_value=f"${nw.get('net_worth', 0.0):,.2f}",
            icon="wallet"
        ))
        
        widgets.append(WidgetBuilder.build(
            title="Monthly Cash Flow",
            value=cf.get("free_cash_flow", 0.0),
            formatted_value=f"${cf.get('free_cash_flow', 0.0):,.2f}",
            icon="arrow-up-down"
        ))
        
        widgets.append(WidgetBuilder.build(
            title="Savings Rate",
            value=cf.get("savings_rate_percentage", 0.0),
            formatted_value=f"{cf.get('savings_rate_percentage', 0.0):.1f}%",
            icon="piggy-bank"
        ))
        
        widgets.append(WidgetBuilder.build(
            title="Financial Health",
            value=pl.get("financial_health_score", 0.0),
            formatted_value=f"{pl.get('financial_health_score', 0.0):.0f}/100",
            icon="heart-pulse"
        ))
        
        # We return a dict that matches WealthSection schema
        # because the @cached decorator serializes it, and the API layer will construct the Pydantic model
        return {"widgets": [w.model_dump() for w in widgets]}
