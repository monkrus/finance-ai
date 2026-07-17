import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_auth_full_lifecycle(client: AsyncClient):
    email = f"auth_{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecretPassword123!"

    # 1. Register User
    res = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201
    
    # 2. Duplicate Registration
    res = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert res.status_code == 400
    assert "already exists" in res.text
    
    # 3. Login Valid Credentials
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    tokens = res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    refresh_token = tokens["refresh_token"]

    # 4. Login Invalid Password (and brute force trigger)
    for _ in range(5):
        res = await client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword!"})
    
    # The 6th attempt should hit rate limit
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 429
    assert "Too many login attempts" in res.text

    # 5. Refresh Token Rotation
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    new_tokens = res.json()
    new_refresh_token = new_tokens["refresh_token"]
    assert new_refresh_token != refresh_token

    # 6. Invalid/Revoked Token usage
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 401
    assert "Invalid or expired" in res.text

    # 7. Logout
    res = await client.post("/api/v1/auth/logout", json={"refresh_token": new_refresh_token})
    assert res.status_code == 204

    # 8. Use logged out token
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh_token})
    assert res.status_code == 401
