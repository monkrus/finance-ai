from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.integration import AuditEvent
import logging

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, user_id: int, action: str, status: str, provider: Optional[str] = None, details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Append-only audit trail."""
        try:
            event = AuditEvent(
                user_id=user_id,
                action=action,
                status=status,
                provider=provider,
                details=details,
                ip_address=ip_address
            )
            self.db.add(event)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            # Ensure audit log failure doesn't crash the operation entirely
