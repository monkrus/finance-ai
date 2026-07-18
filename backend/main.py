from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter

from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import get_redis_client
from app.core.logging import setup_logging
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.exceptions import FinPilotException, finpilot_exception_handler, global_exception_handler
import app.models  # This ensures models are registered

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Rate Limiter
    redis_client = get_redis_client()
    await FastAPILimiter.init(redis_client)
    
    # Start background workers
    from app.notifications.worker import run_worker_loop
    import asyncio
    worker_task = asyncio.create_task(run_worker_loop())

    
    # Initialize the database tables on startup (good for local dev with SQLite/Postgres)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup on shutdown
    worker_task.cancel()
    await FastAPILimiter.close()
    await redis_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for FinPilot AI - an AI-powered financial platform.",
    version="0.1.0",
    lifespan=lifespan
)

# Configure Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure Session Middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Configure CORS (origins are env-driven so production/staging frontends work).
cors_origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(FinPilotException, finpilot_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/")
async def root():
    return {"status": "online", "message": f"Welcome to {settings.PROJECT_NAME} API"}

from app.api.system import router as system_router
from app.api.auth import router as auth_router
from app.api.identity import router as identity_router
from app.api.oauth import router as oauth_router
from app.api.market_data import router as market_data_router
from app.api.v1.ai import router as ai_router
from app.api.v1.documents import router as documents_router
from app.api.v1.analysis import router as analysis_router
from app.api.portfolio import router as portfolio_router
from app.api.news import router as news_router
from app.api.v1.wealth import router as wealth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.integrations import router as integrations_router

api_prefix = settings.API_V1_STR
app.include_router(system_router, tags=["system"])
app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["auth"])
app.include_router(identity_router, prefix=f"{api_prefix}/users", tags=["users"])
app.include_router(oauth_router, prefix=f"{api_prefix}/oauth/google", tags=["oauth"])
app.include_router(market_data_router, prefix=f"{api_prefix}/market-data", tags=["market-data"])
app.include_router(ai_router, prefix=f"{api_prefix}/ai", tags=["ai"])
app.include_router(documents_router, prefix=f"{api_prefix}/documents", tags=["documents"])
app.include_router(analysis_router, prefix=f"{api_prefix}/analysis", tags=["analysis"])
app.include_router(portfolio_router, prefix=f"{api_prefix}/portfolios", tags=["portfolio"])
app.include_router(news_router, prefix=f"{api_prefix}/news", tags=["news"])
app.include_router(wealth_router, prefix=f"{api_prefix}/wealth", tags=["wealth"])
app.include_router(dashboard_router, prefix=f"{api_prefix}", tags=["dashboard"])
app.include_router(notifications_router, prefix=f"{api_prefix}/notifications", tags=["notifications"])
app.include_router(integrations_router, prefix=f"{api_prefix}/integrations", tags=["integrations"])
