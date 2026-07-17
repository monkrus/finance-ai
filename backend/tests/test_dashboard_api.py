import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from app.api.deps import get_current_user
from app.models.user import User
import uuid

# Mock auth
async def override_get_current_user():
    user = User(email="test@example.com")
    user.id = 1
    return user

app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def mock_engine():
    with patch("app.api.v1.dashboard.DashboardEngine") as MockEngineClass:
        mock_instance = AsyncMock()
        MockEngineClass.return_value = mock_instance
        
        # Setup mock responses
        from app.dashboard.schemas import DashboardResponse, OverviewSection, PortfolioSection
        
        ov = OverviewSection(widgets=[])
        pf = PortfolioSection(widgets=[])
        
        full_res = DashboardResponse(overview=ov, portfolio=pf)
        mock_instance.get_dashboard.return_value = full_res
        yield mock_instance

def test_get_full_dashboard(mock_engine):
    response = client.get("/api/v1/dashboard/")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "portfolio" in data

def test_get_partial_dashboard(mock_engine):
    response = client.get("/api/v1/dashboard/?sections=overview,portfolio")
    assert response.status_code == 200
    mock_engine.get_dashboard.assert_called_with(1, ["overview", "portfolio"])

def test_get_overview(mock_engine):
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    mock_engine.get_dashboard.assert_called_with(1, ["overview"])
