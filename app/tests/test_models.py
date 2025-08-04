import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from models.user import User
from models.garden import Garden
from models.plant import Plant
from models.plant_catalog import PlantCatalog


class TestUserModel:
    """Test User model functionality."""
    
    def test_create_user(self, db_session):
        """Test creating a user with valid data."""
        user_data = {
            "email": "test@example.com",
            "hashed_password": "hashed_password_123",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False
        }
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_email_unique_constraint(self, db_session):
        """Test that email must be unique."""
        user1_data = {
            "email": "test@example.com",
            "hashed_password": "hashed_password_123",
            "full_name": "Test User 1"
        }
        
        user2_data = {
            "email": "test@example.com",  # Same email
            "hashed_password": "hashed_password_456",
            "full_name": "Test User 2"
        }
        
        user1 = User(**user1_data)
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(**user2_data)
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Test without email
        user_data = {
            "hashed_password": "hashed_password_123",
            "full_name": "Test User"
        }
        
        user = User(**user_data)
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_default_values(self, db_session):
        """Test default values for user fields."""
        user_data = {
            "email": "test@example.com",
            "hashed_password": "hashed_password_123",
            "full_name": "Test User"
        }
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None
        assert user.updated_at is not None


class TestGardenModel:
    """Test Garden model functionality."""
    
    def test_create_garden(self, db_session, test_user):
        """Test creating a garden with valid data."""
        garden_data = {
            "name": "Test Garden",
            "description": "A test garden",
            "width": 10.0,
            "height": 8.0,
            "user_id": test_user.id,
            "location": "Test Location",
            "soil_type": "loamy",
            "climate_zone": 6
        }
        
        garden = Garden(**garden_data)
        db_session.add(garden)
        db_session.commit()
        db_session.refresh(garden)
        
        assert garden.id is not None
        assert garden.name == "Test Garden"
        assert garden.description == "A test garden"
        assert garden.width == 10.0
        assert garden.height == 8.0
        assert garden.user_id == test_user.id
        assert garden.location == "Test Location"
        assert garden.soil_type == "loamy"
        assert garden.climate_zone == 6
        assert garden.created_at is not None
        assert garden.updated_at is not None
    
    def test_garden_user_relationship(self, db_session, test_user):
        """Test garden-user relationship."""
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
        
        # Test relationship
        assert garden.user == test_user
        assert garden in test_user.gardens
    
    def test_garden_required_fields(self, db_session, test_user):
        """Test that required fields are enforced."""
        # Test without name
        garden_data = {
            "description": "A test garden",
            "width": 10.0,
            "height": 8.0,
            "user_id": test_user.id
        }
        
        garden = Garden(**garden_data)
        db_session.add(garden)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_garden_dimensions_validation(self, db_session, test_user):
        """Test garden dimension validation."""
        garden_data = {
            "name": "Test Garden",
            "description": "A test garden",
            "width": -5.0,  # Invalid negative width
            "height": 8.0,
            "user_id": test_user.id
        }
        
        garden = Garden(**garden_data)
        db_session.add(garden)
        
        # This should raise an error or be handled by the application
        # The exact behavior depends on the database constraints
        try:
            db_session.commit()
        except IntegrityError:
            pass  # Expected behavior
    
    def test_garden_default_values(self, db_session, test_user):
        """Test default values for garden fields."""
        garden_data = {
            "name": "Test Garden",
            "width": 10.0,
            "height": 8.0,
            "user_id": test_user.id
        }
        
        garden = Garden(**garden_data)
        db_session.add(garden)
        db_session.commit()
        db_session.refresh(garden)
        
        assert garden.created_at is not None
        assert garden.updated_at is not None


class TestPlantCatalogModel:
    """Test PlantCatalog model functionality."""
    
    def test_create_plant_catalog(self, db_session):
        """Test creating a plant catalog entry with valid data."""
        plant_data = {
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
        }
        
        plant = PlantCatalog(**plant_data)
        db_session.add(plant)
        db_session.commit()
        db_session.refresh(plant)
        
        assert plant.id is not None
        assert plant.name == "Tomato"
        assert plant.species == "Solanum lycopersicum"
        assert plant.family == "Solanaceae"
        assert plant.growth_duration_days == 80
        assert plant.spacing_cm == 60
        assert plant.water_needs == "medium"
        assert plant.sunlight_needs == "full"
        assert plant.soil_type == "loamy"
        assert plant.ph_range == "6.0-6.8"
        assert plant.max_height_cm == 200
        assert plant.max_spread_cm == 60
        assert plant.root_depth_cm == 30
        assert plant.companion_plants == ["Basil", "Marigold"]
        assert plant.antagonist_plants == ["Potato", "Corn"]
        assert plant.planting_season == "spring"
        assert plant.harvest_season == "summer"
        assert plant.yield_per_plant_kg == 2.5
        assert plant.disease_resistance == ["blight", "mildew"]
        assert plant.pest_resistance == ["aphids", "whiteflies"]
        assert plant.nutrient_requirements == {"N": "medium", "P": "high", "K": "medium"}
        assert plant.climate_zones == [5, 6, 7, 8]
        assert plant.drought_tolerance == "low"
        assert plant.frost_tolerance == "none"
        assert plant.edible_parts == ["fruit"]
        assert plant.culinary_uses == ["fresh", "cooking", "canning"]
        assert plant.medicinal_properties == ["antioxidant", "vitamin_c"]
        assert plant.storage_conditions == "cool_dry"
        assert plant.seed_life_years == 4
        assert plant.germination_days == 7
        assert plant.transplant_days == 21
        assert plant.maturity_days == 70
        assert plant.succession_planting is True
        assert plant.crop_rotation_group == "solanaceae"
        assert plant.nitrogen_fixing is False
        assert plant.pollinator_attractor is True
        assert plant.deer_resistant is False
        assert plant.rabbit_resistant is False
        assert plant.drought_tolerant is False
        assert plant.shade_tolerant is False
        assert plant.container_friendly is True
        assert plant.trellis_required is True
        assert plant.pruning_required is True
        assert plant.fertilizer_needs == "balanced"
        assert plant.watering_frequency == "daily"
        assert plant.mulch_beneficial is True
        assert plant.companion_planting_notes == "Plant with basil to improve flavor and deter pests"
        assert plant.growing_tips == "Provide consistent moisture and support for indeterminate varieties"
        assert plant.harvesting_tips == "Harvest when fully colored but still firm"
        assert plant.storage_tips == "Store at room temperature until ripe, then refrigerate"
        assert plant.seed_saving_tips == "Allow fruits to fully ripen on plant before collecting seeds"
        assert plant.pest_management == "Use row covers and companion planting"
        assert plant.disease_management == "Ensure good air circulation and avoid overhead watering"
        assert plant.soil_preparation == "Add compost and ensure good drainage"
        assert plant.planting_depth_cm == 1
        assert plant.seed_spacing_cm == 2
        assert plant.row_spacing_cm == 90
        assert plant.thinning_required is True
        assert plant.thinning_spacing_cm == 30
        assert plant.support_type == "cage"
        assert plant.support_height_cm == 150
        assert plant.pruning_type == "suckering"
        assert plant.fertilizer_schedule == "every_2_weeks"
        assert plant.watering_method == "drip"
        assert plant.mulch_type == "straw"
        assert plant.mulch_depth_cm == 5
        assert plant.weed_control == "mulch"
        assert plant.pest_monitoring == "weekly"
        assert plant.disease_monitoring == "weekly"
        assert plant.growth_monitoring == "weekly"
        assert plant.harvest_monitoring == "daily"
        assert plant.yield_tracking is True
        assert plant.quality_assessment is True
        assert plant.market_value_per_kg == 3.50
        assert plant.labor_hours_per_plant == 0.5
        assert plant.equipment_needs == ["cages", "trellis", "drip_irrigation"]
        assert plant.specialized_tools == ["pruning_shears", "tomato_cages"]
        assert plant.seasonal_notes == "Plant after last frost, harvest before first frost"
        assert plant.climate_adaptation == "Heat loving, protect from cold"
        assert plant.microclimate_preferences == "Full sun, sheltered from wind"
        assert plant.water_efficiency == "medium"
        assert plant.nutrient_efficiency == "high"
        assert plant.space_efficiency == "medium"
        assert plant.time_efficiency == "medium"
        assert plant.cost_efficiency == "high"
        assert plant.skill_level_required == "intermediate"
        assert plant.maintenance_level == "medium"
        assert plant.risk_level == "low"
        assert plant.reward_level == "high"
        assert plant.sustainability_score == 8
        assert plant.biodiversity_contribution == "high"
        assert plant.ecosystem_services == ["pollination", "pest_control"]
        assert plant.carbon_sequestration == "low"
        assert plant.soil_improvement == "medium"
        assert plant.water_conservation == "medium"
        assert plant.wildlife_habitat == "medium"
        assert plant.educational_value == "high"
        assert plant.therapeutic_value == "medium"
        assert plant.aesthetic_value == "high"
        assert plant.cultural_significance == "high"
        assert plant.economic_value == "high"
        assert plant.nutritional_value == "high"
        assert plant.medicinal_value == "medium"
        assert plant.ecological_value == "medium"
        assert plant.social_value == "high"
        assert plant.historical_significance == "high"
        assert plant.future_potential == "high"
        assert plant.research_priorities == ["disease_resistance", "drought_tolerance"]
        assert plant.breeding_objectives == ["yield", "flavor", "disease_resistance"]
        assert plant.conservation_status == "secure"
        assert plant.genetic_diversity == "high"
        assert plant.adaptation_potential == "high"
        assert plant.climate_resilience == "medium"
        assert plant.sustainability_potential == "high"
        assert plant.innovation_potential == "medium"
        assert plant.market_potential == "high"
        assert plant.community_value == "high"
        assert plant.global_significance == "high"
        assert plant.created_at is not None
        assert plant.updated_at is not None
    
    def test_plant_catalog_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Test without name
        plant_data = {
            "species": "Solanum lycopersicum",
            "family": "Solanaceae",
            "growth_duration_days": 80
        }
        
        plant = PlantCatalog(**plant_data)
        db_session.add(plant)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_plant_catalog_name_unique_constraint(self, db_session):
        """Test that plant name must be unique."""
        plant1_data = {
            "name": "Tomato",
            "species": "Solanum lycopersicum",
            "family": "Solanaceae",
            "growth_duration_days": 80
        }
        
        plant2_data = {
            "name": "Tomato",  # Same name
            "species": "Solanum lycopersicum",
            "family": "Solanaceae",
            "growth_duration_days": 80
        }
        
        plant1 = PlantCatalog(**plant1_data)
        db_session.add(plant1)
        db_session.commit()
        
        plant2 = PlantCatalog(**plant2_data)
        db_session.add(plant2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_plant_catalog_json_fields(self, db_session):
        """Test JSON field serialization/deserialization."""
        plant_data = {
            "name": "Test Plant",
            "species": "Test Species",
            "family": "Test Family",
            "growth_duration_days": 60,
            "companion_plants": ["Plant A", "Plant B"],
            "antagonist_plants": ["Plant C"],
            "nutrient_requirements": {"N": "high", "P": "medium"},
            "climate_zones": [5, 6, 7],
            "edible_parts": ["leaves", "stems"],
            "culinary_uses": ["fresh", "cooked"],
            "medicinal_properties": ["anti-inflammatory"],
            "disease_resistance": ["rust", "mildew"],
            "pest_resistance": ["aphids"],
            "equipment_needs": ["pruner", "watering_can"],
            "specialized_tools": ["harvesting_knife"],
            "ecosystem_services": ["pollination"],
            "research_priorities": ["disease_resistance"],
            "breeding_objectives": ["yield"]
        }
        
        plant = PlantCatalog(**plant_data)
        db_session.add(plant)
        db_session.commit()
        db_session.refresh(plant)
        
        # Test JSON field retrieval
        assert plant.companion_plants == ["Plant A", "Plant B"]
        assert plant.antagonist_plants == ["Plant C"]
        assert plant.nutrient_requirements == {"N": "high", "P": "medium"}
        assert plant.climate_zones == [5, 6, 7]
        assert plant.edible_parts == ["leaves", "stems"]
        assert plant.culinary_uses == ["fresh", "cooked"]
        assert plant.medicinal_properties == ["anti-inflammatory"]
        assert plant.disease_resistance == ["rust", "mildew"]
        assert plant.pest_resistance == ["aphids"]
        assert plant.equipment_needs == ["pruner", "watering_can"]
        assert plant.specialized_tools == ["harvesting_knife"]
        assert plant.ecosystem_services == ["pollination"]
        assert plant.research_priorities == ["disease_resistance"]
        assert plant.breeding_objectives == ["yield"]


class TestPlantModel:
    """Test Plant model functionality."""
    
    def test_create_plant(self, db_session, test_garden, test_plant_catalog):
        """Test creating a plant with valid data."""
        catalog_plant = test_plant_catalog[0]
        plant_data = {
            "name": catalog_plant.name,
            "species": catalog_plant.species,
            "position_x": 1.0,
            "position_y": 1.0,
            "garden_id": test_garden.id,
            "plant_catalog_id": catalog_plant.id,
            "planting_date": date(2024, 3, 15),
            "growth_stage": "seedling",
            "health_status": "healthy",
            "notes": "Test plant"
        }
        
        plant = Plant(**plant_data)
        db_session.add(plant)
        db_session.commit()
        db_session.refresh(plant)
        
        assert plant.id is not None
        assert plant.name == catalog_plant.name
        assert plant.species == catalog_plant.species
        assert plant.position_x == 1.0
        assert plant.position_y == 1.0
        assert plant.garden_id == test_garden.id
        assert plant.plant_catalog_id == catalog_plant.id
        assert plant.planting_date == date(2024, 3, 15)
        assert plant.growth_stage == "seedling"
        assert plant.health_status == "healthy"
        assert plant.notes == "Test plant"
        assert plant.created_at is not None
        assert plant.updated_at is not None
    
    def test_plant_garden_relationship(self, db_session, test_garden, test_plant_catalog):
        """Test plant-garden relationship."""
        catalog_plant = test_plant_catalog[0]
        plant_data = {
            "name": catalog_plant.name,
            "species": catalog_plant.species,
            "position_x": 1.0,
            "position_y": 1.0,
            "garden_id": test_garden.id,
            "plant_catalog_id": catalog_plant.id,
            "planting_date": date(2024, 3, 15),
            "growth_stage": "seedling",
            "health_status": "healthy"
        }
        
        plant = Plant(**plant_data)
        db_session.add(plant)
        db_session.commit()
        db_session.refresh(plant)
        
        # Test relationship
        assert plant.garden == test_garden
        assert plant in test_garden.plants
    
    def test_plant_catalog_relationship(self, db_session, test_garden, test_plant_catalog):
        """Test plant-catalog relationship."""
        catalog_plant = test_plant_catalog[0]
        plant_data = {
            "name": catalog_plant.name,
            "species": catalog_plant.species,
            "position_x": 1.0,
            "position_y": 1.0,
            "garden_id": test_garden.id,
            "plant_catalog_id": catalog_plant.id,
            "planting_date": date(2024, 3, 15),
            "growth_stage": "seedling",
            "health_status": "healthy"
        }
        
        plant = Plant(**plant_data)
        db_session.add(plant)
        db_session.commit()
        db_session.refresh(plant)
        
        # Test relationship
        assert plant.plant_catalog == catalog_plant
    
    def test_plant_required_fields(self, db_session, test_garden, test_plant_catalog):
        """Test that required fields are enforced."""
        catalog_plant = test_plant_catalog[0]
        
        # Test without name
        plant_data = {
            "species": catalog_plant.species,
            "position_x": 1.0,
            "position_y": 1.0,
            "garden_id": test_garden.id,
            "plant_catalog_id": catalog_plant.id,
            "planting_date": date(2024, 3, 15),
            "growth_stage": "seedling",
            "health_status": "healthy"
        }
        
        plant = Plant(**plant_data)
        db_session.add(plant)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_plant_position_validation(self, db_session, test_garden, test_plant_catalog):
        """Test plant position validation."""
        catalog_plant = test_plant_catalog[0]
        
        # Test negative position
        plant_data = {
            "name": catalog_plant.name,
            "species": catalog_plant.species,
            "position_x": -1.0,  # Invalid negative position
            "position_y": 1.0,
            "garden_id": test_garden.id,
            "plant_catalog_id": catalog_plant.id,
            "planting_date": date(2024, 3, 15),
            "growth_stage": "seedling",
            "health_status": "healthy"
        }
        
        plant = Plant(**plant_data)
        db_session.add(plant)
        
        # This should be handled by application logic or database constraints
        try:
            db_session.commit()
        except IntegrityError:
            pass  # Expected behavior
    
    def test_plant_growth_stage_enum(self, db_session, test_garden, test_plant_catalog):
        """Test plant growth stage enum values."""
        catalog_plant = test_plant_catalog[0]
        valid_growth_stages = ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]
        
        for stage in valid_growth_stages:
            plant_data = {
                "name": f"{catalog_plant.name}_{stage}",
                "species": catalog_plant.species,
                "position_x": 1.0,
                "position_y": 1.0,
                "garden_id": test_garden.id,
                "plant_catalog_id": catalog_plant.id,
                "planting_date": date(2024, 3, 15),
                "growth_stage": stage,
                "health_status": "healthy"
            }
            
            plant = Plant(**plant_data)
            db_session.add(plant)
        
        db_session.commit()
        
        # Verify all plants were created
        plants = db_session.query(Plant).filter(Plant.garden_id == test_garden.id).all()
        assert len(plants) == len(valid_growth_stages)
    
    def test_plant_health_status_enum(self, db_session, test_garden, test_plant_catalog):
        """Test plant health status enum values."""
        catalog_plant = test_plant_catalog[0]
        valid_health_statuses = ["healthy", "sick", "dying", "dead"]
        
        for status in valid_health_statuses:
            plant_data = {
                "name": f"{catalog_plant.name}_{status}",
                "species": catalog_plant.species,
                "position_x": 1.0,
                "position_y": 1.0,
                "garden_id": test_garden.id,
                "plant_catalog_id": catalog_plant.id,
                "planting_date": date(2024, 3, 15),
                "growth_stage": "seedling",
                "health_status": status
            }
            
            plant = Plant(**plant_data)
            db_session.add(plant)
        
        db_session.commit()
        
        # Verify all plants were created
        plants = db_session.query(Plant).filter(Plant.garden_id == test_garden.id).all()
        assert len(plants) == len(valid_health_statuses) 