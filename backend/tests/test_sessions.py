import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_session_management(client: AsyncClient):
    email = f"sess_{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecretPassword123!"

    # Setup
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    
    # Login Device 1
    res1 = await client.post("/api/v1/auth/login", json={"email": email, "password": password}, headers={"user-agent": "Device1"})
    t1 = res1.json()["access_token"]
    
    # Login Device 2
    res2 = await client.post("/api/v1/auth/login", json={"email": email, "password": password}, headers={"user-agent": "Device2"})
    t2 = res2.json()["access_token"]
    
    # Get Sessions
    res = await client.get("/api/v1/auth/sessions", headers={"Authorization": f"Bearer {t1}"})
    assert res.status_code == 200
    sessions = res.json()
    assert len(sessions) == 3
    
    # Revoke specific session
    res = await client.delete(f"/api/v1/auth/sessions/{sessions[1]['id']}", headers={"Authorization": f"Bearer {t1}"})
    assert res.status_code == 204
    
    # Revoke all sessions
    res = await client.delete("/api/v1/auth/sessions", headers={"Authorization": f"Bearer {t1}"})
    assert res.status_code == 204
    
    # Verify sessions are revoked (this won't block access token usage immediately without JWT blacklist, 
    # but let's check refresh fails)
    refresh_token = res1.json()["refresh_token"]
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 401
