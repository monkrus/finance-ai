import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.api.deps import get_db, get_current_user
from app.models.user import User
from unittest.mock import AsyncMock, patch, MagicMock

async def override_get_db():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    
    async def mock_refresh(obj):
        from datetime import datetime, timezone
        obj.id = 1
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)
        obj.probability = 0.0
        # Transactions have a timestamp
        if getattr(obj, "timestamp", None) is None:
            obj.timestamp = datetime.now(timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=mock_refresh)

    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = []
    mock_res.scalar_one_or_none.return_value = True
    
    mock_acc = MagicMock()
    mock_acc.balance = 100
    mock_res.scalar_one.return_value = mock_acc
    
    mock_db.execute.return_value = mock_res
    yield mock_db

def override_get_current_user():
    return User(id=1, email="test@test.com", is_active=True)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_accounts_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/wealth/accounts", json={
            "name": "Checking",
            "account_type": "Cash"
        })
        assert response.status_code == 200
        
        response2 = await ac.get("/api/v1/wealth/accounts")
        assert response2.status_code == 200

@pytest.mark.asyncio
async def test_transactions_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/wealth/transactions", json={
            "account_id": 1,
            "amount": 100.0,
            "transaction_type": "Income"
        })
        assert response.status_code == 200
        
        response2 = await ac.get("/api/v1/wealth/transactions")
        assert response2.status_code == 200

@pytest.mark.asyncio
async def test_budgets_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/wealth/budgets", json={
            "budget_type": "Monthly Budget",
            "spending_limit": 1000.0
        })
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_goals_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/wealth/goals", json={
            "goal_type": "Emergency Fund",
            "name": "EF",
            "target_amount": 10000.0
        })
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_analytics_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with patch("app.api.v1.wealth.BudgetEngine") as MockEng:
            MockEng.return_value.calculate_budget_utilization = AsyncMock(return_value={"a": 1})
            res = await ac.get("/api/v1/wealth/analytics/budget")
            assert res.status_code == 200
            
        with patch("app.api.v1.wealth.CashFlowEngine") as MockEng:
            MockEng.return_value.calculate_monthly_cashflow = AsyncMock(return_value={"a": 1})
            res = await ac.get("/api/v1/wealth/analytics/cashflow")
            assert res.status_code == 200
            
        with patch("app.api.v1.wealth.NetWorthEngine") as MockEng:
            MockEng.return_value.calculate_net_worth = AsyncMock(return_value={"a": 1})
            res = await ac.get("/api/v1/wealth/analytics/networth")
            assert res.status_code == 200
            
        with patch("app.api.v1.wealth.GoalEngine") as MockEng:
            MockEng.return_value.calculate_goals_progress = AsyncMock(return_value={"a": 1})
            res = await ac.get("/api/v1/wealth/analytics/goals")
            assert res.status_code == 200
            
        with patch("app.api.v1.wealth.WealthPlanningEngine") as MockEng:
            MockEng.return_value.calculate_wealth_plan = AsyncMock(return_value={"a": 1})
            res = await ac.get("/api/v1/wealth/analytics/planning")
            assert res.status_code == 200

@pytest.mark.asyncio
async def test_coach_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with patch("app.api.v1.wealth.AIFinancialCoach") as MockCoach:
            MockCoach.return_value.get_financial_advice = AsyncMock(return_value="Save more")
            res = await ac.get("/api/v1/wealth/coach/advice?query=hello")
            assert res.status_code == 200
