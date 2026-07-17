import pytest
from unittest.mock import AsyncMock, patch
from app.wealth.coach import AIFinancialCoach

@pytest.mark.asyncio
async def test_ai_coach():
    mock_db = AsyncMock()
    coach = AIFinancialCoach(mock_db)
    
    # Mock engines
    coach.budget_engine.calculate_budget_utilization = AsyncMock(return_value={"a": 1})
    coach.cashflow_engine.calculate_monthly_cashflow = AsyncMock(return_value={"a": 1})
    coach.networth_engine.calculate_net_worth = AsyncMock(return_value={"a": 1})
    coach.goal_engine.calculate_goals_progress = AsyncMock(return_value={"a": 1})
    coach.planning_engine.calculate_wealth_plan = AsyncMock(return_value={"a": 1})
    
    # Mock news
    class MockNews:
        article_type = "Macro"
        headline = "Inflation down"
        content = "Good"
    coach.news_engine.get_recent_news = AsyncMock(return_value=[MockNews()])
    
    # Mock AI Gateway
    coach.ai.chat = AsyncMock(return_value="Save more")
    
    res = await coach.get_financial_advice(1, "Should I save?")
    assert res == "Save more"
