from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.core.database import get_db
from app.services.auth import AuthService
from app.models.session import DeviceSession
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RefreshRequest, LogoutRequest, DeviceSessionResponse, AuthUser
from typing import List
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

# Backend role names -> frontend Role enum values.
_ROLE_MAP = {"Admin": "ADMIN", "Premium User": "PREMIUM", "Standard User": "USER"}


async def _load_auth_user(db: AsyncSession, user_id: int) -> AuthUser:
    """Load a user (with its role eagerly, via selectin) and shape the auth payload.

    Re-selecting guarantees the role relationship is loaded inside the async
    session, avoiding lazy-load access on a possibly-expired instance.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    role_name = user.role.name if user and user.role else None
    return AuthUser(
        id=user.id,
        email=user.email,
        role=_ROLE_MAP.get(role_name, "USER"),
        isEmailVerified=bool(user.is_verified),
        avatarUrl=user.avatar_url,
    )

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: Request, body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register_user(db, body.email, body.password)
    access_token = create_access_token(user.id)
    session = await AuthService.create_device_session(
        db, user.id, request.client.host, request.headers.get("user-agent", "")
    )
    auth_user = await _load_auth_user(db, user.id)
    return {"access_token": access_token, "refresh_token": session.refresh_token, "user": auth_user}

@router.post("/login", response_model=TokenResponse)
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, body.email, body.password, request.client.host)
    access_token = create_access_token(user.id)
    session = await AuthService.create_device_session(
        db, user.id, request.client.host, request.headers.get("user-agent", "")
    )
    auth_user = await _load_auth_user(db, user.id)
    return {"access_token": access_token, "refresh_token": session.refresh_token, "user": auth_user}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeviceSession).where(DeviceSession.refresh_token == body.refresh_token))
    session = result.scalars().first()
    
    if not session or session.is_revoked or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
    access_token = create_access_token(session.user_id)
    # Generate a new refresh token (Rotation)
    new_session = await AuthService.create_device_session(
        db, session.user_id, request.client.host, request.headers.get("user-agent", "")
    )

    # Revoke old session
    session.is_revoked = True
    await db.commit()

    auth_user = await _load_auth_user(db, session.user_id)
    return {"access_token": access_token, "refresh_token": new_session.refresh_token, "user": auth_user}

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    await AuthService.revoke_session(db, body.refresh_token)
    return None

@router.get("/sessions", response_model=List[DeviceSessionResponse])
async def get_sessions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sessions = await AuthService.get_user_sessions(db, current_user.id)
    return sessions

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_specific_session(session_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await AuthService.revoke_session_by_id(db, session_id, current_user.id)
    return None

@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all_sessions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await AuthService.revoke_all_sessions(db, current_user.id)
    return None
