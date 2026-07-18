from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RoleResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    avatar_url: Optional[str] = None

class VerifyEmailRequest(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
