from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog

class AuditService:
    @staticmethod
    async def log_action(db: AsyncSession, action: str, status: str, user_id: int = None, ip_address: str = None, details: str = None):
        """
        Logs a security or important business action to the AuditLog table.
        """
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            status=status,
            ip_address=ip_address,
            details=details
        )
        db.add(log_entry)
        await db.commit()
