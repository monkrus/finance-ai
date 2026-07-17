import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.integration import ConnectedAccount, SyncJob
from app.integrations.providers import BaseProvider

logger = logging.getLogger(__name__)

class SyncEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_sync(self, job_id: int, provider: BaseProvider, account: ConnectedAccount):
        """Execute synchronization logic (delta vs full pull)"""
        job = await self.db.get(SyncJob, job_id)
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        account.sync_status = "syncing"
        await self.db.commit()

        try:
            # Pull data
            last_sync_str = account.last_sync.isoformat() if account.last_sync else None
            data = await provider.sync(account.external_account_id, last_sync_time=last_sync_str)
            
            # (In production, map `data` payload to the Transaction/Holding models here)
            # e.g., self.resolve_conflicts(data)
            
            # Mark Success
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            
            account.sync_status = "idle"
            account.last_sync = job.completed_at
            account.retry_count = 0
            
        except Exception as e:
            logger.error(f"SyncJob {job_id} failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            
            account.sync_status = "failed"
            account.error_message = str(e)
            account.retry_count += 1
            
        await self.db.commit()
