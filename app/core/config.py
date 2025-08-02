import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    # Environment
    ENVIRONMENT: str = "development"

    # API Settings
    PROJECT_NAME: str = "Agrotique Garden Planner API"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    SECRET_KEY: str = "a_very_secret_key_that_is_long_and_secure"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database settings
    # For production, use a robust database like PostgreSQL.
    # For local development and to make this project runnable out-of-the-box, we use SQLite.
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrotique.db"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRE_SECONDS: int = 3600 # 1 hour

    # Email settings for mailtrap
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.mailtrap.io"
    SMTP_USER: str = "your_mailtrap_user"
    SMTP_PASSWORD: str = "your_mailtrap_password"
    EMAILS_FROM_EMAIL: str = "info@agrotique.com"
    EMAILS_FROM_NAME: str = "Agrotique Garden Planner"

    # CSRF Protection
    CSRF_SECRET: str = "a_very_secret_csrf_key"

    # Frontend URL
    CLIENT_URL: str = "http://localhost:5173"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    """
    Returns the settings instance, cached for performance.
    """
    return Settings()

settings = get_settings()
