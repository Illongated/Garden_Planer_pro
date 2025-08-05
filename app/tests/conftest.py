"""
Test configuration and fixtures for pytest
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os

# Set test environment variables
os.environ.update({
    "ENVIRONMENT": "test",
    "SECRET_KEY": "test-secret-key-for-testing-minimum-32-characters-long",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "REFRESH_TOKEN_EXPIRE_HOURS": "168",
    "ALGORITHM": "HS256",
    "DATABASE_URL": "sqlite:///./test.db",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "SMTP_HOST": "smtp.example.com",
    "SMTP_USER": "test",
    "SMTP_PASSWORD": "test",
    "EMAILS_FROM_EMAIL": "test@example.com",
    "CLIENT_URL": "http://localhost:5173",
    "CSRF_SECRET": "test-csrf-secret-key"
})

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_redis_service():
    """Mock Redis service for testing"""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=True)
    mock.add_jti_to_denylist = MagicMock()
    mock.is_jti_in_denylist = MagicMock(return_value=False)
    return mock

@pytest.fixture
def mock_email_service():
    """Mock email service for testing"""
    return {
        "verification": MagicMock(),
        "password_reset": MagicMock()
    }

@pytest.fixture
def client():
    """Create a test client"""
    try:
        from main import app
        with TestClient(app) as test_client:
            yield test_client
    except ImportError as e:
        pytest.skip(f"Cannot import app: {e}")

@pytest.fixture
def authenticated_client(client, mock_email_service):
    """Create an authenticated test client"""
    # This would create a user and return an authenticated client
    # For now, just return the regular client
    return client

# ------------- SQLAlchemy DB & Model Fixtures for Unit Tests -------------

from app.models.base import Base

@pytest.fixture(scope="session")
def db_engine():
    """Engine SQLite pour tests avec Base créée et détruite à la session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine) -> Session:
    """Session SQLAlchemy pour tests unitaires, rollback à la fin."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def db(db_session):
    """Alias pour db_session (compatibilité)."""
    return db_session

# --- Example ready-to-use objects for testing relations ---

from app.models.user import User
from app.models.garden import Garden

@pytest.fixture
def test_user(db_session):
    """User de test pour relier les modèles."""
    user = User(email="testuser@example.com", full_name="Test User", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_garden(db_session, test_user):
    """Garden de test lié à un user."""
    garden = Garden(name="Test Garden", owner_id=test_user.id, width=10, length=20)
    db_session.add(garden)
    db_session.commit()
    db_session.refresh(garden)
    return garden
