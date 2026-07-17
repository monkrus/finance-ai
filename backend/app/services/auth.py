from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.models.user import User
from app.models.session import DeviceSession
from app.models.rbac import Role
from app.core.security import verify_password, get_password_hash, create_refresh_token
from app.core.exceptions import FinPilotException
from app.core.redis import get_redis_client
from app.services.audit import AuditService
from app.core.config import settings

class AuthService:
    BRUTE_FORCE_LIMIT = 5
    BRUTE_FORCE_WINDOW = 300 # 5 minutes

    @staticmethod
    async def _check_brute_force(email: str, ip_address: str):
        redis = get_redis_client()
        key = f"login_attempts:{email}:{ip_address}"
        attempts = await redis.get(key)
        if attempts and int(attempts) >= AuthService.BRUTE_FORCE_LIMIT:
            raise FinPilotException("Too many login attempts. Please try again later.", status_code=429)

    @staticmethod
    async def _increment_failed_attempt(email: str, ip_address: str):
        redis = get_redis_client()
        key = f"login_attempts:{email}:{ip_address}"
        await redis.incr(key)
        await redis.expire(key, AuthService.BRUTE_FORCE_WINDOW)

    @staticmethod
    async def _clear_failed_attempts(email: str, ip_address: str):
        redis = get_redis_client()
        key = f"login_attempts:{email}:{ip_address}"
        await redis.delete(key)

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str, ip_address: str) -> User:
        await AuthService._check_brute_force(email, ip_address)

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            await AuthService._increment_failed_attempt(email, ip_address)
            await AuditService.log_action(db, action="login", status="failure", user_id=user.id if user else None, ip_address=ip_address)
            raise FinPilotException("Incorrect email or password", status_code=401)

        if not user.is_active:
            await AuditService.log_action(db, action="login", status="failure_inactive", user_id=user.id, ip_address=ip_address)
            raise FinPilotException("User account is disabled", status_code=403)

        await AuthService._clear_failed_attempts(email, ip_address)
        await AuditService.log_action(db, action="login", status="success", user_id=user.id, ip_address=ip_address)
        return user

    @staticmethod
    async def register_user(db: AsyncSession, email: str, password: str) -> User:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalars().first():
            raise FinPilotException("User with this email already exists")

        # Assign standard role by default
        role_result = await db.execute(select(Role).where(Role.name == "Standard User"))
        standard_role = role_result.scalars().first()

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role_id=standard_role.id if standard_role else None,
            is_active=True,
            is_verified=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await AuditService.log_action(db, action="register", status="success", user_id=user.id)
        return user

    @staticmethod
    async def create_device_session(db: AsyncSession, user_id: int, ip_address: str, user_agent: str) -> DeviceSession:
        refresh_token = create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        session = DeviceSession(
            user_id=user_id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_user_sessions(db: AsyncSession, user_id: int):
        result = await db.execute(select(DeviceSession).where(DeviceSession.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def revoke_session(db: AsyncSession, refresh_token: str):
        result = await db.execute(select(DeviceSession).where(DeviceSession.refresh_token == refresh_token))
        session = result.scalars().first()
        if session and not session.is_revoked:
            session.is_revoked = True
            await db.commit()

    @staticmethod
    async def revoke_session_by_id(db: AsyncSession, session_id: int, user_id: int):
        result = await db.execute(select(DeviceSession).where(DeviceSession.id == session_id, DeviceSession.user_id == user_id))
        session = result.scalars().first()
        if session and not session.is_revoked:
            session.is_revoked = True
            await db.commit()
            
    @staticmethod
    async def revoke_all_sessions(db: AsyncSession, user_id: int, except_session_id: int = None):
        query = select(DeviceSession).where(DeviceSession.user_id == user_id, DeviceSession.is_revoked == False)
        if except_session_id:
            query = query.where(DeviceSession.id != except_session_id)
        result = await db.execute(query)
        for session in result.scalars().all():
            session.is_revoked = True
        await db.commit()
