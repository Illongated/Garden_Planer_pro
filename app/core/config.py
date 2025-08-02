import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    # API Settings
    PROJECT_NAME: str = "Agrotique Garden Planner API"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    SECRET_KEY: str = "a_very_secret_key_that_is_long_and_secure"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRE_SECONDS: int = 3600 # 1 hour

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Returns the settings instance, cached for performance.
    """
    return Settings()

settings = get_settings()
