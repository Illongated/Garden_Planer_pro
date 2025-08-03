import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from redis import Redis
import redis.asyncio as aioredis
from unittest.mock import Mock, patch

from app.main import app
from app.db.session import get_db
from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.garden import Garden
from app.models.plant import Plant
from app.models.plant_catalog import PlantCatalog
from app.core.security import create_access_token
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create database session for testing."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator:
    """Create test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = True
        mock_redis.exists.return_value = False
        yield mock_redis


@pytest.fixture
def mock_aioredis():
    """Mock async Redis for testing."""
    with patch('app.services.redis_service.aioredis_client') as mock_aioredis:
        mock_aioredis.get.return_value = None
        mock_aioredis.set.return_value = True
        mock_aioredis.delete.return_value = True
        mock_aioredis.exists.return_value = False
        yield mock_aioredis


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    user = user_crud.create(db_session, obj_in=user_data)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Create access token for test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def authenticated_client(client, test_user_token):
    """Create authenticated test client."""
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client


@pytest.fixture
def test_garden(db_session, test_user):
    """Create a test garden."""
    garden_data = {
        "name": "Test Garden",
        "description": "A test garden",
        "width": 10.0,
        "height": 8.0,
        "user_id": test_user.id
    }
    garden = Garden(**garden_data)
    db_session.add(garden)
    db_session.commit()
    db_session.refresh(garden)
    return garden


@pytest.fixture
def test_plant_catalog(db_session):
    """Create test plant catalog entries."""
    plants = [
        {
            "name": "Tomato",
            "species": "Solanum lycopersicum",
            "family": "Solanaceae",
            "growth_duration_days": 80,
            "spacing_cm": 60,
            "water_needs": "medium",
            "sunlight_needs": "full",
            "soil_type": "loamy",
            "ph_range": "6.0-6.8",
            "max_height_cm": 200,
            "max_spread_cm": 60,
            "root_depth_cm": 30,
            "companion_plants": ["Basil", "Marigold"],
            "antagonist_plants": ["Potato", "Corn"],
            "planting_season": "spring",
            "harvest_season": "summer",
            "yield_per_plant_kg": 2.5,
            "disease_resistance": ["blight", "mildew"],
            "pest_resistance": ["aphids", "whiteflies"],
            "nutrient_requirements": {"N": "medium", "P": "high", "K": "medium"},
            "climate_zones": [5, 6, 7, 8],
            "drought_tolerance": "low",
            "frost_tolerance": "none",
            "edible_parts": ["fruit"],
            "culinary_uses": ["fresh", "cooking", "canning"],
            "medicinal_properties": ["antioxidant", "vitamin_c"],
            "storage_conditions": "cool_dry",
            "seed_life_years": 4,
            "germination_days": 7,
            "transplant_days": 21,
            "maturity_days": 70,
            "succession_planting": True,
            "crop_rotation_group": "solanaceae",
            "nitrogen_fixing": False,
            "pollinator_attractor": True,
            "deer_resistant": False,
            "rabbit_resistant": False,
            "drought_tolerant": False,
            "shade_tolerant": False,
            "container_friendly": True,
            "trellis_required": True,
            "pruning_required": True,
            "fertilizer_needs": "balanced",
            "watering_frequency": "daily",
            "mulch_beneficial": True,
            "companion_planting_notes": "Plant with basil to improve flavor and deter pests",
            "growing_tips": "Provide consistent moisture and support for indeterminate varieties",
            "harvesting_tips": "Harvest when fully colored but still firm",
            "storage_tips": "Store at room temperature until ripe, then refrigerate",
            "seed_saving_tips": "Allow fruits to fully ripen on plant before collecting seeds",
            "pest_management": "Use row covers and companion planting",
            "disease_management": "Ensure good air circulation and avoid overhead watering",
            "soil_preparation": "Add compost and ensure good drainage",
            "planting_depth_cm": 1,
            "seed_spacing_cm": 2,
            "row_spacing_cm": 90,
            "thinning_required": True,
            "thinning_spacing_cm": 30,
            "support_type": "cage",
            "support_height_cm": 150,
            "pruning_type": "suckering",
            "fertilizer_schedule": "every_2_weeks",
            "watering_method": "drip",
            "mulch_type": "straw",
            "mulch_depth_cm": 5,
            "weed_control": "mulch",
            "pest_monitoring": "weekly",
            "disease_monitoring": "weekly",
            "growth_monitoring": "weekly",
            "harvest_monitoring": "daily",
            "yield_tracking": True,
            "quality_assessment": True,
            "market_value_per_kg": 3.50,
            "labor_hours_per_plant": 0.5,
            "equipment_needs": ["cages", "trellis", "drip_irrigation"],
            "specialized_tools": ["pruning_shears", "tomato_cages"],
            "seasonal_notes": "Plant after last frost, harvest before first frost",
            "climate_adaptation": "Heat loving, protect from cold",
            "microclimate_preferences": "Full sun, sheltered from wind",
            "water_efficiency": "medium",
            "nutrient_efficiency": "high",
            "space_efficiency": "medium",
            "time_efficiency": "medium",
            "cost_efficiency": "high",
            "skill_level_required": "intermediate",
            "maintenance_level": "medium",
            "risk_level": "low",
            "reward_level": "high",
            "sustainability_score": 8,
            "biodiversity_contribution": "high",
            "ecosystem_services": ["pollination", "pest_control"],
            "carbon_sequestration": "low",
            "soil_improvement": "medium",
            "water_conservation": "medium",
            "wildlife_habitat": "medium",
            "educational_value": "high",
            "therapeutic_value": "medium",
            "aesthetic_value": "high",
            "cultural_significance": "high",
            "economic_value": "high",
            "nutritional_value": "high",
            "medicinal_value": "medium",
            "ecological_value": "medium",
            "social_value": "high",
            "historical_significance": "high",
            "future_potential": "high",
            "research_priorities": ["disease_resistance", "drought_tolerance"],
            "breeding_objectives": ["yield", "flavor", "disease_resistance"],
            "conservation_status": "secure",
            "genetic_diversity": "high",
            "adaptation_potential": "high",
            "climate_resilience": "medium",
            "sustainability_potential": "high",
            "innovation_potential": "medium",
            "market_potential": "high",
            "community_value": "high",
            "global_significance": "high"
        },
        {
            "name": "Basil",
            "species": "Ocimum basilicum",
            "family": "Lamiaceae",
            "growth_duration_days": 60,
            "spacing_cm": 30,
            "water_needs": "medium",
            "sunlight_needs": "full",
            "soil_type": "well_drained",
            "ph_range": "6.0-7.5",
            "max_height_cm": 60,
            "max_spread_cm": 30,
            "root_depth_cm": 20,
            "companion_plants": ["Tomato", "Pepper"],
            "antagonist_plants": ["Rue"],
            "planting_season": "spring",
            "harvest_season": "summer",
            "yield_per_plant_kg": 0.5,
            "disease_resistance": ["downy_mildew"],
            "pest_resistance": ["aphids"],
            "nutrient_requirements": {"N": "medium", "P": "low", "K": "low"},
            "climate_zones": [4, 5, 6, 7, 8, 9],
            "drought_tolerance": "medium",
            "frost_tolerance": "none",
            "edible_parts": ["leaves"],
            "culinary_uses": ["fresh", "cooking", "pesto"],
            "medicinal_properties": ["antibacterial", "anti_inflammatory"],
            "storage_conditions": "refrigerated",
            "seed_life_years": 5,
            "germination_days": 5,
            "transplant_days": 14,
            "maturity_days": 45,
            "succession_planting": True,
            "crop_rotation_group": "herbs",
            "nitrogen_fixing": False,
            "pollinator_attractor": True,
            "deer_resistant": True,
            "rabbit_resistant": True,
            "drought_tolerant": True,
            "shade_tolerant": False,
            "container_friendly": True,
            "trellis_required": False,
            "pruning_required": True,
            "fertilizer_needs": "light",
            "watering_frequency": "moderate",
            "mulch_beneficial": True,
            "companion_planting_notes": "Excellent companion for tomatoes, repels pests",
            "growing_tips": "Pinch off flower buds to encourage leaf growth",
            "harvesting_tips": "Harvest leaves regularly to promote bushiness",
            "storage_tips": "Store in refrigerator wrapped in damp paper towel",
            "seed_saving_tips": "Allow some plants to flower and collect seeds",
            "pest_management": "Companion planting and natural predators",
            "disease_management": "Good air circulation and avoid overhead watering",
            "soil_preparation": "Well-drained soil with organic matter",
            "planting_depth_cm": 0.5,
            "seed_spacing_cm": 1,
            "row_spacing_cm": 30,
            "thinning_required": True,
            "thinning_spacing_cm": 15,
            "support_type": "none",
            "support_height_cm": 0,
            "pruning_type": "pinching",
            "fertilizer_schedule": "monthly",
            "watering_method": "drip",
            "mulch_type": "straw",
            "mulch_depth_cm": 3,
            "weed_control": "mulch",
            "pest_monitoring": "weekly",
            "disease_monitoring": "weekly",
            "growth_monitoring": "weekly",
            "harvest_monitoring": "daily",
            "yield_tracking": True,
            "quality_assessment": True,
            "market_value_per_kg": 15.00,
            "labor_hours_per_plant": 0.2,
            "equipment_needs": ["drip_irrigation"],
            "specialized_tools": ["pruning_shears"],
            "seasonal_notes": "Plant after last frost, harvest before first frost",
            "climate_adaptation": "Heat loving, protect from cold",
            "microclimate_preferences": "Full sun, sheltered from wind",
            "water_efficiency": "high",
            "nutrient_efficiency": "high",
            "space_efficiency": "high",
            "time_efficiency": "high",
            "cost_efficiency": "high",
            "skill_level_required": "beginner",
            "maintenance_level": "low",
            "risk_level": "very_low",
            "reward_level": "high",
            "sustainability_score": 9,
            "biodiversity_contribution": "high",
            "ecosystem_services": ["pollination", "pest_control"],
            "carbon_sequestration": "low",
            "soil_improvement": "low",
            "water_conservation": "high",
            "wildlife_habitat": "medium",
            "educational_value": "high",
            "therapeutic_value": "high",
            "aesthetic_value": "high",
            "cultural_significance": "high",
            "economic_value": "high",
            "nutritional_value": "medium",
            "medicinal_value": "high",
            "ecological_value": "high",
            "social_value": "high",
            "historical_significance": "medium",
            "future_potential": "high",
            "research_priorities": ["drought_tolerance", "disease_resistance"],
            "breeding_objectives": ["flavor", "yield", "disease_resistance"],
            "conservation_status": "secure",
            "genetic_diversity": "high",
            "adaptation_potential": "high",
            "climate_resilience": "high",
            "sustainability_potential": "high",
            "innovation_potential": "medium",
            "market_potential": "high",
            "community_value": "high",
            "global_significance": "medium"
        }
    ]
    
    for plant_data in plants:
        plant = PlantCatalog(**plant_data)
        db_session.add(plant)
    
    db_session.commit()
    return db_session.query(PlantCatalog).all()


@pytest.fixture
def test_plants(db_session, test_garden, test_plant_catalog):
    """Create test plants in the garden."""
    plants = []
    for i, catalog_plant in enumerate(test_plant_catalog[:2]):
        plant_data = {
            "name": catalog_plant.name,
            "species": catalog_plant.species,
            "position_x": 1.0 + i * 2.0,
            "position_y": 1.0 + i * 2.0,
            "garden_id": test_garden.id,
            "plant_catalog_id": catalog_plant.id,
            "planting_date": "2024-03-15",
            "growth_stage": "seedling",
            "health_status": "healthy",
            "notes": f"Test plant {i+1}"
        }
        plant = Plant(**plant_data)
        db_session.add(plant)
        plants.append(plant)
    
    db_session.commit()
    return plants


@pytest.fixture
def mock_weather_api():
    """Mock weather API responses."""
    with patch('app.services.weather_service.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "current": {
                "temp": 22.5,
                "humidity": 65,
                "wind_speed": 5.2,
                "weather": [{"main": "Clear", "description": "clear sky"}]
            },
            "daily": [
                {
                    "dt": 1640995200,
                    "temp": {"day": 25.0, "night": 15.0},
                    "humidity": 60,
                    "weather": [{"main": "Clear"}]
                }
            ] * 7
        }
        yield mock_get


@pytest.fixture
def mock_irrigation_calculations():
    """Mock irrigation calculation results."""
    return {
        "zones": [
            {
                "id": "zone_1",
                "name": "High Water Needs",
                "plants": ["Tomato", "Basil"],
                "water_needs_mm_per_day": 8.5,
                "area_sqm": 12.0,
                "daily_water_volume_liters": 102.0,
                "irrigation_duration_minutes": 45,
                "equipment_recommendations": ["drip_emitters", "sprinklers"]
            }
        ],
        "hydraulic_calculations": {
            "total_flow_rate_lpm": 15.2,
            "pressure_loss_kpa": 12.5,
            "pump_power_watts": 850,
            "efficiency": 0.78
        },
        "cost_estimation": {
            "equipment_cost": 450.0,
            "installation_cost": 200.0,
            "total_cost": 650.0,
            "annual_operating_cost": 120.0
        }
    }


@pytest.fixture
def mock_companion_planting_data():
    """Mock companion planting recommendations."""
    return {
        "recommendations": [
            {
                "plant_name": "Tomato",
                "companions": [
                    {"name": "Basil", "relationship": "beneficial", "reason": "Repels pests and improves flavor"},
                    {"name": "Marigold", "relationship": "beneficial", "reason": "Deters nematodes"}
                ],
                "antagonists": [
                    {"name": "Potato", "relationship": "antagonistic", "reason": "Same family, disease risk"},
                    {"name": "Corn", "relationship": "antagonistic", "reason": "Competes for nutrients"}
                ]
            }
        ],
        "garden_optimization": {
            "compatibility_score": 0.85,
            "conflicts_detected": 2,
            "suggestions": [
                "Move tomatoes away from potatoes",
                "Add more basil around tomatoes"
            ]
        }
    }


@pytest.fixture
def mock_3d_scene_data():
    """Mock 3D scene configuration."""
    return {
        "scene_id": "test_scene",
        "garden_id": "test_garden",
        "plants": [
            {
                "id": "plant_1",
                "name": "Tomato",
                "species": "Solanum lycopersicum",
                "position": {"x": 1.0, "y": 1.0, "z": 0.0},
                "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
                "scale": {"x": 1.0, "y": 1.0, "z": 1.0},
                "growth_stage": "vegetative",
                "health": 0.9,
                "age": 45,
                "max_age": 80
            }
        ],
        "lighting": {
            "time_of_day": 12.0,
            "season": "summer",
            "weather": "clear",
            "intensity": 1.0,
            "color": {"r": 1.0, "g": 1.0, "b": 1.0}
        },
        "camera": {
            "mode": "isometric",
            "position": {"x": 5.0, "y": 5.0, "z": 10.0},
            "target": {"x": 0.0, "y": 0.0, "z": 0.0}
        }
    }


# Performance testing fixtures
@pytest.fixture
def large_garden_data():
    """Generate large garden data for performance testing."""
    return {
        "name": "Large Test Garden",
        "description": "Performance test garden",
        "width": 100.0,
        "height": 100.0,
        "plants": [
            {
                "name": f"Plant_{i}",
                "species": "Test Species",
                "position_x": i % 10 * 10.0,
                "position_y": i // 10 * 10.0,
                "growth_stage": "mature",
                "health_status": "healthy"
            }
            for i in range(100)
        ]
    }


@pytest.fixture
def mock_websocket_connection():
    """Mock WebSocket connection for testing."""
    mock_websocket = Mock()
    mock_websocket.send_text = Mock()
    mock_websocket.send_json = Mock()
    mock_websocket.close = Mock()
    return mock_websocket


# Security testing fixtures
@pytest.fixture
def malicious_inputs():
    """Provide malicious inputs for security testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ],
        "xss": [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd"
        ],
        "command_injection": [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& echo 'hacked'"
        ]
    }


# Load testing fixtures
@pytest.fixture
def concurrent_users_data():
    """Data for concurrent user testing."""
    return {
        "user_count": 100,
        "requests_per_user": 10,
        "test_duration_seconds": 60,
        "endpoints": [
            "/api/v1/gardens/",
            "/api/v1/plants/",
            "/api/v1/plant-catalog/",
            "/api/v1/irrigation/calculate"
        ]
    }


# Browser compatibility test data
@pytest.fixture
def browser_test_data():
    """Data for browser compatibility testing."""
    return {
        "browsers": [
            {"name": "Chrome", "version": "120.0"},
            {"name": "Firefox", "version": "121.0"},
            {"name": "Safari", "version": "17.0"},
            {"name": "Edge", "version": "120.0"}
        ],
        "screen_sizes": [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 768, "height": 1024},
            {"width": 375, "height": 667}
        ],
        "features": [
            "WebGL",
            "WebWorkers",
            "WebSocket",
            "LocalStorage",
            "IndexedDB"
        ]
    }


# Mobile/responsive test data
@pytest.fixture
def mobile_test_data():
    """Data for mobile/responsive testing."""
    return {
        "devices": [
            {"name": "iPhone 14", "width": 390, "height": 844},
            {"name": "Samsung Galaxy S23", "width": 360, "height": 780},
            {"name": "iPad", "width": 768, "height": 1024},
            {"name": "Android Tablet", "width": 1024, "height": 768}
        ],
        "orientations": ["portrait", "landscape"],
        "touch_gestures": [
            "tap",
            "double_tap",
            "long_press",
            "swipe",
            "pinch_zoom"
        ]
    }
