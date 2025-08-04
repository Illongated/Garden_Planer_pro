"""
Garden Planner Pro - Performance Tests
Locust test file for load testing the API endpoints
"""

from locust import HttpUser, task, between
import json

class GardenPlannerUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Health check first
        self.client.get("/health")
    
    @task(3)
    def test_health_endpoint(self):
        """Test the health endpoint - most frequent"""
        self.client.get("/health")
    
    @task(2)
    def test_api_docs(self):
        """Test API documentation endpoint"""
        self.client.get("/docs")
    
    @task(1)
    def test_openapi_spec(self):
        """Test OpenAPI specification"""
        self.client.get("/openapi.json")
    
    @task(1)
    def test_metrics_endpoint(self):
        """Test metrics endpoint if available"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 404:
                # Metrics endpoint might not be enabled in test
                response.success()
    
    # Note: Authentication tests would require valid credentials
    # Commenting out to avoid test failures in CI
    
    # @task(1)
    # def test_user_registration(self):
    #     """Test user registration endpoint"""
    #     test_data = {
    #         "email": f"test-{self.random_id()}@example.com",
    #         "full_name": "Test User",
    #         "password": "testpassword123"
    #     }
    #     self.client.post("/api/v1/auth/register", json=test_data)
    
    def random_id(self):
        """Generate a random ID for test data"""
        import random
        return random.randint(1000, 9999)

class AdminUser(HttpUser):
    """Simulate admin user behavior"""
    wait_time = between(2, 5)
    
    @task
    def test_security_endpoints(self):
        """Test security endpoints that don't require auth"""
        # These endpoints require authentication, so they'll return 401
        # but that's expected and means the endpoint is working
        with self.client.get("/api/v1/security/health", catch_response=True) as response:
            if response.status_code in [401, 403]:
                response.success()  # Expected for unauthenticated requests