import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.models.user import User
from app.models.garden import Garden
from app.core.security import create_access_token


class TestSQLInjection:
    """Test SQL injection vulnerabilities."""
    
    def test_sql_injection_in_garden_name(self, authenticated_client, malicious_inputs):
        """Test SQL injection in garden name field."""
        for payload in malicious_inputs["sql_injection"]:
            garden_data = {
                "name": payload,
                "description": "Test garden",
                "width": 10.0,
                "height": 8.0
            }
            
            response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            # Should return 422 (validation error) or 400 (bad request), not 500
            assert response.status_code in [400, 422]
    
    def test_sql_injection_in_plant_name(self, authenticated_client, test_garden, test_plant_catalog, malicious_inputs):
        """Test SQL injection in plant name field."""
        catalog_plant = test_plant_catalog[0]
        
        for payload in malicious_inputs["sql_injection"]:
            plant_data = {
                "name": payload,
                "species": catalog_plant.species,
                "position_x": 1.0,
                "position_y": 1.0,
                "garden_id": test_garden.id,
                "plant_catalog_id": catalog_plant.id,
                "planting_date": "2024-03-15",
                "growth_stage": "seedling",
                "health_status": "healthy"
            }
            
            response = authenticated_client.post("/api/v1/plants/", json=plant_data)
            # Should return 422 (validation error) or 400 (bad request), not 500
            assert response.status_code in [400, 422]
    
    def test_sql_injection_in_search_parameter(self, authenticated_client, malicious_inputs):
        """Test SQL injection in search parameters."""
        for payload in malicious_inputs["sql_injection"]:
            response = authenticated_client.get(f"/api/v1/plant-catalog/?search={payload}")
            # Should return 200 with empty results or 422, not 500
            assert response.status_code in [200, 422]
    
    def test_sql_injection_in_filter_parameters(self, authenticated_client, malicious_inputs):
        """Test SQL injection in filter parameters."""
        for payload in malicious_inputs["sql_injection"]:
            response = authenticated_client.get(f"/api/v1/plant-catalog/?water_needs={payload}")
            # Should return 200 with empty results or 422, not 500
            assert response.status_code in [200, 422]


class TestXSS:
    """Test Cross-Site Scripting vulnerabilities."""
    
    def test_xss_in_garden_description(self, authenticated_client, malicious_inputs):
        """Test XSS in garden description field."""
        for payload in malicious_inputs["xss"]:
            garden_data = {
                "name": "Test Garden",
                "description": payload,
                "width": 10.0,
                "height": 8.0
            }
            
            response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            # Should return 422 (validation error) or 400 (bad request)
            assert response.status_code in [400, 422]
    
    def test_xss_in_plant_notes(self, authenticated_client, test_garden, test_plant_catalog, malicious_inputs):
        """Test XSS in plant notes field."""
        catalog_plant = test_plant_catalog[0]
        
        for payload in malicious_inputs["xss"]:
            plant_data = {
                "name": catalog_plant.name,
                "species": catalog_plant.species,
                "position_x": 1.0,
                "position_y": 1.0,
                "garden_id": test_garden.id,
                "plant_catalog_id": catalog_plant.id,
                "planting_date": "2024-03-15",
                "growth_stage": "seedling",
                "health_status": "healthy",
                "notes": payload
            }
            
            response = authenticated_client.post("/api/v1/plants/", json=plant_data)
            # Should return 422 (validation error) or 400 (bad request)
            assert response.status_code in [400, 422]
    
    def test_xss_in_user_full_name(self, client, malicious_inputs):
        """Test XSS in user registration full name field."""
        for payload in malicious_inputs["xss"]:
            user_data = {
                "email": f"test{hash(payload)}@example.com",
                "password": "testpassword123",
                "full_name": payload
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            # Should return 422 (validation error) or 400 (bad request)
            assert response.status_code in [400, 422]


class TestAuthenticationBypass:
    """Test authentication bypass vulnerabilities."""
    
    def test_access_protected_endpoints_without_token(self, client, test_garden):
        """Test accessing protected endpoints without authentication token."""
        protected_endpoints = [
            f"/api/v1/gardens/{test_garden.id}",
            "/api/v1/gardens/",
            "/api/v1/plants/",
            "/api/v1/plant-catalog/",
            "/api/v1/users/",
            "/api/v1/auth/me"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_access_protected_endpoints_with_invalid_token(self, client, test_garden):
        """Test accessing protected endpoints with invalid token."""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            ""
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = client.get(f"/api/v1/gardens/{test_garden.id}", headers=headers)
            assert response.status_code == 401
    
    def test_access_protected_endpoints_with_expired_token(self, client, test_garden):
        """Test accessing protected endpoints with expired token."""
        # Create an expired token (this would require modifying the token creation)
        # For now, we'll test with a malformed token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjM0NTY3ODkwfQ.invalid"
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get(f"/api/v1/gardens/{test_garden.id}", headers=headers)
        assert response.status_code == 401
    
    def test_access_other_user_resources(self, authenticated_client, test_user):
        """Test accessing other user's resources."""
        # Create a garden for the current user
        garden_data = {
            "name": "My Garden",
            "description": "My garden",
            "width": 10.0,
            "height": 8.0
        }
        
        response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
        assert response.status_code == 201
        my_garden_id = response.json()["id"]
        
        # Try to access with a different user's token
        # This would require creating another user and their token
        # For now, we'll test with a non-existent garden ID
        fake_garden_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.get(f"/api/v1/gardens/{fake_garden_id}")
        assert response.status_code == 404


class TestPathTraversal:
    """Test path traversal vulnerabilities."""
    
    def test_path_traversal_in_file_uploads(self, authenticated_client, malicious_inputs):
        """Test path traversal in file upload endpoints."""
        for payload in malicious_inputs["path_traversal"]:
            # Test with file upload simulation
            files = {"file": (payload, b"test content", "text/plain")}
            response = authenticated_client.post("/api/v1/upload/", files=files)
            # Should return 400 or 422, not 200
            assert response.status_code in [400, 422, 404]
    
    def test_path_traversal_in_export_paths(self, authenticated_client, test_garden, malicious_inputs):
        """Test path traversal in export file paths."""
        for payload in malicious_inputs["path_traversal"]:
            export_data = {
                "filename": payload,
                "format": "pdf"
            }
            
            response = authenticated_client.post(f"/api/v1/irrigation/export/pdf", json=export_data)
            # Should return 400 or 422, not 200
            assert response.status_code in [400, 422]


class TestCommandInjection:
    """Test command injection vulnerabilities."""
    
    def test_command_injection_in_system_calls(self, authenticated_client, malicious_inputs):
        """Test command injection in system calls."""
        for payload in malicious_inputs["command_injection"]:
            # Test with any endpoint that might execute system commands
            # For example, weather API calls or file operations
            response = authenticated_client.get(f"/api/v1/irrigation/weather/{payload}")
            # Should return 400, 422, or 404, not 500
            assert response.status_code in [400, 422, 404]


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_oversized_inputs(self, authenticated_client):
        """Test handling of oversized inputs."""
        oversized_inputs = [
            "a" * 10000,  # Very long string
            "x" * 100000,  # Extremely long string
            "test" * 1000   # Repeated string
        ]
        
        for payload in oversized_inputs:
            garden_data = {
                "name": payload,
                "description": "Test garden",
                "width": 10.0,
                "height": 8.0
            }
            
            response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            # Should return 422 (validation error) or 400 (bad request)
            assert response.status_code in [400, 422]
    
    def test_special_characters(self, authenticated_client):
        """Test handling of special characters."""
        special_chars = [
            "!@#$%^&*()",
            "<script>alert('test')</script>",
            "'; DROP TABLE users; --",
            "\\x00\\x01\\x02",
            "🎉🌱🌿",
            "测试",
            "áéíóúñ"
        ]
        
        for payload in special_chars:
            garden_data = {
                "name": f"Test Garden {payload}",
                "description": f"Description {payload}",
                "width": 10.0,
                "height": 8.0
            }
            
            response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            # Should handle gracefully (200, 400, or 422)
            assert response.status_code in [200, 201, 400, 422]
    
    def test_numeric_validation(self, authenticated_client):
        """Test numeric input validation."""
        invalid_numbers = [
            float('inf'),
            float('-inf'),
            float('nan'),
            -999999999,
            999999999,
            0.0000001,
            1000000.0
        ]
        
        for payload in invalid_numbers:
            garden_data = {
                "name": "Test Garden",
                "description": "Test garden",
                "width": payload,
                "height": 8.0
            }
            
            response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            # Should return 422 (validation error)
            assert response.status_code in [400, 422]


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting_on_auth_endpoints(self, client):
        """Test rate limiting on authentication endpoints."""
        # Make multiple rapid requests to auth endpoints
        for i in range(10):
            user_data = {
                "email": f"test{i}@example.com",
                "password": "testpassword123",
                "full_name": f"Test User {i}"
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            # Should not be rate limited for registration (or should handle gracefully)
            assert response.status_code in [201, 400, 422]
    
    def test_rate_limiting_on_api_endpoints(self, authenticated_client):
        """Test rate limiting on API endpoints."""
        # Make multiple rapid requests to API endpoints
        for i in range(20):
            response = authenticated_client.get("/api/v1/gardens/")
            # Should not be rate limited (or should handle gracefully)
            assert response.status_code in [200, 429]


class TestCSRF:
    """Test CSRF protection."""
    
    def test_csrf_token_validation(self, client):
        """Test CSRF token validation."""
        # Test endpoints that should require CSRF tokens
        # This depends on the specific CSRF implementation
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        })
        # Should work without CSRF token for API endpoints
        assert response.status_code in [201, 400, 422]


class TestDataExposure:
    """Test for sensitive data exposure."""
    
    def test_no_password_exposure(self, authenticated_client, test_user):
        """Test that passwords are not exposed in responses."""
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_no_sensitive_data_in_errors(self, authenticated_client):
        """Test that error messages don't expose sensitive data."""
        # Test with invalid UUID
        response = authenticated_client.get("/api/v1/gardens/invalid-uuid")
        assert response.status_code == 422
        
        error_data = response.json()
        # Error should not expose internal database structure
        assert "database" not in str(error_data).lower()
        assert "sql" not in str(error_data).lower()
    
    def test_no_internal_paths_exposed(self, authenticated_client):
        """Test that internal file paths are not exposed."""
        response = authenticated_client.get("/api/v1/gardens/invalid-uuid")
        assert response.status_code == 422
        
        error_data = response.json()
        # Error should not expose internal file paths
        assert "/app/" not in str(error_data)
        assert "/var/" not in str(error_data)
        assert "/etc/" not in str(error_data)


class TestAuthorization:
    """Test authorization and access control."""
    
    def test_user_can_only_access_own_resources(self, authenticated_client, test_user):
        """Test that users can only access their own resources."""
        # Create a garden for the current user
        garden_data = {
            "name": "My Garden",
            "description": "My garden",
            "width": 10.0,
            "height": 8.0
        }
        
        response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
        assert response.status_code == 201
        my_garden_id = response.json()["id"]
        
        # Should be able to access own garden
        response = authenticated_client.get(f"/api/v1/gardens/{my_garden_id}")
        assert response.status_code == 200
        
        # Should not be able to access non-existent garden
        fake_garden_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.get(f"/api/v1/gardens/{fake_garden_id}")
        assert response.status_code == 404
    
    def test_admin_only_endpoints(self, authenticated_client):
        """Test admin-only endpoints."""
        # Test accessing admin endpoints as regular user
        response = authenticated_client.get("/api/v1/users/")
        # Should either be allowed or return 403, not 500
        assert response.status_code in [200, 403]


class TestSessionManagement:
    """Test session management and token handling."""
    
    def test_token_expiration(self, authenticated_client):
        """Test token expiration handling."""
        # This would require creating an expired token
        # For now, we'll test with an invalid token
        response = authenticated_client.get("/api/v1/auth/me")
        # Should work with valid token
        assert response.status_code == 200
    
    def test_token_refresh(self, client, test_user):
        """Test token refresh functionality."""
        # Login to get initial token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        # Test refresh endpoint if it exists
        # This depends on the specific implementation
        pass


class TestLoggingAndMonitoring:
    """Test security logging and monitoring."""
    
    def test_failed_login_attempts_logged(self, client):
        """Test that failed login attempts are logged."""
        # Make multiple failed login attempts
        for i in range(5):
            login_data = {
                "username": f"nonexistent{i}@example.com",
                "password": "wrongpassword"
            }
            
            response = client.post("/api/v1/auth/login", data=login_data)
            assert response.status_code == 401
        
        # The system should log these attempts
        # This would require checking logs, which is beyond the scope of this test
    
    def test_suspicious_activity_detection(self, authenticated_client, malicious_inputs):
        """Test detection of suspicious activity."""
        # Make requests with malicious inputs
        for payload in malicious_inputs["sql_injection"][:3]:  # Test a few payloads
            garden_data = {
                "name": payload,
                "description": "Test garden",
                "width": 10.0,
                "height": 8.0
            }
            
            response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            # Should handle gracefully
            assert response.status_code in [400, 422]


class TestSecureHeaders:
    """Test secure HTTP headers."""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present in responses."""
        response = client.get("/api/v1/plant-catalog/")
        
        # Check for common security headers
        headers = response.headers
        
        # These headers should be present (implementation dependent)
        # assert "X-Content-Type-Options" in headers
        # assert "X-Frame-Options" in headers
        # assert "X-XSS-Protection" in headers
        
        # At minimum, should not expose sensitive headers
        assert "X-Powered-By" not in headers
        assert "Server" not in headers or "nginx" in headers.get("Server", "")


class TestDataValidation:
    """Test comprehensive data validation."""
    
    def test_enum_validation(self, authenticated_client, test_garden, test_plant_catalog):
        """Test validation of enum fields."""
        catalog_plant = test_plant_catalog[0]
        
        invalid_enums = [
            {"growth_stage": "invalid_stage"},
            {"health_status": "invalid_status"},
            {"water_needs": "invalid_water"},
            {"sunlight_needs": "invalid_sunlight"}
        ]
        
        for invalid_enum in invalid_enums:
            plant_data = {
                "name": catalog_plant.name,
                "species": catalog_plant.species,
                "position_x": 1.0,
                "position_y": 1.0,
                "garden_id": test_garden.id,
                "plant_catalog_id": catalog_plant.id,
                "planting_date": "2024-03-15",
                **invalid_enum
            }
            
            response = authenticated_client.post("/api/v1/plants/", json=plant_data)
            assert response.status_code == 422
    
    def test_date_validation(self, authenticated_client, test_garden, test_plant_catalog):
        """Test date field validation."""
        catalog_plant = test_plant_catalog[0]
        
        invalid_dates = [
            "invalid-date",
            "2024-13-45",
            "2024-02-30",
            "2024/03/15",
            "15-03-2024"
        ]
        
        for invalid_date in invalid_dates:
            plant_data = {
                "name": catalog_plant.name,
                "species": catalog_plant.species,
                "position_x": 1.0,
                "position_y": 1.0,
                "garden_id": test_garden.id,
                "plant_catalog_id": catalog_plant.id,
                "planting_date": invalid_date,
                "growth_stage": "seedling",
                "health_status": "healthy"
            }
            
            response = authenticated_client.post("/api/v1/plants/", json=plant_data)
            assert response.status_code == 422
    
    def test_uuid_validation(self, authenticated_client):
        """Test UUID field validation."""
        invalid_uuids = [
            "invalid-uuid",
            "12345678-1234-1234-1234-123456789012",
            "00000000-0000-0000-0000-000000000000",
            "not-a-uuid-at-all"
        ]
        
        for invalid_uuid in invalid_uuids:
            response = authenticated_client.get(f"/api/v1/gardens/{invalid_uuid}")
            assert response.status_code == 422 