import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_rbac_premium_data(client: AsyncClient):
    # Generate unique email for this test
    email = f"premium_{uuid.uuid4().hex[:8]}@example.com"

    # Register
    res = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password"
    })
    access_token = res.json()["access_token"]

    # Attempt to access premium data (Standard User shouldn't have 'view:premium_content' by default in our standard seed)
    res = await client.get("/api/v1/users/premium-data", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 403
    assert "Access denied" in res.text or "Missing required permission" in res.text
