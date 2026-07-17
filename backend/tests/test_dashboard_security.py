import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dashboard_api_unauthorized():
    # Clear overrides set by other test modules globally
    app.dependency_overrides.clear()
    
    # Attempt to access dashboard without auth token
    response = client.get("/api/v1/dashboard/")
    # Our global deps or route deps for get_current_user should block this
    assert response.status_code in [401, 403]

def test_dashboard_api_overview_unauthorized():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code in [401, 403]
