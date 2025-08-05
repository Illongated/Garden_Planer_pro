import pytest
import asyncio
from datetime import datetime
from app.services.agronomic_engine import (
    AgronomicEngine, PlantSpecs, GardenZone, PlantPlacement,
    PlantType, WaterNeed, SunExposure, GrowthStage
)

@pytest.fixture
def sample_plant_specs():
    return PlantSpecs(
        name="Tomato",
        type=PlantType.VEGETABLE,
        spacing_min=30.0,
        spacing_optimal=45.0,
        water_need=WaterNeed.MEDIUM,
        sun_exposure=SunExposure.FULL_SUN,
        growth_days=80,
        height_max=120.0,
        width_max=60.0,
        root_depth=45.0,
        yield_per_plant=2.5,
        companion_plants=["Basil", "Marigold"],
        incompatible_plants=["Potato", "Corn"],
        water_consumption_daily=2.0,
        nutrient_requirements={"N": 0.15, "P": 0.10, "K": 0.20},
        frost_tolerance=False,
        heat_tolerance=True
    )

@pytest.fixture
def sample_garden_zone():
    return GardenZone(
        id="zone_1",
        name="Main Garden",
        area=100.0,
        soil_type="loamy",
        ph_level=6.5,
        sun_exposure=SunExposure.FULL_SUN,
        water_availability=50.0,
        elevation=100.0,
        slope=5.0,
        coordinates=(0.0, 0.0)
    )

@pytest.fixture
def sample_plant_placement(sample_plant_specs):
    return PlantPlacement(
        plant_id="tomato_1",
        plant_specs=sample_plant_specs,
        x=0.0,
        y=0.0,
        planted_date=datetime.now(),
        current_stage=GrowthStage.SEEDLING,
        health_score=1.0,
        water_stress=0.0,
        nutrient_stress=0.0
    )

@pytest.fixture
def agronomic_engine():
    return AgronomicEngine()

class TestAgronomicCalculator:
    """Test the core agronomic calculation engine"""

    def test_calculate_optimal_spacing(self, agronomic_engine, sample_plant_specs):
        """Test optimal spacing calculation with different soil qualities"""
        # Test with good soil quality
        spacing_good = agronomic_engine.calculator.calculate_optimal_spacing(sample_plant_specs, 0.8)
        assert spacing_good > sample_plant_specs.spacing_min
        assert spacing_good <= sample_plant_specs.spacing_optimal * 1.2

        # Test with poor soil quality
        spacing_poor = agronomic_engine.calculator.calculate_optimal_spacing(sample_plant_specs, 0.3)
        assert spacing_poor >= sample_plant_specs.spacing_min
        assert spacing_poor > spacing_good  # Poor soil should require more spacing

        # Test minimum spacing enforcement
        spacing_min = agronomic_engine.calculator.calculate_optimal_spacing(sample_plant_specs, 0.0)
        assert spacing_min >= sample_plant_specs.spacing_min

    def test_calculate_water_needs(self, agronomic_engine, sample_plant_specs):
        """Test water needs calculation with different conditions"""
        weather_data = {"et0": 5.0}

        # Test different growth stages
        water_seed = agronomic_engine.calculator.calculate_water_needs(
            sample_plant_specs, weather_data, 0.5, GrowthStage.SEED
        )
        water_vegetative = agronomic_engine.calculator.calculate_water_needs(
            sample_plant_specs, weather_data, 0.5, GrowthStage.VEGETATIVE
        )
        assert water_vegetative > water_seed  # Vegetative stage needs more water

        # Test different water need levels with same width
        high_water_plant = PlantSpecs(
            name="Rice",
            type=PlantType.VEGETABLE,
            spacing_min=20.0,
            spacing_optimal=30.0,
            water_need=WaterNeed.HIGH,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=120,
            height_max=100.0,
            width_max=60.0,  # << même largeur que tomato pour un vrai test besoin eau
            root_depth=30.0,
            yield_per_plant=1.0
        )
        water_high = agronomic_engine.calculator.calculate_water_needs(
            high_water_plant, weather_data, 0.5, GrowthStage.VEGETATIVE
        )
        water_medium = agronomic_engine.calculator.calculate_water_needs(
            sample_plant_specs, weather_data, 0.5, GrowthStage.VEGETATIVE
        )
        assert water_high > water_medium  # High water need plants need more water

    def test_calculate_solar_exposure(self, agronomic_engine, sample_plant_placement, sample_garden_zone):
        """Test solar exposure calculation"""
        sun_data = {"seasonal_factor": 1.0}
        # Place le plant dans la zone testée pour garantir la logique
        plant_in_sun = PlantPlacement(
            plant_id="tomato_1",
            plant_specs=sample_plant_placement.plant_specs,
            x=0.0, y=0.0,
            planted_date=datetime.now(),
            current_stage=GrowthStage.SEEDLING,
            health_score=1.0,
            water_stress=0.0,
            nutrient_stress=0.0
        )
        exposure = agronomic_engine.calculator.calculate_solar_exposure(
            plant_in_sun, [sample_garden_zone], sun_data
        )
        assert 0.0 <= exposure <= 1.0  # Exposure should be normalized

        # Test different sun exposures, plant placé au centre de la shade zone
        shade_zone = GardenZone(
            id="shade_zone",
            name="Shade Garden",
            area=50.0,
            soil_type="loamy",
            ph_level=6.5,
            sun_exposure=SunExposure.SHADE,
            water_availability=30.0,
            elevation=100.0,
            slope=0.0,
            coordinates=(10.0, 10.0)
        )
        plant_in_shade = PlantPlacement(
            plant_id="tomato_1",
            plant_specs=sample_plant_placement.plant_specs,
            x=10.0, y=10.0,
            planted_date=datetime.now(),
            current_stage=GrowthStage.SEEDLING,
            health_score=1.0,
            water_stress=0.0,
            nutrient_stress=0.0
        )
        shade_exposure = agronomic_engine.calculator.calculate_solar_exposure(
            plant_in_shade, [shade_zone], sun_data
        )
        assert shade_exposure < exposure  # Shade should have lower exposure

    def test_calculate_growth_prediction(self, agronomic_engine, sample_plant_specs, sample_plant_placement):
        """Test growth prediction calculation"""
        environmental_factors = {
            "temperature_stress": 0.1,
            "humidity_stress": 0.2
        }
        prediction = agronomic_engine.calculator.calculate_growth_prediction(
            sample_plant_specs, sample_plant_placement, environmental_factors
        )
        assert "growth_modifier" in prediction
        assert "predicted_yield" in prediction
        assert "current_progress" in prediction
        assert "days_to_harvest" in prediction
        assert "health_score" in prediction
        assert "stress_factors" in prediction

        # Test stress impact
        high_stress_placement = PlantPlacement(
            plant_id="stressed_plant",
            plant_specs=sample_plant_specs,
            x=10.0,
            y=10.0,
            planted_date=datetime.now(),
            current_stage=GrowthStage.SEEDLING,
            health_score=0.5,
            water_stress=0.8,
            nutrient_stress=0.7
        )
        stressed_prediction = agronomic_engine.calculator.calculate_growth_prediction(
            sample_plant_specs, high_stress_placement, environmental_factors
        )
        assert stressed_prediction["predicted_yield"] < prediction["predicted_yield"]
        assert stressed_prediction["growth_modifier"] < prediction["growth_modifier"]

class TestPlacementOptimizer:
    """Test the placement optimization algorithms"""

    @pytest.mark.asyncio
    async def test_optimize_placement_genetic(self, agronomic_engine, sample_plant_specs, sample_garden_zone):
        """Test genetic algorithm optimization"""
        # Test now with 2 plants to ensure crossover triggers
        plants = [sample_plant_specs, sample_plant_specs]
        zones = [sample_garden_zone]
        constraints = {"min_spacing": 0.3}
        optimized_placements = await agronomic_engine.optimizer.optimize_placement_genetic(
            plants, zones, constraints
        )
        assert len(optimized_placements) == len(plants)
        # Check that all placements are within valid zones
        for placement in optimized_placements:
            in_valid_zone = any(
                agronomic_engine.calculator._is_in_zone(placement, zone)
                for zone in zones
            )
            assert in_valid_zone

    @pytest.mark.asyncio
    async def test_fitness_calculation(self, agronomic_engine, sample_garden_zone):
        """Test fitness calculation for optimization"""
        # Create test placements
        plant_specs1 = PlantSpecs(
            name="Plant1",
            type=PlantType.VEGETABLE,
            spacing_min=30.0,
            spacing_optimal=45.0,
            water_need=WaterNeed.MEDIUM,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=80,
            height_max=60.0,
            width_max=30.0,
            root_depth=30.0,
            yield_per_plant=1.0
        )
        plant_specs2 = PlantSpecs(
            name="Plant2",
            type=PlantType.VEGETABLE,
            spacing_min=25.0,
            spacing_optimal=40.0,
            water_need=WaterNeed.LOW,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=70,
            height_max=50.0,
            width_max=25.0,
            root_depth=25.0,
            yield_per_plant=0.8
        )
        # Good placement (well spaced)
        good_placements = [
            PlantPlacement(
                plant_id="plant1",
                plant_specs=plant_specs1,
                x=0.0,
                y=0.0,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEED
            ),
            PlantPlacement(
                plant_id="plant2",
                plant_specs=plant_specs2,
                x=1.0,
                y=1.0,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEED
            )
        ]
        # Bad placement (too close)
        bad_placements = [
            PlantPlacement(
                plant_id="plant1",
                plant_specs=plant_specs1,
                x=0.0,
                y=0.0,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEED
            ),
            PlantPlacement(
                plant_id="plant2",
                plant_specs=plant_specs2,
                x=0.1,
                y=0.1,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEED
            )
        ]
        good_fitness = await agronomic_engine.optimizer._calculate_fitness(
            good_placements, [sample_garden_zone], {}
        )
        bad_fitness = await agronomic_engine.optimizer._calculate_fitness(
            bad_placements, [sample_garden_zone], {}
        )
        assert good_fitness > bad_fitness  # Good placement should have higher fitness

class TestIrrigationPlanner:
    """Test irrigation zone planning"""

    @pytest.mark.asyncio
    async def test_calculate_irrigation_zones(self, agronomic_engine, sample_garden_zone):
        """Test irrigation zone calculation"""
        # Create plants with different water needs, **même largeur**
        low_water_plant = PlantSpecs(
            name="Cactus",
            type=PlantType.VEGETABLE,
            spacing_min=20.0,
            spacing_optimal=30.0,
            water_need=WaterNeed.LOW,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=60,
            height_max=30.0,
            width_max=50.0,
            root_depth=20.0,
            yield_per_plant=0.5
        )
        high_water_plant = PlantSpecs(
            name="Rice",
            type=PlantType.VEGETABLE,
            spacing_min=25.0,
            spacing_optimal=35.0,
            water_need=WaterNeed.HIGH,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=120,
            height_max=100.0,
            width_max=50.0,
            root_depth=40.0,
            yield_per_plant=2.0
        )
        placements = [
            PlantPlacement(
                plant_id="cactus_1",
                plant_specs=low_water_plant,
                x=0.0,
                y=0.0,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEEDLING
            ),
            PlantPlacement(
                plant_id="rice_1",
                plant_specs=high_water_plant,
                x=10.0,
                y=10.0,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEEDLING
            )
        ]
        water_constraints = {"weather": {"et0": 5.0}}
        irrigation_analysis = await agronomic_engine.irrigation_planner.calculate_irrigation_zones(
            placements, [sample_garden_zone], water_constraints
        )
        assert "zones" in irrigation_analysis
        assert "total_water_needs" in irrigation_analysis
        assert "efficiency_score" in irrigation_analysis
        # Should have separate zones for different water needs
        assert len(irrigation_analysis["zones"]) >= 2
        # High water plants should need more water
        if "high" in irrigation_analysis["total_water_needs"] and "low" in irrigation_analysis["total_water_needs"]:
            assert irrigation_analysis["total_water_needs"]["high"] > irrigation_analysis["total_water_needs"]["low"]

class TestConflictDetector:
    """Test conflict detection algorithms"""

    @pytest.mark.asyncio
    async def test_detect_conflicts(self, agronomic_engine, sample_garden_zone):
        """Test conflict detection"""
        # Create incompatible plants
        plant_specs1 = PlantSpecs(
            name="Tomato",
            type=PlantType.VEGETABLE,
            spacing_min=30.0,
            spacing_optimal=45.0,
            water_need=WaterNeed.MEDIUM,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=80,
            height_max=60.0,
            width_max=30.0,
            root_depth=30.0,
            yield_per_plant=1.0,
            incompatible_plants=["Potato"]
        )
        plant_specs2 = PlantSpecs(
            name="Potato",
            type=PlantType.VEGETABLE,
            spacing_min=25.0,
            spacing_optimal=40.0,
            water_need=WaterNeed.MEDIUM,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=90,
            height_max=50.0,
            width_max=25.0,
            root_depth=25.0,
            yield_per_plant=0.8,
            incompatible_plants=["Tomato"]
        )
        # Place incompatible plants close together
        placements = [
            PlantPlacement(
                plant_id="tomato_1",
                plant_specs=plant_specs1,
                x=0.0,
                y=0.0,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEEDLING
            ),
            PlantPlacement(
                plant_id="potato_1",
                plant_specs=plant_specs2,
                x=0.5,
                y=0.5,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEEDLING
            )
        ]
        conflicts = await agronomic_engine.conflict_detector.detect_conflicts(
            placements, [sample_garden_zone]
        )
        assert "compatibility_violations" in conflicts
        assert len(conflicts["compatibility_violations"]) > 0

        # Test spacing violations
        plant_specs3 = PlantSpecs(
            name="Lettuce",
            type=PlantType.VEGETABLE,
            spacing_min=20.0,
            spacing_optimal=30.0,
            water_need=WaterNeed.MEDIUM,
            sun_exposure=SunExposure.PARTIAL_SUN,
            growth_days=45,
            height_max=20.0,
            width_max=15.0,
            root_depth=15.0,
            yield_per_plant=0.3
        )
        # Place plants too close together
        close_placements = [
            PlantPlacement(
                plant_id="lettuce_1",
                plant_specs=plant_specs3,
                x=0.0,
                y=0.0,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEEDLING
            ),
            PlantPlacement(
                plant_id="lettuce_2",
                plant_specs=plant_specs3,
                x=0.1,
                y=0.1,
                planted_date=datetime.now(),
                current_stage=GrowthStage.SEEDLING
            )
        ]
        spacing_conflicts = await agronomic_engine.conflict_detector.detect_conflicts(
            close_placements, [sample_garden_zone]
        )
        assert "spacing_violations" in spacing_conflicts
        assert len(spacing_conflicts["spacing_violations"]) > 0

class TestAgronomicEngine:
    """Test the main agronomic engine integration"""

    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, agronomic_engine, sample_plant_placement, sample_garden_zone):
        """Test comprehensive agronomic analysis"""
        environmental_data = {
            "weather": {"et0": 5.0, "temperature": 25.0},
            "sun_data": {"seasonal_factor": 1.0},
            "soil_moisture": 0.6,
            "temperature_stress": 0.1,
            "humidity_stress": 0.2
        }
        analysis = await agronomic_engine.calculate_comprehensive_analysis(
            [sample_plant_placement], [sample_garden_zone], environmental_data
        )
        assert "water_analysis" in analysis
        assert "solar_analysis" in analysis
        assert "growth_predictions" in analysis
        assert "conflicts" in analysis
        assert "total_predicted_yield" in analysis
        assert "efficiency_metrics" in analysis
        assert "timestamp" in analysis
        # Check that all required keys exist
        assert sample_plant_placement.plant_id in analysis["solar_analysis"]
        assert sample_plant_placement.plant_id in analysis["growth_predictions"]
        assert analysis["total_predicted_yield"] >= 0

    @pytest.mark.asyncio
    async def test_incremental_update(self, agronomic_engine, sample_plant_placement, sample_garden_zone):
        """Test incremental calculation updates"""
        environmental_data = {
            "weather": {"et0": 5.0},
            "sun_data": {"seasonal_factor": 1.0},
            "soil_moisture": 0.6
        }
        new_placement = PlantPlacement(
            plant_id="new_plant",
            plant_specs=sample_plant_placement.plant_specs,
            x=20.0,
            y=20.0,
            planted_date=datetime.now(),
            current_stage=GrowthStage.SEED
        )
        incremental_result = await agronomic_engine.calculate_incremental_update(
            [sample_plant_placement], new_placement, [sample_garden_zone], environmental_data
        )
        assert "new_plant_analysis" in incremental_result
        assert "conflicts_with_new_plant" in incremental_result
        assert "updated_irrigation_zones" in incremental_result
        # Check that new plant analysis contains required fields
        new_analysis = incremental_result["new_plant_analysis"]
        assert "water_need" in new_analysis
        assert "solar_exposure" in new_analysis
        assert "growth_prediction" in new_analysis

class TestScientificValidation:
    """Test scientific validity of algorithms"""

    def test_water_calculation_scientific_basis(self, agronomic_engine):
        """Test that water calculations follow scientific principles"""
        plant_specs = PlantSpecs(
            name="Test Plant",
            type=PlantType.VEGETABLE,
            spacing_min=30.0,
            spacing_optimal=45.0,
            water_need=WaterNeed.MEDIUM,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=80,
            height_max=60.0,
            width_max=30.0,
            root_depth=30.0,
            yield_per_plant=1.0
        )
        weather_data = {"et0": 5.0}
        # Test that water needs increase with growth stage (scientific principle)
        water_seed = agronomic_engine.calculator.calculate_water_needs(
            plant_specs, weather_data, 0.5, GrowthStage.SEED
        )
        water_vegetative = agronomic_engine.calculator.calculate_water_needs(
            plant_specs, weather_data, 0.5, GrowthStage.VEGETATIVE
        )
        water_fruiting = agronomic_engine.calculator.calculate_water_needs(
            plant_specs, weather_data, 0.5, GrowthStage.FRUITING
        )
        assert water_seed < water_vegetative < water_fruiting  # Water needs should increase with growth

    def test_spacing_calculation_scientific_basis(self, agronomic_engine):
        """Test that spacing calculations follow agronomic principles"""
        plant_specs = PlantSpecs(
            name="Test Plant",
            type=PlantType.VEGETABLE,
            spacing_min=30.0,
            spacing_optimal=45.0,
            water_need=WaterNeed.MEDIUM,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=80,
            height_max=60.0,
            width_max=30.0,
            root_depth=30.0,
            yield_per_plant=1.0
        )
        # Test that better soil allows closer spacing (agronomic principle)
        spacing_poor_soil = agronomic_engine.calculator.calculate_optimal_spacing(plant_specs, 0.2)
        spacing_good_soil = agronomic_engine.calculator.calculate_optimal_spacing(plant_specs, 0.8)
        assert spacing_poor_soil > spacing_good_soil  # Poor soil requires more spacing
        # Test that minimum spacing is always respected
        spacing_min_test = agronomic_engine.calculator.calculate_optimal_spacing(plant_specs, 0.0)
        assert spacing_min_test >= plant_specs.spacing_min

    def test_growth_prediction_scientific_basis(self, agronomic_engine):
        """Test that growth predictions follow biological principles"""
        plant_specs = PlantSpecs(
            name="Test Plant",
            type=PlantType.VEGETABLE,
            spacing_min=30.0,
            spacing_optimal=45.0,
            water_need=WaterNeed.MEDIUM,
            sun_exposure=SunExposure.FULL_SUN,
            growth_days=80,
            height_max=60.0,
            width_max=30.0,
            root_depth=30.0,
            yield_per_plant=1.0
        )
        healthy_placement = PlantPlacement(
            plant_id="healthy",
            plant_specs=plant_specs,
            x=10.0,
            y=10.0,
            planted_date=datetime.now(),
            current_stage=GrowthStage.SEEDLING,
            health_score=1.0,
            water_stress=0.0,
            nutrient_stress=0.0
        )
        stressed_placement = PlantPlacement(
            plant_id="stressed",
            plant_specs=plant_specs,
            x=10.0,
            y=10.0,
            planted_date=datetime.now(),
            current_stage=GrowthStage.SEEDLING,
            health_score=0.5,
            water_stress=0.8,
            nutrient_stress=0.7
        )
        environmental_factors = {"temperature_stress": 0.0, "humidity_stress": 0.0}
        healthy_prediction = agronomic_engine.calculator.calculate_growth_prediction(
            plant_specs, healthy_placement, environmental_factors
        )
        stressed_prediction = agronomic_engine.calculator.calculate_growth_prediction(
            plant_specs, stressed_placement, environmental_factors
        )
        # Stressed plants should have lower yield and slower growth
        assert stressed_prediction["predicted_yield"] < healthy_prediction["predicted_yield"]
        assert stressed_prediction["growth_modifier"] < healthy_prediction["growth_modifier"]
        assert stressed_prediction["health_score"] < healthy_prediction["health_score"]

if __name__ == "__main__":
    pytest.main([__file__])
