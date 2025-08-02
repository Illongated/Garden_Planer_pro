import uuid
from fastapi.testclient import TestClient

def test_user_registration(client: TestClient):
    """
    Test user registration success and failure for duplicate email.
    """
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "a_strong_password"

    # Successful registration
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Test User", "password": password},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "hashed_password" not in data

    # Duplicate registration
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Another User", "password": "another_password"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_for_access_token(client: TestClient):
    """
    Test user login success and failure.
    """
    email = f"logintest_{uuid.uuid4()}@example.com"
    password = "a_very_secure_password"

    # First, register the user
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Login Test User", "password": password},
    )

    # Successful login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Failed login (wrong password)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_read_current_user(client: TestClient):
    """
    Test accessing a protected route with and without a valid token.
    """
    email = f"protected_route_test_{uuid.uuid4()}@example.com"
    password = "password123"

    # Register and login to get a token
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Protected User", "password": password},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    access_token = login_response.json()["access_token"]

    # Access protected route with token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email

    # Access protected route without token
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401 # FastAPI's dependency will catch this
    assert "Not authenticated" in response.json()["detail"]

    # Access protected route with invalid token
    headers = {"Authorization": "Bearer an_invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]
