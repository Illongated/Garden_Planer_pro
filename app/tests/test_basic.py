import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data

def test_docs_endpoint():
    """Test that the docs endpoint is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_main_import():
    """Test that the main module can be imported"""
    import main
    assert main.app is not None 