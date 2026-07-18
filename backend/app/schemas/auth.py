from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Minimum password length enforced server-side (never trust the client).
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

class AuthUser(BaseModel):
    """Authenticated user payload returned alongside tokens.

    Shaped to the frontend `User` contract (camelCase, role as an enum string)
    so login/register/refresh responses are consistent across the stack.
    """
    id: int
    email: EmailStr
    role: str  # "ADMIN" | "PREMIUM" | "USER"
    isEmailVerified: bool
    avatarUrl: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    user: AuthUser

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class DeviceSessionResponse(BaseModel):
    id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_revoked: bool
    
    class Config:
        from_attributes = True
