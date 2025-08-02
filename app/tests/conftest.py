import pytest
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app

@pytest.fixture(scope="module")
def client() -> Generator:
    """
    A fixture to provide a TestClient instance for the tests.
    """
    with TestClient(app) as c:
        yield c
