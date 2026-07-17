from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()

@router.get("/health", summary="Infrastructure Health Check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check the health of the API and its dependencies (e.g. database)."""
    db_status = "offline"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "online"
    except Exception:
        pass

    return {
        "status": "healthy",
        "database": db_status
    }
