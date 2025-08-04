import uuid
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from jose import jwt

from core.config import settings
from core import security

def test_user_registration(client: TestClient, mock_email_service: dict[str, MagicMock]):
    """
    Test user registration success and asserts that a verification email is sent.
    """
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "a_strong_password"

    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Test User", "password": password},
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Registration successful. Please check your email to verify your account."}

    # Assert that the verification email was called
    mock_email_service["verification"].assert_called_once()
    call_args = mock_email_service["verification"].call_args
    assert call_args.kwargs["email_to"] == email
    assert isinstance(call_args.kwargs["token"], str)

def test_registration_duplicate_email(client: TestClient):
    """
    Test that registering with a duplicate email fails.
    """
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "a_strong_password"

    # First registration should succeed
    client.post("/api/v1/auth/register", json={"email": email, "full_name": "Test User", "password": password})

    # Second registration with the same email should fail
    response = client.post("/api/v1/auth/register", json={"email": email, "full_name": "Another User", "password": "another_password"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_email_verification(client: TestClient, mock_email_service: dict[str, MagicMock]):
    """
    Test the complete email verification flow.
    """
    email = f"verify_test_{uuid.uuid4()}@example.com"
    password = "a_strong_password"

    # 1. Register user
    client.post("/api/v1/auth/register", json={"email": email, "full_name": "Verify Test", "password": password})

    # 2. Extract token from the mocked email call
    token = mock_email_service["verification"].call_args.kwargs["token"]

    # 3. Fail login because email is not verified
    login_response_fail = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_response_fail.status_code == 403
    assert "not verified" in login_response_fail.json()["detail"]

    # 4. Verify email with the token
    verify_response = client.get(f"/api/v1/auth/verify-email?token={token}")
    assert verify_response.status_code == 200
    assert verify_response.json() == {"message": "Email verified successfully. You can now log in."}

    # 5. Login should now succeed
    login_response_success = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_response_success.status_code == 200
    assert "access_token" in login_response_success.json()

def test_login_and_me_endpoint(client: TestClient):
    """
    Test successful login and accessing the /me endpoint.
    """
    email = f"login_me_test_{uuid.uuid4()}@example.com"
    password = "password123"

    # Register and manually verify user for simplicity in this test
    client.post("/api/v1/auth/register", json={"email": email, "full_name": "Me Test", "password": password})
    token = security.generate_verification_token(email)
    client.get(f"/api/v1/auth/verify-email?token={token}")

    # Login
    login_response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Access /me endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    user_data = me_response.json()
    assert user_data["email"] == email
    assert user_data["full_name"] == "Me Test"
    assert user_data["is_verified"] is True

def test_password_reset_flow(client: TestClient, mock_email_service: dict[str, MagicMock]):
    """
    Test the full password reset flow.
    """
    email = f"password_reset_{uuid.uuid4()}@example.com"
    old_password = "old_password"
    new_password = "new_password"

    # 1. Register and verify user
    client.post("/api/v1/auth/register", json={"email": email, "full_name": "Reset Test", "password": old_password})
    verification_token = security.generate_verification_token(email)
    client.get(f"/api/v1/auth/verify-email?token={verification_token}")

    # 2. Request password reset
    reset_request_response = client.post("/api/v1/auth/request-password-reset", json={"email": email})
    assert reset_request_response.status_code == 200
    mock_email_service["password_reset"].assert_called_once()
    reset_token = mock_email_service["password_reset"].call_args.kwargs["token"]

    # 3. Reset the password with the token
    reset_response = client.post("/api/v1/auth/reset-password", json={"token": reset_token, "new_password": new_password})
    assert reset_response.status_code == 200
    assert "Password has been reset" in reset_response.json()["message"]

    # 4. Login with old password should fail
    failed_login_response = client.post("/api/v1/auth/login", data={"username": email, "password": old_password})
    assert failed_login_response.status_code == 401

    # 5. Login with new password should succeed
    success_login_response = client.post("/api/v1/auth/login", data={"username": email, "password": new_password})
    assert success_login_response.status_code == 200

def test_logout_and_refresh(client: TestClient, mock_redis_service: MagicMock):
    """
    Test user logout and that the refresh token is invalidated.
    """
    email = f"logout_test_{uuid.uuid4()}@example.com"
    password = "password123"

    # 1. Register and verify
    client.post("/api/v1/auth/register", json={"email": email, "full_name": "Logout Test", "password": password})
    verification_token = security.generate_verification_token(email)
    client.get(f"/api/v1/auth/verify-email?token={verification_token}")

    # 2. Login to get tokens
    login_response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "refresh_token" in login_data
    refresh_token = login_data["refresh_token"]

    # 3. Logout
    logout_response = client.post("/api/v1/auth/logout", cookies={"refresh_token": refresh_token})
    assert logout_response.status_code == 200

    # Assert that the JTI was added to the denylist
    mock_redis_service.add_jti_to_denylist.assert_called_once()

    # 4. Try to refresh with the old token, should fail
    mock_redis_service.is_jti_in_denylist.return_value = True # Simulate that the token is now in the denylist
    refresh_response = client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401
