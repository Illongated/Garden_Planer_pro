import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.core.config import settings

# Create a new async engine for the test database
test_engine = create_async_engine(settings.DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to create a new database session for each test function.
    It also creates all tables and drops them after the test.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator:
    """
    Fixture to provide a TestClient instance with an overridden DB dependency
    and a disabled rate limiter.
    """
    def override_get_db():
        yield db_session

    # Disable rate limiting for tests
    from app.core.limiter import limiter
    limiter.enabled = False

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    # Restore original state
    del app.dependency_overrides[get_db]
    limiter.enabled = True


@pytest.fixture(scope="function", autouse=True)
def mock_email_service(mocker) -> dict[str, MagicMock]:
    """
    Fixture to mock the email sending services.
    This is set to autouse=True to apply to all tests automatically.
    """
    mock_send_verification = mocker.patch(
        "app.api.v1.endpoints.auth.send_verification_email",
        autospec=True
    )
    mock_send_password_reset = mocker.patch(
        "app.api.v1.endpoints.auth.send_password_reset_email",
        autospec=True
    )
    return {
        "verification": mock_send_verification,
        "password_reset": mock_send_password_reset,
    }

@pytest.fixture(scope="function")
def mock_redis_service(mocker) -> MagicMock:
    """
    Fixture to mock the RedisService.
    """
    mock = mocker.patch(
        "app.api.v1.endpoints.auth.RedisService",
        autospec=True
    )
    instance = mock.return_value
    instance.is_jti_in_denylist.return_value = False # Default to not being in denylist
    return instance
