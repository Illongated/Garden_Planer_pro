import uuid
from fastapi.testclient import TestClient
from app.core import security

# --- Helper function to get a valid token ---
def get_auth_token(client: TestClient, email_prefix: str) -> str:
    email = f"{email_prefix}_{uuid.uuid4()}@example.com"
    password = "password123"

    # Register the user
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": f"{email_prefix} User", "password": password},
    )

    # Manually verify the user's email for the test
    verification_token = security.generate_verification_token(email)
    client.get(f"/api/v1/auth/verify-email?token={verification_token}")

    # Log in to get the token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200, f"Login failed for {email}"
    return login_response.json()["access_token"]


def test_project_crud_and_permissions(client: TestClient):
    """
    Test the full lifecycle of a project, including creation, access, and permissions.
    """
    token_a = get_auth_token(client, "user_a")
    token_b = get_auth_token(client, "user_b")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. User A creates a project
    project_name = f"User A's Garden Project {uuid.uuid4()}"
    response = client.post(
        "/api/v1/projects/",
        headers=headers_a,
        json={"name": project_name, "description": "A test project"},
    )
    assert response.status_code == 201
    project_a_data = response.json()
    project_id = project_a_data["id"]
    assert project_a_data["name"] == project_name

    # 2. User A can list their project
    response = client.get("/api/v1/projects/", headers=headers_a)
    assert response.status_code == 200
    projects_list = response.json()
    assert len(projects_list) == 1
    assert projects_list[0]["id"] == project_id

    # 3. User B's project list should be empty
    response = client.get("/api/v1/projects/", headers=headers_b)
    assert response.status_code == 200
    assert len(response.json()) == 0

    # 4. User A can read their specific project
    response = client.get(f"/api/v1/projects/{project_id}", headers=headers_a)
    assert response.status_code == 200
    assert response.json()["id"] == project_id

    # 5. User B cannot read User A's project
    response = client.get(f"/api/v1/projects/{project_id}", headers=headers_b)
    assert response.status_code == 404

    # 6. User A can update their project
    updated_name = "User A's Updated Project"
    response = client.put(
        f"/api/v1/projects/{project_id}",
        headers=headers_a,
        json={"name": updated_name},
    )
    assert response.status_code == 200
    assert response.json()["name"] == updated_name

    # 7. User B cannot update User A's project
    response = client.put(
        f"/api/v1/projects/{project_id}",
        headers=headers_b,
        json={"name": "Malicious Update"},
    )
    assert response.status_code == 404

    # 8. User B cannot delete User A's project
    response = client.delete(f"/api/v1/projects/{project_id}", headers=headers_b)
    assert response.status_code == 404

    # 9. User A can delete their project
    response = client.delete(f"/api/v1/projects/{project_id}", headers=headers_a)
    assert response.status_code == 204

    # 10. The project is now gone
    response = client.get(f"/api/v1/projects/{project_id}", headers=headers_a)
    assert response.status_code == 404
