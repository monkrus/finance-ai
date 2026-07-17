from sqlalchemy.ext.asyncio import AsyncSession
from app.wealth.budget import BudgetEngine
from app.wealth.cashflow import CashFlowEngine
from app.wealth.networth import NetWorthEngine
from app.wealth.goals import GoalEngine
from app.wealth.planning import WealthPlanningEngine
from app.news.engine import NewsIntelligenceEngine
from app.ai.gateway import AIGatewayService
from datetime import datetime, timezone
import json

class AIFinancialCoach:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai = AIGatewayService()
        self.budget_engine = BudgetEngine(db)
        self.cashflow_engine = CashFlowEngine(db)
        self.networth_engine = NetWorthEngine(db)
        self.goal_engine = GoalEngine(db)
        self.planning_engine = WealthPlanningEngine(db)
        self.news_engine = NewsIntelligenceEngine(db)

    async def _gather_context(self, user_id: int) -> dict:
        now = datetime.now(timezone.utc)
        
        # We rely strictly on our deterministic engines for data.
        # AI never performs calculations.
        budget_data = await self.budget_engine.calculate_budget_utilization(user_id, now.year, now.month)
        cashflow_data = await self.cashflow_engine.calculate_monthly_cashflow(user_id, now.year, now.month)
        networth_data = await self.networth_engine.calculate_net_worth(user_id)
        goals_data = await self.goal_engine.calculate_goals_progress(user_id)
        plan_data = await self.planning_engine.calculate_wealth_plan(user_id)
        
        # Integrate news affecting personal finance
        # e.g., inflation news, interest rates
        latest_news = await self.news_engine.get_recent_news(limit=5)
        macro_news = [n for n in latest_news if n.article_type in ["Macro", "General", "Economics"]]
        
        return {
            "budget": budget_data,
            "cashflow": cashflow_data,
            "networth": networth_data,
            "goals": goals_data,
            "planning": plan_data,
            "macro_news": [{"headline": n.headline, "summary": n.content} for n in macro_news]
        }

    async def get_financial_advice(self, user_id: int, user_query: str) -> str:
        """
        Takes a user's question, gathers their entire financial state from engines,
        and uses the AI Gateway to generate coaching advice.
        """
        context = await self._gather_context(user_id)
        
        system_prompt = (
            "You are FinPilot's AI Financial Coach. Your goal is to provide personal finance "
            "advice using the provided strictly calculated data context.\n"
            "Rules:\n"
            "1. NEVER perform mathematical calculations yourself. Use the provided context values.\n"
            "2. Incorporate macroeconomic news into your advice (e.g., inflation, interest rates).\n"
            "3. Be concise, actionable, and encouraging.\n"
            f"DATA CONTEXT:\n{json.dumps(context, indent=2)}"
        )
        
        response = await self.ai.chat(
            prompt=user_query,
            system_prompt=system_prompt,
            model="gpt-4"
        )
        
        return response
