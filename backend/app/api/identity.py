from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserProfileResponse, UpdateProfileRequest, VerifyEmailRequest, PasswordResetRequest, PasswordResetConfirmRequest
from app.services.identity import IdentityService
from app.core.rbac import RequiresPermission

router = APIRouter()

@router.get("/me", response_model=UserProfileResponse)
async def get_current_profile(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile"""
    return current_user

@router.put("/me", response_model=UserProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile details"""
    updated_user = await IdentityService.update_profile(db, current_user, avatar_url=body.avatar_url)
    return updated_user

@router.get("/premium-data", dependencies=[Depends(RequiresPermission("view:premium_content"))])
async def get_premium_data():
    """Example endpoint demonstrating RBAC"""
    return {"message": "You have access to premium content."}

@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    await IdentityService.verify_email(db, body.token)
    return {"message": "Email verified successfully"}

@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(body: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    await IdentityService.create_password_reset_token(db, body.email)
    return {"message": "If that email exists, a password reset link has been sent"}

@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(body: PasswordResetConfirmRequest, db: AsyncSession = Depends(get_db)):
    await IdentityService.reset_password(db, body.token, body.new_password)
    return {"message": "Password has been reset successfully"}
