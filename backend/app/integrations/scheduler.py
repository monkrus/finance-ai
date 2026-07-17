import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.integration import ConnectedAccount

logger = logging.getLogger(__name__)

class Scheduler:
    """Background polling loop for triggering Syncs based on next_sync timestamps."""
    
    @staticmethod
    async def run_loop():
        logger.info("Starting Integration Scheduler Loop...")
        while True:
            try:
                async with AsyncSessionLocal() as db:
                    now = datetime.now(timezone.utc)
                    
                    # Find accounts that need syncing
                    result = await db.execute(
                        select(ConnectedAccount).where(
                            ConnectedAccount.next_sync <= now,
                            ConnectedAccount.status == "active",
                            ConnectedAccount.sync_status == "idle"
                        )
                    )
                    accounts = result.scalars().all()
                    
                    for account in accounts:
                        # In production, dispatch a Redis Celery/RQ job here
                        logger.info(f"Dispatching scheduled sync for account {account.id}")
                        account.sync_status = "queued"
                        
                    await db.commit()
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                
            await asyncio.sleep(60) # Run check every 60 seconds
