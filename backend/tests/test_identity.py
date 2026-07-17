import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_identity_full_lifecycle(client: AsyncClient):
    email = f"id_{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecretPassword123!"

    # Setup
    res = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    tokens = res.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Profile Update
    res = await client.put("/api/v1/users/me", headers=headers, json={"avatar_url": "https://example.com/avatar.png"})
    assert res.status_code == 200
    assert res.json()["avatar_url"] == "https://example.com/avatar.png"

    # Password Reset Request
    res = await client.post("/api/v1/users/password-reset/request", json={"email": email})
    assert res.status_code == 202

    # We can't easily intercept the mock email token without modifying the app to return it in test mode.
    # We will test the failure path of Invalid Token.
    res = await client.post("/api/v1/users/password-reset/confirm", json={"token": "invalid_token", "new_password": "NewPassword123!"})
    assert res.status_code == 400
    assert "Invalid or expired" in res.text

    # Verify Email failure path
    res = await client.post("/api/v1/users/verify-email", json={"token": "invalid_token"})
    assert res.status_code == 400
    assert "Invalid or expired" in res.text

    # Successful Verify Email
    from app.core.redis import get_redis_client
    redis = get_redis_client()
    await redis.set("verify_email:valid_token", email)
    res = await client.post("/api/v1/users/verify-email", json={"token": "valid_token"})
    assert res.status_code == 200
    
    # Verify Email - User Not Found
    await redis.set("verify_email:no_user_token", "does_not_exist@example.com")
    res = await client.post("/api/v1/users/verify-email", json={"token": "no_user_token"})
    assert res.status_code == 404

    # Successful Password Reset
    await redis.set("password_reset:valid_token", email)
    res = await client.post("/api/v1/users/password-reset/confirm", json={"token": "valid_token", "new_password": "NewPassword123!"})
    assert res.status_code == 200
    
    # Password Reset - User Not Found
    await redis.set("password_reset:no_user_token", "does_not_exist@example.com")
    res = await client.post("/api/v1/users/password-reset/confirm", json={"token": "no_user_token", "new_password": "NewPassword123!"})
    assert res.status_code == 404

