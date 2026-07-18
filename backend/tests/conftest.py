import os
# Ensure mandatory environment variables are set before any application code is imported
os.environ["SECRET_KEY"] = "d9b3b8908320478b88d01d4a8990d0b7952701b22e0325d7c35f29ab6e107567"
os.environ["ENVIRONMENT"] = "test"

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import fakeredis.aioredis
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import Base

from app.core.config import settings
# Wait for FastAPI refactor if it gets moved inside app (currently in root)
from main import app

# Use the same test DB as exported in environment
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False)


# Rebind the application's own sessionmaker to the SQLite test engine. Tests and
# code that use AsyncSessionLocal() directly (e.g. test_rbac_advanced, the
# notifications worker) bypass the get_db dependency, so they would otherwise
# connect to the real (Postgres) engine. Reconfiguring the shared sessionmaker in
# place redirects every such caller to the test database.
from app.core.database import AsyncSessionLocal as _AppSessionLocal
_AppSessionLocal.configure(bind=test_engine)


async def override_get_db():
    """Route DB access to the SQLite test session instead of the real engine."""
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(autouse=True)
def _apply_db_override():
    # Re-assert the SQLite get_db override before every test. Some test modules
    # call app.dependency_overrides.clear() in their teardown, which otherwise
    # wipes this session-scoped override and lets later tests fall through to the
    # real (Postgres) engine. Re-applying per test keeps the suite isolated and
    # runnable without a live Postgres.
    from app.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    yield

@pytest_asyncio.fixture(scope="session", autouse=True)
async def mock_redis():
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    with patch("app.core.redis.get_redis_client", return_value=fake_redis), \
         patch("app.services.auth.get_redis_client", return_value=fake_redis), \
         patch("app.services.identity.get_redis_client", return_value=fake_redis), \
         patch("app.market_data.cache.get_redis_client", return_value=fake_redis), \
         patch("main.get_redis_client", return_value=fake_redis):
        yield fake_redis

@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    from app.models.user import User
    from app.services.auth import get_password_hash
    import uuid
    user = User(
        email=f"portfolio_test_{uuid.uuid4()}@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def test_user_token_headers(client, test_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
