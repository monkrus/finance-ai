import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
import secrets

from app.models.user import User
from app.models.rbac import Role
from app.core.security import get_password_hash
from app.core.exceptions import FinPilotException
from app.core.redis import get_redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """
    Mock Email Service interface. 
    In production, this would integrate with SendGrid, AWS SES, or similar.
    """
    @staticmethod
    async def send_verification_email(email: str, token: str):
        logger.info(f"--- MOCK EMAIL ---")
        logger.info(f"To: {email}")
        logger.info(f"Subject: Verify your FinPilot Account")
        logger.info(f"Body: Your verification token is {token}")
        logger.info(f"------------------")

    @staticmethod
    async def send_password_reset_email(email: str, token: str):
        logger.info(f"--- MOCK EMAIL ---")
        logger.info(f"To: {email}")
        logger.info(f"Subject: Password Reset Request")
        logger.info(f"Body: Your reset token is {token}")
        logger.info(f"------------------")

class IdentityService:
    @staticmethod
    async def update_profile(db: AsyncSession, user: User, avatar_url: str = None):
        if avatar_url:
            user.avatar_url = avatar_url
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def generate_verification_token() -> str:
        # Generate a secure random token
        return secrets.token_urlsafe(32)
        
    @staticmethod
    async def verify_email(db: AsyncSession, token: str):
        redis = get_redis_client()
        key = f"verify_email:{token}"
        email = await redis.get(key)
        if not email:
            raise FinPilotException("Invalid or expired verification token", status_code=400)
            
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            user.is_verified = True
            await db.commit()
            await redis.delete(key)
            return user
        raise FinPilotException("User not found", status_code=404)

    @staticmethod
    async def create_password_reset_token(db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            # We don't want to leak if an email exists or not via API, so we just return silently
            return
            
        token = secrets.token_urlsafe(32)
        redis = get_redis_client()
        key = f"password_reset:{token}"
        # Store for the configured expiry time
        await redis.setex(key, timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS), email)
        await EmailService.send_password_reset_email(email, token)

    @staticmethod
    async def reset_password(db: AsyncSession, token: str, new_password: str):
        redis = get_redis_client()
        key = f"password_reset:{token}"
        email = await redis.get(key)
        if not email:
            raise FinPilotException("Invalid or expired reset token", status_code=400)
            
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            user.hashed_password = get_password_hash(new_password)
            await db.commit()
            await redis.delete(key)
            return user
        raise FinPilotException("User not found", status_code=404)
