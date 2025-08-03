import asyncio
import math
import random
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import json

from pydantic import BaseModel, Field, validator
from scipy.spatial.distance import cdist
from scipy.optimize import minimize
import networkx as nx

logger = logging.getLogger(__name__)

class PlantType(str, Enum):
    VEGETABLE = "vegetable"
    HERB = "herb"
    FRUIT = "fruit"
    FLOWER = "flower"
    ROOT = "root"
    LEGUME = "legume"

class GrowthStage(str, Enum):
    SEED = "seed"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    HARVEST = "harvest"

class WaterNeed(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SunExposure(str, Enum):
    FULL_SUN = "full_sun"
    PARTIAL_SUN = "partial_sun"
    SHADE = "shade"

@dataclass
class PlantSpecs:
    """Scientific plant specifications for agronomic calculations"""
    name: str
    type: PlantType
    spacing_min: float  # cm
    spacing_optimal: float  # cm
    water_need: WaterNeed
    sun_exposure: SunExposure
    growth_days: int
    height_max: float  # cm
    width_max: float  # cm
    root_depth: float  # cm
    yield_per_plant: float  # kg
    companion_plants: List[str] = field(default_factory=list)
    incompatible_plants: List[str] = field(default_factory=list)
    water_consumption_daily: float = 0.0  # liters per day
    nutrient_requirements: Dict[str, float] = field(default_factory=dict)
    frost_tolerance: bool = False
    heat_tolerance: bool = False

@dataclass
class GardenZone:
    """Represents a garden zone with environmental conditions"""
    id: str
    name: str
    area: float  # m²
    soil_type: str
    ph_level: float
    sun_exposure: SunExposure
    water_availability: float  # liters per day
    elevation: float  # meters
    slope: float  # degrees
    coordinates: Tuple[float, float] = (0.0, 0.0)

@dataclass
class PlantPlacement:
    """Represents a plant placement in the garden"""
    plant_id: str
    plant_specs: PlantSpecs
    x: float
    y: float
    planted_date: datetime
    current_stage: GrowthStage
    health_score: float = 1.0
    water_stress: float = 0.0
    nutrient_stress: float = 0.0

class AgronomicCalculator:
    """Core agronomic computation engine with scientific validation"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache = {}
        
    @lru_cache(maxsize=1000)
    def calculate_optimal_spacing(self, plant_specs: PlantSpecs, soil_quality: float) -> float:
        """
        Calculate optimal spacing based on plant specifications and soil quality.
        Uses scientific formulas for plant spacing optimization.
        """
        base_spacing = plant_specs.spacing_optimal
        
        # Adjust for soil quality (better soil = closer spacing)
        soil_factor = 0.8 + (soil_quality * 0.4)  # 0.8 to 1.2 range
        
        # Adjust for water availability
        water_factor = {
            WaterNeed.LOW: 1.0,
            WaterNeed.MEDIUM: 1.1,
            WaterNeed.HIGH: 1.2
        }.get(plant_specs.water_need, 1.0)
        
        # Adjust for sun exposure
        sun_factor = {
            SunExposure.FULL_SUN: 1.1,
            SunExposure.PARTIAL_SUN: 1.0,
            SunExposure.SHADE: 0.9
        }.get(plant_specs.sun_exposure, 1.0)
        
        optimal_spacing = base_spacing * soil_factor * water_factor * sun_factor
        
        # Ensure minimum spacing is maintained
        return max(optimal_spacing, plant_specs.spacing_min)
    
    def calculate_water_needs(self, plant_specs: PlantSpecs, weather_data: Dict, 
                            soil_moisture: float, growth_stage: GrowthStage) -> float:
        """
        Calculate daily water needs based on scientific evapotranspiration models.
        """
        # Base evapotranspiration (ET0) from weather data
        et0 = weather_data.get('et0', 5.0)  # mm/day
        
        # Crop coefficient based on growth stage
        kc_values = {
            GrowthStage.SEED: 0.3,
            GrowthStage.SEEDLING: 0.5,
            GrowthStage.VEGETATIVE: 0.8,
            GrowthStage.FLOWERING: 1.0,
            GrowthStage.FRUITING: 1.1,
            GrowthStage.HARVEST: 0.7
        }
        kc = kc_values.get(growth_stage, 0.8)
        
        # Water need multiplier based on plant type
        water_multiplier = {
            WaterNeed.LOW: 0.7,
            WaterNeed.MEDIUM: 1.0,
            WaterNeed.HIGH: 1.3
        }.get(plant_specs.water_need, 1.0)
        
        # Soil moisture stress factor
        stress_factor = max(0.5, min(1.5, soil_moisture / 0.3))
        
        # Calculate daily water need in liters
        daily_water = (et0 * kc * water_multiplier * stress_factor * 
                      plant_specs.width_max * plant_specs.width_max / 10000)
        
        return max(0.1, daily_water)
    
    def calculate_solar_exposure(self, plant_placement: PlantPlacement, 
                               garden_zones: List[GardenZone], 
                               sun_data: Dict) -> float:
        """
        Calculate solar exposure score based on position and environmental factors.
        """
        zone = next((z for z in garden_zones if self._is_in_zone(plant_placement, z)), None)
        if not zone:
            return 0.5
        
        # Base exposure from zone
        base_exposure = {
            SunExposure.FULL_SUN: 1.0,
            SunExposure.PARTIAL_SUN: 0.6,
            SunExposure.SHADE: 0.3
        }.get(zone.sun_exposure, 0.5)
        
        # Adjust for seasonal sun angle
        seasonal_factor = sun_data.get('seasonal_factor', 1.0)
        
        # Adjust for slope and orientation
        slope_factor = 1.0 + (zone.slope / 90.0) * 0.2
        
        # Calculate final exposure score
        exposure_score = base_exposure * seasonal_factor * slope_factor
        
        return min(1.0, max(0.0, exposure_score))
    
    def _is_in_zone(self, placement: PlantPlacement, zone: GardenZone) -> bool:
        """Check if plant placement is within a garden zone"""
        # Simplified distance calculation
        dx = placement.x - zone.coordinates[0]
        dy = placement.y - zone.coordinates[1]
        distance = math.sqrt(dx*dx + dy*dy)
        return distance <= math.sqrt(zone.area / math.pi)
    
    def calculate_growth_prediction(self, plant_specs: PlantSpecs, 
                                  placement: PlantPlacement,
                                  environmental_factors: Dict) -> Dict:
        """
        Predict growth timeline and yield based on environmental conditions.
        """
        # Calculate growth rate modifier based on conditions
        water_stress = placement.water_stress
        nutrient_stress = placement.nutrient_stress
        health_score = placement.health_score
        
        # Environmental stress factors
        temp_stress = environmental_factors.get('temperature_stress', 0.0)
        humidity_stress = environmental_factors.get('humidity_stress', 0.0)
        
        # Combined stress factor
        total_stress = (water_stress + nutrient_stress + temp_stress + humidity_stress) / 4
        
        # Growth rate modifier (0.5 to 1.5)
        growth_modifier = 1.0 - (total_stress * 0.5)
        growth_modifier = max(0.5, min(1.5, growth_modifier))
        
        # Calculate adjusted growth timeline
        adjusted_growth_days = int(plant_specs.growth_days / growth_modifier)
        
        # Calculate yield prediction
        base_yield = plant_specs.yield_per_plant
        yield_modifier = health_score * (1.0 - total_stress * 0.3)
        predicted_yield = base_yield * yield_modifier
        
        # Calculate stage progression
        stage_durations = {
            GrowthStage.SEED: 0.1,
            GrowthStage.SEEDLING: 0.2,
            GrowthStage.VEGETATIVE: 0.4,
            GrowthStage.FLOWERING: 0.2,
            GrowthStage.FRUITING: 0.1
        }
        
        current_progress = sum(stage_durations.get(stage, 0) for stage in 
                             list(GrowthStage)[:list(GrowthStage).index(placement.current_stage) + 1])
        
        days_elapsed = (datetime.now() - placement.planted_date).days
        total_progress = days_elapsed / adjusted_growth_days
        
        return {
            'growth_modifier': growth_modifier,
            'adjusted_growth_days': adjusted_growth_days,
            'predicted_yield': predicted_yield,
            'current_progress': min(1.0, total_progress),
            'days_to_harvest': max(0, adjusted_growth_days - days_elapsed),
            'health_score': health_score,
            'stress_factors': {
                'water': water_stress,
                'nutrient': nutrient_stress,
                'temperature': temp_stress,
                'humidity': humidity_stress
            }
        }

class PlacementOptimizer:
    """Advanced placement optimization using genetic algorithms and simulated annealing"""
    
    def __init__(self, calculator: AgronomicCalculator):
        self.calculator = calculator
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        
    async def optimize_placement_genetic(self, 
                                      plants: List[PlantSpecs],
                                      garden_zones: List[GardenZone],
                                      constraints: Dict) -> List[PlantPlacement]:
        """
        Optimize plant placement using genetic algorithm.
        """
        # Initialize population
        population = await self._initialize_population(plants, garden_zones, constraints)
        
        best_fitness = float('-inf')
        best_solution = None
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = await self._calculate_fitness(individual, garden_zones, constraints)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = individual.copy()
            
            # Selection
            new_population = []
            for _ in range(self.population_size // 2):
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1, garden_zones, constraints)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2, garden_zones, constraints)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
            
            if generation % 10 == 0:
                logger.info(f"Generation {generation}: Best fitness = {best_fitness}")
        
        return best_solution
    
    async def _initialize_population(self, plants: List[PlantSpecs], 
                                   garden_zones: List[GardenZone],
                                   constraints: Dict) -> List[List[PlantPlacement]]:
        """Initialize random population of plant placements"""
        population = []
        
        for _ in range(self.population_size):
            individual = []
            for plant_specs in plants:
                placement = await self._create_random_placement(plant_specs, garden_zones, constraints)
                individual.append(placement)
            population.append(individual)
        
        return population
    
    async def _create_random_placement(self, plant_specs: PlantSpecs,
                                     garden_zones: List[GardenZone],
                                     constraints: Dict) -> PlantPlacement:
        """Create a random valid plant placement"""
        # Select random zone
        zone = random.choice(garden_zones)
        
        # Generate random coordinates within zone bounds
        radius = math.sqrt(zone.area / math.pi)
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        
        x = zone.coordinates[0] + distance * math.cos(angle)
        y = zone.coordinates[1] + distance * math.sin(angle)
        
        return PlantPlacement(
            plant_id=f"{plant_specs.name}_{random.randint(1000, 9999)}",
            plant_specs=plant_specs,
            x=x,
            y=y,
            planted_date=datetime.now(),
            current_stage=GrowthStage.SEED
        )
    
    async def _calculate_fitness(self, individual: List[PlantPlacement],
                               garden_zones: List[GardenZone],
                               constraints: Dict) -> float:
        """Calculate fitness score for a placement solution"""
        if not individual:
            return float('-inf')
        
        # Spacing violations penalty
        spacing_penalty = 0
        for i, placement1 in enumerate(individual):
            for j, placement2 in enumerate(individual[i+1:], i+1):
                distance = math.sqrt((placement1.x - placement2.x)**2 + 
                                   (placement1.y - placement2.y)**2)
                min_spacing = self.calculator.calculate_optimal_spacing(
                    placement1.plant_specs, 0.7) / 100  # Convert to meters
                
                if distance < min_spacing:
                    spacing_penalty += (min_spacing - distance) * 10
        
        # Compatibility violations penalty
        compatibility_penalty = 0
        for i, placement1 in enumerate(individual):
            for j, placement2 in enumerate(individual[i+1:], i+1):
                if (placement2.plant_specs.name in placement1.plant_specs.incompatible_plants or
                    placement1.plant_specs.name in placement2.plant_specs.incompatible_plants):
                    distance = math.sqrt((placement1.x - placement2.x)**2 + 
                                       (placement1.y - placement2.y)**2)
                    if distance < 1.0:  # Within 1 meter
                        compatibility_penalty += 50
        
        # Zone constraint violations
        zone_penalty = 0
        for placement in individual:
            if not any(self.calculator._is_in_zone(placement, zone) for zone in garden_zones):
                zone_penalty += 100
        
        # Calculate total fitness (higher is better)
        total_penalty = spacing_penalty + compatibility_penalty + zone_penalty
        
        # Base fitness based on number of plants placed
        base_fitness = len(individual) * 10
        
        return base_fitness - total_penalty
    
    def _tournament_selection(self, population: List[List[PlantPlacement]], 
                            fitness_scores: List[float]) -> List[PlantPlacement]:
        """Tournament selection for genetic algorithm"""
        tournament_size = 3
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
        return population[winner_index]
    
    def _crossover(self, parent1: List[PlantPlacement], 
                  parent2: List[PlantPlacement]) -> Tuple[List[PlantPlacement], List[PlantPlacement]]:
        """Crossover operation for genetic algorithm"""
        if len(parent1) != len(parent2):
            return parent1.copy(), parent2.copy()
        
        crossover_point = random.randint(1, len(parent1) - 1)
        
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2
    
    def _mutate(self, individual: List[PlantPlacement],
                garden_zones: List[GardenZone],
                constraints: Dict) -> List[PlantPlacement]:
        """Mutation operation for genetic algorithm"""
        mutated = individual.copy()
        
        # Randomly mutate some placements
        for i in range(len(mutated)):
            if random.random() < 0.1:  # 10% mutation rate per placement
                # Small random adjustment to coordinates
                mutated[i].x += random.uniform(-0.5, 0.5)
                mutated[i].y += random.uniform(-0.5, 0.5)
        
        return mutated

class IrrigationPlanner:
    """Advanced irrigation zone planning and optimization"""
    
    def __init__(self, calculator: AgronomicCalculator):
        self.calculator = calculator
    
    async def calculate_irrigation_zones(self, placements: List[PlantPlacement],
                                       garden_zones: List[GardenZone],
                                       water_constraints: Dict) -> Dict:
        """
        Calculate optimal irrigation zones based on plant water needs and constraints.
        """
        # Group plants by water needs
        water_groups = {
            WaterNeed.LOW: [],
            WaterNeed.MEDIUM: [],
            WaterNeed.HIGH: []
        }
        
        for placement in placements:
            water_groups[placement.plant_specs.water_need].append(placement)
        
        # Calculate zones for each water need level
        zones = {}
        for water_need, plants in water_groups.items():
            if plants:
                zone_data = await self._create_irrigation_zone(plants, garden_zones, water_need)
                zones[water_need] = zone_data
        
        # Calculate total water requirements
        total_water_needs = {}
        for water_need, zone_data in zones.items():
            daily_water = sum(
                self.calculator.calculate_water_needs(
                    placement.plant_specs, 
                    water_constraints.get('weather', {}),
                    0.5,  # Default soil moisture
                    placement.current_stage
                ) for placement in zone_data['plants']
            )
            total_water_needs[water_need] = daily_water
        
        return {
            'zones': zones,
            'total_water_needs': total_water_needs,
            'efficiency_score': self._calculate_irrigation_efficiency(zones, total_water_needs)
        }
    
    async def _create_irrigation_zone(self, plants: List[PlantPlacement],
                                     garden_zones: List[GardenZone],
                                     water_need: WaterNeed) -> Dict:
        """Create an irrigation zone for plants with similar water needs"""
        if not plants:
            return {'plants': [], 'center': (0, 0), 'radius': 0}
        
        # Calculate center of the zone
        center_x = sum(p.x for p in plants) / len(plants)
        center_y = sum(p.y for p in plants) / len(plants)
        
        # Calculate radius to cover all plants
        max_distance = max(
            math.sqrt((p.x - center_x)**2 + (p.y - center_y)**2) 
            for p in plants
        )
        
        return {
            'plants': plants,
            'center': (center_x, center_y),
            'radius': max_distance + 1.0,  # Add 1m buffer
            'water_need': water_need
        }
    
    def _calculate_irrigation_efficiency(self, zones: Dict, water_needs: Dict) -> float:
        """Calculate irrigation efficiency score"""
        if not zones:
            return 0.0
        
        # Calculate overlap between zones
        total_overlap = 0
        zone_list = list(zones.values())
        
        for i, zone1 in enumerate(zone_list):
            for zone2 in zone_list[i+1:]:
                distance = math.sqrt(
                    (zone1['center'][0] - zone2['center'][0])**2 +
                    (zone1['center'][1] - zone2['center'][1])**2
                )
                combined_radius = zone1['radius'] + zone2['radius']
                
                if distance < combined_radius:
                    overlap = combined_radius - distance
                    total_overlap += overlap
        
        # Efficiency based on minimal overlap and balanced water distribution
        overlap_penalty = total_overlap * 0.1
        water_balance = 1.0 - (max(water_needs.values()) - min(water_needs.values())) / 10
        
        return max(0.0, min(1.0, water_balance - overlap_penalty))

class ConflictDetector:
    """Real-time conflict detection for plant compatibility and spacing"""
    
    def __init__(self, calculator: AgronomicCalculator):
        self.calculator = calculator
    
    async def detect_conflicts(self, placements: List[PlantPlacement],
                             garden_zones: List[GardenZone]) -> Dict:
        """
        Detect all conflicts in current plant placement.
        """
        conflicts = {
            'spacing_violations': [],
            'compatibility_violations': [],
            'zone_violations': [],
            'resource_conflicts': []
        }
        
        # Check spacing violations
        for i, placement1 in enumerate(placements):
            for j, placement2 in enumerate(placements[i+1:], i+1):
                distance = math.sqrt((placement1.x - placement2.x)**2 + 
                                   (placement1.y - placement2.y)**2)
                
                min_spacing = self.calculator.calculate_optimal_spacing(
                    placement1.plant_specs, 0.7) / 100
                
                if distance < min_spacing:
                    conflicts['spacing_violations'].append({
                        'plant1': placement1.plant_id,
                        'plant2': placement2.plant_id,
                        'current_distance': distance,
                        'required_distance': min_spacing,
                        'severity': 'high' if distance < min_spacing * 0.5 else 'medium'
                    })
        
        # Check compatibility violations
        for i, placement1 in enumerate(placements):
            for j, placement2 in enumerate(placements[i+1:], i+1):
                if (placement2.plant_specs.name in placement1.plant_specs.incompatible_plants or
                    placement1.plant_specs.name in placement2.plant_specs.incompatible_plants):
                    
                    distance = math.sqrt((placement1.x - placement2.x)**2 + 
                                       (placement1.y - placement2.y)**2)
                    
                    if distance < 2.0:  # Within 2 meters
                        conflicts['compatibility_violations'].append({
                            'plant1': placement1.plant_id,
                            'plant2': placement2.plant_id,
                            'distance': distance,
                            'severity': 'high'
                        })
        
        # Check zone violations
        for placement in placements:
            in_valid_zone = any(
                self.calculator._is_in_zone(placement, zone) 
                for zone in garden_zones
            )
            
            if not in_valid_zone:
                conflicts['zone_violations'].append({
                    'plant_id': placement.plant_id,
                    'position': (placement.x, placement.y),
                    'severity': 'high'
                })
        
        # Check resource conflicts (water, nutrients)
        water_conflicts = await self._detect_water_conflicts(placements, garden_zones)
        conflicts['resource_conflicts'].extend(water_conflicts)
        
        return conflicts
    
    async def _detect_water_conflicts(self, placements: List[PlantPlacement],
                                    garden_zones: List[GardenZone]) -> List[Dict]:
        """Detect water resource conflicts"""
        conflicts = []
        
        # Group plants by proximity
        for i, placement1 in enumerate(placements):
            high_water_plants = []
            
            for placement2 in placements[i+1:]:
                distance = math.sqrt((placement1.x - placement2.x)**2 + 
                                   (placement1.y - placement2.y)**2)
                
                if distance < 1.0:  # Within 1 meter
                    if (placement1.plant_specs.water_need == WaterNeed.HIGH and
                        placement2.plant_specs.water_need == WaterNeed.HIGH):
                        high_water_plants.append(placement2.plant_id)
            
            if len(high_water_plants) > 2:  # More than 2 high-water plants in close proximity
                conflicts.append({
                    'type': 'water_competition',
                    'plants': [placement1.plant_id] + high_water_plants,
                    'severity': 'medium',
                    'description': 'Multiple high-water-need plants in close proximity'
                })
        
        return conflicts

class AgronomicEngine:
    """Main agronomic computation engine orchestrating all calculations"""
    
    def __init__(self):
        self.calculator = AgronomicCalculator()
        self.optimizer = PlacementOptimizer(self.calculator)
        self.irrigation_planner = IrrigationPlanner(self.calculator)
        self.conflict_detector = ConflictDetector(self.calculator)
        self.cache = {}
    
    async def calculate_comprehensive_analysis(self, 
                                            placements: List[PlantPlacement],
                                            garden_zones: List[GardenZone],
                                            environmental_data: Dict) -> Dict:
        """
        Perform comprehensive agronomic analysis including all calculations.
        """
        # Calculate water needs per zone
        water_analysis = await self.irrigation_planner.calculate_irrigation_zones(
            placements, garden_zones, environmental_data
        )
        
        # Calculate solar exposure for each plant
        solar_analysis = {}
        for placement in placements:
            solar_score = self.calculator.calculate_solar_exposure(
                placement, garden_zones, environmental_data.get('sun_data', {})
            )
            solar_analysis[placement.plant_id] = solar_score
        
        # Calculate growth predictions
        growth_predictions = {}
        for placement in placements:
            prediction = self.calculator.calculate_growth_prediction(
                placement.plant_specs, placement, environmental_data
            )
            growth_predictions[placement.plant_id] = prediction
        
        # Detect conflicts
        conflicts = await self.conflict_detector.detect_conflicts(placements, garden_zones)
        
        # Calculate yield estimates
        total_yield = sum(
            prediction['predicted_yield'] 
            for prediction in growth_predictions.values()
        )
        
        # Calculate efficiency metrics
        efficiency_metrics = self._calculate_efficiency_metrics(
            placements, water_analysis, solar_analysis, conflicts
        )
        
        return {
            'water_analysis': water_analysis,
            'solar_analysis': solar_analysis,
            'growth_predictions': growth_predictions,
            'conflicts': conflicts,
            'total_predicted_yield': total_yield,
            'efficiency_metrics': efficiency_metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_efficiency_metrics(self, placements: List[PlantPlacement],
                                    water_analysis: Dict,
                                    solar_analysis: Dict,
                                    conflicts: Dict) -> Dict:
        """Calculate overall garden efficiency metrics"""
        if not placements:
            return {'overall_score': 0.0, 'details': {}}
        
        # Space utilization
        total_area = sum(zone.area for zone in water_analysis.get('zones', {}).values())
        space_utilization = len(placements) / max(total_area, 1.0)
        
        # Water efficiency
        water_efficiency = water_analysis.get('efficiency_score', 0.0)
        
        # Solar efficiency
        avg_solar_score = sum(solar_analysis.values()) / len(solar_analysis) if solar_analysis else 0.0
        
        # Conflict penalty
        conflict_penalty = (
            len(conflicts.get('spacing_violations', [])) * 0.1 +
            len(conflicts.get('compatibility_violations', [])) * 0.2 +
            len(conflicts.get('zone_violations', [])) * 0.3
        )
        
        # Overall score (0-100)
        overall_score = (
            space_utilization * 25 +
            water_efficiency * 25 +
            avg_solar_score * 25 +
            (1.0 - min(conflict_penalty, 1.0)) * 25
        )
        
        return {
            'overall_score': min(100.0, max(0.0, overall_score)),
            'space_utilization': space_utilization,
            'water_efficiency': water_efficiency,
            'solar_efficiency': avg_solar_score,
            'conflict_penalty': conflict_penalty,
            'details': {
                'total_plants': len(placements),
                'total_conflicts': sum(len(conflicts.get(key, [])) for key in conflicts),
                'avg_water_need': sum(p.plant_specs.water_need.value for p in placements) / len(placements)
            }
        }
    
    async def optimize_placement(self, plants: List[PlantSpecs],
                               garden_zones: List[GardenZone],
                               constraints: Dict) -> List[PlantPlacement]:
        """
        Optimize plant placement using genetic algorithm.
        """
        return await self.optimizer.optimize_placement_genetic(
            plants, garden_zones, constraints
        )
    
    async def calculate_incremental_update(self, 
                                         current_placements: List[PlantPlacement],
                                         new_placement: PlantPlacement,
                                         garden_zones: List[GardenZone],
                                         environmental_data: Dict) -> Dict:
        """
        Calculate incremental updates when a single plant is added/modified.
        """
        # Add new placement to existing ones
        updated_placements = current_placements + [new_placement]
        
        # Calculate only the affected metrics
        affected_metrics = {
            'new_plant_analysis': {
                'water_need': self.calculator.calculate_water_needs(
                    new_placement.plant_specs,
                    environmental_data.get('weather', {}),
                    0.5,
                    new_placement.current_stage
                ),
                'solar_exposure': self.calculator.calculate_solar_exposure(
                    new_placement, garden_zones, environmental_data.get('sun_data', {})
                ),
                'growth_prediction': self.calculator.calculate_growth_prediction(
                    new_placement.plant_specs, new_placement, environmental_data
                )
            },
            'conflicts_with_new_plant': await self.conflict_detector.detect_conflicts(
                updated_placements, garden_zones
            ),
            'updated_irrigation_zones': await self.irrigation_planner.calculate_irrigation_zones(
                updated_placements, garden_zones, environmental_data
            )
        }
        
        return affected_metrics 