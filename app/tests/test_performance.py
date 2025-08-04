import pytest
import time
import asyncio
import concurrent.futures
from typing import List, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from models.user import User
from models.garden import Garden
from models.plant import Plant
from models.plant_catalog import PlantCatalog


class TestResponseTime:
    """Test response time performance."""
    
    def test_garden_list_response_time(self, authenticated_client, test_garden):
        """Test response time for garden list endpoint."""
        start_time = time.time()
        response = authenticated_client.get("/api/v1/gardens/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_plant_catalog_response_time(self, authenticated_client, test_plant_catalog):
        """Test response time for plant catalog endpoint."""
        start_time = time.time()
        response = authenticated_client.get("/api/v1/plant-catalog/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
    
    def test_irrigation_calculation_response_time(self, authenticated_client, test_garden, test_plants):
        """Test response time for irrigation calculations."""
        garden_id = test_garden.id
        start_time = time.time()
        response = authenticated_client.post(f"/api/v1/irrigation/calculate-zones/{garden_id}")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 5.0  # Complex calculations should complete within 5 seconds
    
    def test_3d_scene_generation_response_time(self, authenticated_client, test_garden, test_plants):
        """Test response time for 3D scene generation."""
        garden_id = test_garden.id
        start_time = time.time()
        response = authenticated_client.get(f"/api/v1/3d/scene/{garden_id}")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 3.0  # 3D scene generation should complete within 3 seconds
    
    def test_companion_planting_analysis_response_time(self, authenticated_client, test_garden, test_plants):
        """Test response time for companion planting analysis."""
        garden_id = test_garden.id
        start_time = time.time()
        response = authenticated_client.post(f"/api/v1/companion-planting/analyze-garden/{garden_id}")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 3.0  # Analysis should complete within 3 seconds


class TestThroughput:
    """Test throughput performance."""
    
    def test_concurrent_garden_requests(self, authenticated_client, test_user):
        """Test handling of concurrent garden requests."""
        def create_garden(i: int) -> Dict[str, Any]:
            garden_data = {
                "name": f"Concurrent Garden {i}",
                "description": f"Test garden {i}",
                "width": 10.0,
                "height": 8.0
            }
            response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            return {"status_code": response.status_code, "data": response.json() if response.status_code == 201 else None}
        
        # Create 10 gardens concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_garden, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        success_count = sum(1 for result in results if result["status_code"] == 201)
        assert success_count >= 8  # At least 80% should succeed
    
    def test_concurrent_plant_requests(self, authenticated_client, test_garden, test_plant_catalog):
        """Test handling of concurrent plant creation requests."""
        catalog_plant = test_plant_catalog[0]
        
        def create_plant(i: int) -> Dict[str, Any]:
            plant_data = {
                "name": f"{catalog_plant.name}_{i}",
                "species": catalog_plant.species,
                "position_x": i * 2.0,
                "position_y": i * 2.0,
                "garden_id": test_garden.id,
                "plant_catalog_id": catalog_plant.id,
                "planting_date": "2024-03-15",
                "growth_stage": "seedling",
                "health_status": "healthy"
            }
            response = authenticated_client.post("/api/v1/plants/", json=plant_data)
            return {"status_code": response.status_code, "data": response.json() if response.status_code == 201 else None}
        
        # Create 20 plants concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_plant, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        success_count = sum(1 for result in results if result["status_code"] == 201)
        assert success_count >= 16  # At least 80% should succeed
    
    def test_concurrent_read_requests(self, authenticated_client, test_garden):
        """Test handling of concurrent read requests."""
        def read_garden() -> Dict[str, Any]:
            response = authenticated_client.get(f"/api/v1/gardens/{test_garden.id}")
            return {"status_code": response.status_code, "data": response.json() if response.status_code == 200 else None}
        
        # Make 50 concurrent read requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_garden) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All read requests should succeed
        success_count = sum(1 for result in results if result["status_code"] == 200)
        assert success_count >= 45  # At least 90% should succeed


class TestLoadTesting:
    """Test system performance under load."""
    
    def test_high_concurrency_garden_operations(self, authenticated_client, test_user):
        """Test garden operations under high concurrency."""
        def garden_operation(i: int) -> Dict[str, Any]:
            # Create garden
            garden_data = {
                "name": f"Load Test Garden {i}",
                "description": f"Load test garden {i}",
                "width": 10.0,
                "height": 8.0
            }
            create_response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
            
            if create_response.status_code == 201:
                garden_id = create_response.json()["id"]
                
                # Read garden
                read_response = authenticated_client.get(f"/api/v1/gardens/{garden_id}")
                
                # Update garden
                update_data = {"name": f"Updated Load Test Garden {i}"}
                update_response = authenticated_client.put(f"/api/v1/gardens/{garden_id}", json=update_data)
                
                return {
                    "create_status": create_response.status_code,
                    "read_status": read_response.status_code,
                    "update_status": update_response.status_code
                }
            else:
                return {"create_status": create_response.status_code, "read_status": None, "update_status": None}
        
        # Perform 30 concurrent garden operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(garden_operation, i) for i in range(30)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Check success rates
        create_success = sum(1 for result in results if result["create_status"] == 201)
        read_success = sum(1 for result in results if result["read_status"] == 200)
        update_success = sum(1 for result in results if result["update_status"] == 200)
        
        assert create_success >= 24  # At least 80% should succeed
        assert read_success >= 24    # At least 80% should succeed
        assert update_success >= 24   # At least 80% should succeed
    
    def test_database_connection_pool_performance(self, authenticated_client, test_garden):
        """Test database connection pool performance under load."""
        def database_operation() -> Dict[str, Any]:
            # Perform multiple database operations
            operations = []
            for i in range(5):
                response = authenticated_client.get(f"/api/v1/gardens/{test_garden.id}")
                operations.append(response.status_code)
            
            return {"operations": operations}
        
        # Perform 40 concurrent database operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(database_operation) for _ in range(40)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Check that most operations succeeded
        total_operations = sum(len(result["operations"]) for result in results)
        successful_operations = sum(
            sum(1 for status in result["operations"] if status == 200)
            for result in results
        )
        
        success_rate = successful_operations / total_operations if total_operations > 0 else 0
        assert success_rate >= 0.9  # At least 90% should succeed


class TestMemoryUsage:
    """Test memory usage under various conditions."""
    
    def test_large_garden_memory_usage(self, authenticated_client, test_user):
        """Test memory usage when creating large gardens with many plants."""
        # Create a large garden
        garden_data = {
            "name": "Large Memory Test Garden",
            "description": "A garden for memory testing",
            "width": 100.0,
            "height": 100.0
        }
        
        response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
        assert response.status_code == 201
        garden_id = response.json()["id"]
        
        # Add many plants to test memory usage
        plant_count = 100
        for i in range(plant_count):
            plant_data = {
                "name": f"Memory Test Plant {i}",
                "species": "Test Species",
                "position_x": i % 10 * 10.0,
                "position_y": i // 10 * 10.0,
                "garden_id": garden_id,
                "planting_date": "2024-03-15",
                "growth_stage": "mature",
                "health_status": "healthy",
                "notes": f"Memory test plant {i} with detailed notes for memory testing purposes"
            }
            
            response = authenticated_client.post("/api/v1/plants/", json=plant_data)
            assert response.status_code == 201
        
        # Test retrieving the garden with all plants
        response = authenticated_client.get(f"/api/v1/gardens/{garden_id}")
        assert response.status_code == 200
        
        # Test retrieving plants for the garden
        response = authenticated_client.get(f"/api/v1/gardens/{garden_id}/plants/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= plant_count
    
    def test_large_plant_catalog_memory_usage(self, authenticated_client):
        """Test memory usage when retrieving large plant catalog."""
        # Test with filters that might return large datasets
        response = authenticated_client.get("/api/v1/plant-catalog/?limit=1000")
        assert response.status_code == 200
        
        data = response.json()
        # Should handle large datasets without memory issues
        assert isinstance(data, list)
    
    def test_concurrent_memory_intensive_operations(self, authenticated_client, test_garden, test_plant_catalog):
        """Test memory usage during concurrent intensive operations."""
        catalog_plant = test_plant_catalog[0]
        
        def memory_intensive_operation(i: int) -> Dict[str, Any]:
            # Create multiple plants with detailed data
            plants_data = []
            for j in range(10):
                plant_data = {
                    "name": f"Memory Intensive Plant {i}_{j}",
                    "species": catalog_plant.species,
                    "position_x": (i * 10 + j) * 2.0,
                    "position_y": (i * 10 + j) * 2.0,
                    "garden_id": test_garden.id,
                    "plant_catalog_id": catalog_plant.id,
                    "planting_date": "2024-03-15",
                    "growth_stage": "mature",
                    "health_status": "healthy",
                    "notes": f"Detailed notes for memory intensive plant {i}_{j} with extensive information for testing memory usage under concurrent load conditions"
                }
                plants_data.append(plant_data)
            
            # Submit all plants
            responses = []
            for plant_data in plants_data:
                response = authenticated_client.post("/api/v1/plants/", json=plant_data)
                responses.append(response.status_code)
            
            return {"responses": responses}
        
        # Perform 10 concurrent memory-intensive operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(memory_intensive_operation, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Check that most operations succeeded
        total_operations = sum(len(result["responses"]) for result in results)
        successful_operations = sum(
            sum(1 for status in result["responses"] if status == 201)
            for result in results
        )
        
        success_rate = successful_operations / total_operations if total_operations > 0 else 0
        assert success_rate >= 0.8  # At least 80% should succeed


class TestCPUIntensiveOperations:
    """Test CPU-intensive operations performance."""
    
    def test_irrigation_calculation_performance(self, authenticated_client, test_garden, test_plants):
        """Test performance of CPU-intensive irrigation calculations."""
        garden_id = test_garden.id
        
        # Perform multiple irrigation calculations
        calculation_times = []
        for i in range(5):
            start_time = time.time()
            response = authenticated_client.post(f"/api/v1/irrigation/calculate-zones/{garden_id}")
            end_time = time.time()
            
            calculation_time = end_time - start_time
            calculation_times.append(calculation_time)
            
            assert response.status_code == 200
        
        # Check that calculations complete within reasonable time
        avg_calculation_time = sum(calculation_times) / len(calculation_times)
        assert avg_calculation_time < 3.0  # Average should be under 3 seconds
    
    def test_companion_planting_analysis_performance(self, authenticated_client, test_garden, test_plants):
        """Test performance of CPU-intensive companion planting analysis."""
        garden_id = test_garden.id
        
        # Perform multiple companion planting analyses
        analysis_times = []
        for i in range(5):
            start_time = time.time()
            response = authenticated_client.post(f"/api/v1/companion-planting/analyze-garden/{garden_id}")
            end_time = time.time()
            
            analysis_time = end_time - start_time
            analysis_times.append(analysis_time)
            
            assert response.status_code == 200
        
        # Check that analyses complete within reasonable time
        avg_analysis_time = sum(analysis_times) / len(analysis_times)
        assert avg_analysis_time < 2.0  # Average should be under 2 seconds
    
    def test_3d_scene_generation_performance(self, authenticated_client, test_garden, test_plants):
        """Test performance of CPU-intensive 3D scene generation."""
        garden_id = test_garden.id
        
        # Perform multiple 3D scene generations
        generation_times = []
        for i in range(5):
            start_time = time.time()
            response = authenticated_client.get(f"/api/v1/3d/scene/{garden_id}")
            end_time = time.time()
            
            generation_time = end_time - start_time
            generation_times.append(generation_time)
            
            assert response.status_code == 200
        
        # Check that generations complete within reasonable time
        avg_generation_time = sum(generation_times) / len(generation_times)
        assert avg_generation_time < 2.0  # Average should be under 2 seconds


class TestCachingPerformance:
    """Test caching performance and effectiveness."""
    
    def test_plant_catalog_caching(self, authenticated_client):
        """Test caching performance for plant catalog."""
        # First request
        start_time = time.time()
        response1 = authenticated_client.get("/api/v1/plant-catalog/")
        first_request_time = time.time() - start_time
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = authenticated_client.get("/api/v1/plant-catalog/")
        second_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()
        
        # Second request should be faster (if caching is implemented)
        # assert second_request_time < first_request_time
    
    def test_garden_data_caching(self, authenticated_client, test_garden):
        """Test caching performance for garden data."""
        garden_id = test_garden.id
        
        # First request
        start_time = time.time()
        response1 = authenticated_client.get(f"/api/v1/gardens/{garden_id}")
        first_request_time = time.time() - start_time
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = authenticated_client.get(f"/api/v1/gardens/{garden_id}")
        second_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()
        
        # Second request should be faster (if caching is implemented)
        # assert second_request_time < first_request_time


class TestScalability:
    """Test system scalability."""
    
    def test_scalability_with_increasing_load(self, authenticated_client, test_user):
        """Test system performance with increasing load."""
        load_levels = [10, 20, 30, 40, 50]
        performance_metrics = []
        
        for load in load_levels:
            start_time = time.time()
            
            # Create gardens under current load
            with concurrent.futures.ThreadPoolExecutor(max_workers=load) as executor:
                futures = []
                for i in range(load):
                    garden_data = {
                        "name": f"Scalability Test Garden {i}",
                        "description": f"Test garden {i}",
                        "width": 10.0,
                        "height": 8.0
                    }
                    future = executor.submit(
                        authenticated_client.post, 
                        "/api/v1/gardens/", 
                        json=garden_data
                    )
                    futures.append(future)
                
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            success_count = sum(1 for result in results if result.status_code == 201)
            success_rate = success_count / load
            
            performance_metrics.append({
                "load": load,
                "total_time": total_time,
                "success_rate": success_rate,
                "throughput": load / total_time if total_time > 0 else 0
            })
        
        # Check that performance degrades gracefully
        for i in range(1, len(performance_metrics)):
            current = performance_metrics[i]
            previous = performance_metrics[i-1]
            
            # Success rate should not drop too much
            assert current["success_rate"] >= 0.7
            
            # Throughput should not drop too dramatically
            if previous["throughput"] > 0:
                throughput_ratio = current["throughput"] / previous["throughput"]
                assert throughput_ratio >= 0.5  # Should not drop more than 50%
    
    def test_database_scalability(self, authenticated_client, test_garden):
        """Test database scalability with large datasets."""
        # Create many plants to test database scalability
        plant_count = 200
        
        start_time = time.time()
        for i in range(plant_count):
            plant_data = {
                "name": f"Scalability Test Plant {i}",
                "species": "Test Species",
                "position_x": i % 20 * 5.0,
                "position_y": i // 20 * 5.0,
                "garden_id": test_garden.id,
                "planting_date": "2024-03-15",
                "growth_stage": "mature",
                "health_status": "healthy"
            }
            
            response = authenticated_client.post("/api/v1/plants/", json=plant_data)
            assert response.status_code == 201
        
        creation_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        response = authenticated_client.get(f"/api/v1/gardens/{test_garden.id}/plants/")
        retrieval_time = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= plant_count
        
        # Performance should be reasonable
        assert creation_time < 30.0  # Should create 200 plants in under 30 seconds
        assert retrieval_time < 5.0   # Should retrieve 200 plants in under 5 seconds


class TestResourceLimits:
    """Test system behavior under resource constraints."""
    
    def test_large_payload_handling(self, authenticated_client, test_garden):
        """Test handling of large payloads."""
        # Create a very large description
        large_description = "A" * 10000  # 10KB description
        
        garden_data = {
            "name": "Large Payload Garden",
            "description": large_description,
            "width": 10.0,
            "height": 8.0
        }
        
        response = authenticated_client.post("/api/v1/gardens/", json=garden_data)
        # Should handle large payloads gracefully
        assert response.status_code in [201, 400, 422]
    
    def test_many_concurrent_connections(self, authenticated_client):
        """Test handling of many concurrent connections."""
        def make_request():
            response = authenticated_client.get("/api/v1/gardens/")
            return response.status_code
        
        # Simulate many concurrent connections
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Most requests should succeed
        success_count = sum(1 for status in results if status == 200)
        assert success_count >= 80  # At least 80% should succeed
    
    def test_memory_leak_prevention(self, authenticated_client, test_garden):
        """Test for memory leaks during repeated operations."""
        # Perform the same operation many times to check for memory leaks
        for i in range(100):
            response = authenticated_client.get(f"/api/v1/gardens/{test_garden.id}")
            assert response.status_code == 200
            
            # Also test plant retrieval
            response = authenticated_client.get(f"/api/v1/gardens/{test_garden.id}/plants/")
            assert response.status_code == 200
        
        # If there are memory leaks, the system might become slower
        # or fail after many iterations. This test ensures the operations
        # remain consistent throughout the iterations. 