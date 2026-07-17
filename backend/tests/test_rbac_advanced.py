import pytest
from httpx import AsyncClient
from app.core.database import AsyncSessionLocal
from app.models.rbac import Role, Permission
from sqlalchemy import select

@pytest.mark.asyncio
async def test_rbac_advanced(client: AsyncClient):
    # 1. Register User
    email = "rbac_advanced@example.com"
    password = "SuperSecretPassword123!"
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    
    # 2. Assign standard role in DB to simulate proper RBAC
    async with AsyncSessionLocal() as db:
        # Create standard role if not exists
        role = Role(name="Standard User")
        db.add(role)
        await db.commit()
        
        # Assign to user
        from app.models.user import User
        user = (await db.execute(select(User).where(User.email == email))).scalars().first()
        user.role_id = role.id
        await db.commit()
        
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    
    # Standard user hits premium data -> 403 Missing required permission
    res = await client.get("/api/v1/users/premium-data", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert "Missing required permission" in res.text
    
    # 3. Give user permission
    async with AsyncSessionLocal() as db:
        role = (await db.execute(select(Role).where(Role.name == "Standard User"))).scalars().first()
        perm = Permission(name="view:premium_content", description="View premium content")
        role.permissions.append(perm)
        db.add(role)
        await db.commit()
        
    # Standard user hits premium data -> 200 Success
    res = await client.get("/api/v1/users/premium-data", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "message" in res.json()
