import pytest
from fastapi.testclient import TestClient
from main import app
from app.api.deps import get_current_user

client = TestClient(app)

def test_dashboard_api_unauthorized():
    # Remove only a leaked auth override (if any) so real auth runs. Do NOT
    # clear() the whole map, as that also drops the get_db test-DB override
    # installed by conftest and breaks DB-backed tests later in the session.
    app.dependency_overrides.pop(get_current_user, None)

    # Attempt to access dashboard without auth token
    response = client.get("/api/v1/dashboard/")
    # Our global deps or route deps for get_current_user should block this
    assert response.status_code in [401, 403]

def test_dashboard_api_overview_unauthorized():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code in [401, 403]
