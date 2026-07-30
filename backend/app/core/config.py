import os
import sys
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

def get_mandatory_secret_key() -> str:
    secret = os.getenv("SECRET_KEY")
    if not secret:
        print("CRITICAL ERROR: SECRET_KEY environment variable is missing. It is mandatory for application startup.")
        sys.exit(1)
    if len(secret) < 32:
        print("CRITICAL ERROR: SECRET_KEY must be at least 32 characters long for sufficient entropy.")
        sys.exit(1)
    
    weak_keys = [
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        "generate_a_secure_random_key_here",
    ]
    if secret in weak_keys or "secret" in secret.lower() or "password" in secret.lower() or secret == "1" * len(secret) or secret == "0" * len(secret):
        print("CRITICAL ERROR: SECRET_KEY must not be a default or weak value. Please generate a secure random string.")
        sys.exit(1)
    return secret


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinPilot AI"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development") # development, staging, production

    # Comma-separated list of allowed CORS origins (env-driven for prod/staging).
    BACKEND_CORS_ORIGINS: str = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")

    # Security
    SECRET_KEY: str = get_mandatory_secret_key()
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes for access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days for refresh tokens
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    
    # OAuth (Google)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/oauth/google/callback")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/finpilot")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Market Data Providers
    FMP_API_KEY: str = os.getenv("FMP_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    EXCHANGE_RATE_API_KEY: str = os.getenv("EXCHANGE_RATE_API_KEY", "")

    # AI Gateway
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
