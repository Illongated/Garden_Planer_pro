import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # General
    ENVIRONMENT: str = "development"

    # API
    PROJECT_NAME: str = "Agrotique Garden Planner API"
    API_V1_STR: str = "/api/v1"

    # JWT
    SECRET_KEY: str = "a_very_secret_key_that_is_long_and_secure"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_HOURS: int = 168
    ALGORITHM: str = "HS256"

    # Database (SQLite by default, switch via .env or env var)
    DATABASE_URL: str = "sqlite:///./garden_planner.db"

    # Pooling (ignored by SQLite, useful for Postgres)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRE_SECONDS: int = 3600

    # Perf/Caching
    ENABLE_COMPRESSION: bool = True
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600
    QUERY_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 100
    RATE_LIMIT_PER_MINUTE: int = 60

    # Monitoring/Health
    ENABLE_METRICS: bool = True
    METRICS_ENDPOINT: str = "/metrics"
    ENABLE_HEALTH_CHECK: bool = True
    HEALTH_CHECK_INTERVAL: int = 30

    # CDN/Static
    CDN_URL: str = ""
    STATIC_FILES_CDN: bool = False

    # Email/Mailtrap
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.mailtrap.io"
    SMTP_USER: str = "your_mailtrap_user"
    SMTP_PASSWORD: str = "your_mailtrap_password"
    EMAILS_FROM_EMAIL: str = "info@agrotique.com"
    EMAILS_FROM_NAME: str = "Agrotique Garden Planner"

    # CSRF
    CSRF_SECRET: str = "a_very_secret_csrf_key"

    # Frontend
    CLIENT_URL: str = "http://localhost:5173"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
