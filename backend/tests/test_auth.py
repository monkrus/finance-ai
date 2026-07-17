import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword123"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Login
    res = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "strongpassword123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Get Profile
    res = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert res.status_code == 200
    profile = res.json()
    assert profile["email"] == "test@example.com"
