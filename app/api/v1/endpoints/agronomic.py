from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.agronomic_engine import (
    AgronomicEngine, PlantSpecs, GardenZone, PlantPlacement,
    PlantType, WaterNeed, SunExposure, GrowthStage
)
from app.services.websocket_manager import WebSocketManager
from app.core.config import settings
import redis.asyncio as redis

router = APIRouter()
agronomic_engine = AgronomicEngine()
websocket_manager = WebSocketManager()

# Pydantic models for API requests/responses
class PlantSpecsRequest(BaseModel):
    name: str
    type: PlantType
    spacing_min: float = Field(..., gt=0)
    spacing_optimal: float = Field(..., gt=0)
    water_need: WaterNeed
    sun_exposure: SunExposure
    growth_days: int = Field(..., gt=0)
    height_max: float = Field(..., gt=0)
    width_max: float = Field(..., gt=0)
    root_depth: float = Field(..., gt=0)
    yield_per_plant: float = Field(..., gt=0)
    companion_plants: List[str] = []
    incompatible_plants: List[str] = []
    water_consumption_daily: float = 0.0
    nutrient_requirements: Dict[str, float] = {}
    frost_tolerance: bool = False
    heat_tolerance: bool = False

class GardenZoneRequest(BaseModel):
    id: str
    name: str
    area: float = Field(..., gt=0)
    soil_type: str
    ph_level: float = Field(..., ge=0, le=14)
    sun_exposure: SunExposure
    water_availability: float = Field(..., gt=0)
    elevation: float = 0.0
    slope: float = Field(..., ge=0, le=90)
    coordinates: tuple[float, float] = (0.0, 0.0)

class PlantPlacementRequest(BaseModel):
    plant_id: str
    plant_specs: PlantSpecsRequest
    x: float
    y: float
    planted_date: datetime
    current_stage: GrowthStage = GrowthStage.SEED
    health_score: float = Field(1.0, ge=0, le=1)
    water_stress: float = Field(0.0, ge=0, le=1)
    nutrient_stress: float = Field(0.0, ge=0, le=1)

class EnvironmentalDataRequest(BaseModel):
    weather: Dict[str, Any] = {}
    sun_data: Dict[str, Any] = {}
    soil_moisture: float = Field(0.5, ge=0, le=1)
    temperature: float = 20.0
    humidity: float = Field(0.5, ge=0, le=1)
    wind_speed: float = 0.0
    precipitation: float = 0.0

class OptimizationConstraintsRequest(BaseModel):
    max_plants: Optional[int] = None
    min_spacing: float = 0.3
    max_water_usage: Optional[float] = None
    preferred_zones: List[str] = []
    excluded_zones: List[str] = []
    companion_plant_preferences: Dict[str, List[str]] = {}
    incompatible_plant_restrictions: Dict[str, List[str]] = {}

class AnalysisResponse(BaseModel):
    water_analysis: Dict[str, Any]
    solar_analysis: Dict[str, float]
    growth_predictions: Dict[str, Dict[str, Any]]
    conflicts: Dict[str, List[Dict[str, Any]]]
    total_predicted_yield: float
    efficiency_metrics: Dict[str, Any]
    timestamp: str

class OptimizationResponse(BaseModel):
    optimized_placements: List[Dict[str, Any]]
    fitness_score: float
    conflicts_resolved: int
    water_efficiency: float
    space_utilization: float
    computation_time: float

class IncrementalUpdateResponse(BaseModel):
    new_plant_analysis: Dict[str, Any]
    conflicts_with_new_plant: Dict[str, List[Dict[str, Any]]]
    updated_irrigation_zones: Dict[str, Any]
    affected_metrics: Dict[str, Any]

# Cache for storing computation results
computation_cache = {}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_garden(
    placements: List[PlantPlacementRequest],
    garden_zones: List[GardenZoneRequest],
    environmental_data: EnvironmentalDataRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform comprehensive agronomic analysis of garden layout.
    """
    try:
        # Convert request models to internal models
        plant_placements = []
        for placement_req in placements:
            plant_specs = PlantSpecs(
                name=placement_req.plant_specs.name,
                type=placement_req.plant_specs.type,
                spacing_min=placement_req.plant_specs.spacing_min,
                spacing_optimal=placement_req.plant_specs.spacing_optimal,
                water_need=placement_req.plant_specs.water_need,
                sun_exposure=placement_req.plant_specs.sun_exposure,
                growth_days=placement_req.plant_specs.growth_days,
                height_max=placement_req.plant_specs.height_max,
                width_max=placement_req.plant_specs.width_max,
                root_depth=placement_req.plant_specs.root_depth,
                yield_per_plant=placement_req.plant_specs.yield_per_plant,
                companion_plants=placement_req.plant_specs.companion_plants,
                incompatible_plants=placement_req.plant_specs.incompatible_plants,
                water_consumption_daily=placement_req.plant_specs.water_consumption_daily,
                nutrient_requirements=placement_req.plant_specs.nutrient_requirements,
                frost_tolerance=placement_req.plant_specs.frost_tolerance,
                heat_tolerance=placement_req.plant_specs.heat_tolerance
            )
            
            placement = PlantPlacement(
                plant_id=placement_req.plant_id,
                plant_specs=plant_specs,
                x=placement_req.x,
                y=placement_req.y,
                planted_date=placement_req.planted_date,
                current_stage=placement_req.current_stage,
                health_score=placement_req.health_score,
                water_stress=placement_req.water_stress,
                nutrient_stress=placement_req.nutrient_stress
            )
            plant_placements.append(placement)
        
        zones = []
        for zone_req in garden_zones:
            zone = GardenZone(
                id=zone_req.id,
                name=zone_req.name,
                area=zone_req.area,
                soil_type=zone_req.soil_type,
                ph_level=zone_req.ph_level,
                sun_exposure=zone_req.sun_exposure,
                water_availability=zone_req.water_availability,
                elevation=zone_req.elevation,
                slope=zone_req.slope,
                coordinates=zone_req.coordinates
            )
            zones.append(zone)
        
        # Prepare environmental data
        env_data = {
            'weather': environmental_data.weather,
            'sun_data': environmental_data.sun_data,
            'soil_moisture': environmental_data.soil_moisture,
            'temperature_stress': max(0, abs(environmental_data.temperature - 20) / 20),
            'humidity_stress': abs(environmental_data.humidity - 0.6) / 0.6
        }
        
        # Perform comprehensive analysis
        analysis_result = await agronomic_engine.calculate_comprehensive_analysis(
            plant_placements, zones, env_data
        )
        
        # Cache the result
        cache_key = f"analysis_{current_user.id}_{hash(str(placements) + str(zones))}"
        computation_cache[cache_key] = {
            'result': analysis_result,
            'timestamp': datetime.now().isoformat()
        }
        
        return AnalysisResponse(**analysis_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_placement(
    plants: List[PlantSpecsRequest],
    garden_zones: List[GardenZoneRequest],
    constraints: OptimizationConstraintsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Optimize plant placement using genetic algorithms.
    """
    try:
        import time
        start_time = time.time()
        
        # Convert request models to internal models
        plant_specs_list = []
        for plant_req in plants:
            plant_specs = PlantSpecs(
                name=plant_req.name,
                type=plant_req.type,
                spacing_min=plant_req.spacing_min,
                spacing_optimal=plant_req.spacing_optimal,
                water_need=plant_req.water_need,
                sun_exposure=plant_req.sun_exposure,
                growth_days=plant_req.growth_days,
                height_max=plant_req.height_max,
                width_max=plant_req.width_max,
                root_depth=plant_req.root_depth,
                yield_per_plant=plant_req.yield_per_plant,
                companion_plants=plant_req.companion_plants,
                incompatible_plants=plant_req.incompatible_plants,
                water_consumption_daily=plant_req.water_consumption_daily,
                nutrient_requirements=plant_req.nutrient_requirements,
                frost_tolerance=plant_req.frost_tolerance,
                heat_tolerance=plant_req.heat_tolerance
            )
            plant_specs_list.append(plant_specs)
        
        zones = []
        for zone_req in garden_zones:
            zone = GardenZone(
                id=zone_req.id,
                name=zone_req.name,
                area=zone_req.area,
                soil_type=zone_req.soil_type,
                ph_level=zone_req.ph_level,
                sun_exposure=zone_req.sun_exposure,
                water_availability=zone_req.water_availability,
                elevation=zone_req.elevation,
                slope=zone_req.slope,
                coordinates=zone_req.coordinates
            )
            zones.append(zone)
        
        # Prepare constraints
        optimization_constraints = {
            'max_plants': constraints.max_plants,
            'min_spacing': constraints.min_spacing,
            'max_water_usage': constraints.max_water_usage,
            'preferred_zones': constraints.preferred_zones,
            'excluded_zones': constraints.excluded_zones,
            'companion_preferences': constraints.companion_plant_preferences,
            'incompatible_restrictions': constraints.incompatible_plant_restrictions
        }
        
        # Perform optimization
        optimized_placements = await agronomic_engine.optimize_placement(
            plant_specs_list, zones, optimization_constraints
        )
        
        computation_time = time.time() - start_time
        
        # Calculate metrics for response
        conflicts = await agronomic_engine.conflict_detector.detect_conflicts(optimized_placements, zones)
        total_conflicts = sum(len(conflicts.get(key, [])) for key in conflicts)
        
        # Calculate water efficiency
        water_analysis = await agronomic_engine.irrigation_planner.calculate_irrigation_zones(
            optimized_placements, zones, {}
        )
        water_efficiency = water_analysis.get('efficiency_score', 0.0)
        
        # Calculate space utilization
        total_area = sum(zone.area for zone in zones)
        space_utilization = len(optimized_placements) / max(total_area, 1.0)
        
        # Calculate fitness score
        fitness_score = len(optimized_placements) * 10 - total_conflicts * 5
        
        # Convert placements to dict format for response
        placement_dicts = []
        for placement in optimized_placements:
            placement_dict = {
                'plant_id': placement.plant_id,
                'plant_name': placement.plant_specs.name,
                'x': placement.x,
                'y': placement.y,
                'planted_date': placement.planted_date.isoformat(),
                'current_stage': placement.current_stage.value,
                'health_score': placement.health_score,
                'water_stress': placement.water_stress,
                'nutrient_stress': placement.nutrient_stress
            }
            placement_dicts.append(placement_dict)
        
        return OptimizationResponse(
            optimized_placements=placement_dicts,
            fitness_score=fitness_score,
            conflicts_resolved=total_conflicts,
            water_efficiency=water_efficiency,
            space_utilization=space_utilization,
            computation_time=computation_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/incremental-update", response_model=IncrementalUpdateResponse)
async def calculate_incremental_update(
    current_placements: List[PlantPlacementRequest],
    new_placement: PlantPlacementRequest,
    garden_zones: List[GardenZoneRequest],
    environmental_data: EnvironmentalDataRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate incremental updates when a single plant is added/modified.
    """
    try:
        # Convert current placements
        current_plant_placements = []
        for placement_req in current_placements:
            plant_specs = PlantSpecs(
                name=placement_req.plant_specs.name,
                type=placement_req.plant_specs.type,
                spacing_min=placement_req.plant_specs.spacing_min,
                spacing_optimal=placement_req.plant_specs.spacing_optimal,
                water_need=placement_req.plant_specs.water_need,
                sun_exposure=placement_req.plant_specs.sun_exposure,
                growth_days=placement_req.plant_specs.growth_days,
                height_max=placement_req.plant_specs.height_max,
                width_max=placement_req.plant_specs.width_max,
                root_depth=placement_req.plant_specs.root_depth,
                yield_per_plant=placement_req.plant_specs.yield_per_plant,
                companion_plants=placement_req.plant_specs.companion_plants,
                incompatible_plants=placement_req.plant_specs.incompatible_plants,
                water_consumption_daily=placement_req.plant_specs.water_consumption_daily,
                nutrient_requirements=placement_req.plant_specs.nutrient_requirements,
                frost_tolerance=placement_req.plant_specs.frost_tolerance,
                heat_tolerance=placement_req.plant_specs.heat_tolerance
            )
            
            placement = PlantPlacement(
                plant_id=placement_req.plant_id,
                plant_specs=plant_specs,
                x=placement_req.x,
                y=placement_req.y,
                planted_date=placement_req.planted_date,
                current_stage=placement_req.current_stage,
                health_score=placement_req.health_score,
                water_stress=placement_req.water_stress,
                nutrient_stress=placement_req.nutrient_stress
            )
            current_plant_placements.append(placement)
        
        # Convert new placement
        new_plant_specs = PlantSpecs(
            name=new_placement.plant_specs.name,
            type=new_placement.plant_specs.type,
            spacing_min=new_placement.plant_specs.spacing_min,
            spacing_optimal=new_placement.plant_specs.spacing_optimal,
            water_need=new_placement.plant_specs.water_need,
            sun_exposure=new_placement.plant_specs.sun_exposure,
            growth_days=new_placement.plant_specs.growth_days,
            height_max=new_placement.plant_specs.height_max,
            width_max=new_placement.plant_specs.width_max,
            root_depth=new_placement.plant_specs.root_depth,
            yield_per_plant=new_placement.plant_specs.yield_per_plant,
            companion_plants=new_placement.plant_specs.companion_plants,
            incompatible_plants=new_placement.plant_specs.incompatible_plants,
            water_consumption_daily=new_placement.plant_specs.water_consumption_daily,
            nutrient_requirements=new_placement.plant_specs.nutrient_requirements,
            frost_tolerance=new_placement.plant_specs.frost_tolerance,
            heat_tolerance=new_placement.plant_specs.heat_tolerance
        )
        
        new_plant_placement = PlantPlacement(
            plant_id=new_placement.plant_id,
            plant_specs=new_plant_specs,
            x=new_placement.x,
            y=new_placement.y,
            planted_date=new_placement.planted_date,
            current_stage=new_placement.current_stage,
            health_score=new_placement.health_score,
            water_stress=new_placement.water_stress,
            nutrient_stress=new_placement.nutrient_stress
        )
        
        # Convert zones
        zones = []
        for zone_req in garden_zones:
            zone = GardenZone(
                id=zone_req.id,
                name=zone_req.name,
                area=zone_req.area,
                soil_type=zone_req.soil_type,
                ph_level=zone_req.ph_level,
                sun_exposure=zone_req.sun_exposure,
                water_availability=zone_req.water_availability,
                elevation=zone_req.elevation,
                slope=zone_req.slope,
                coordinates=zone_req.coordinates
            )
            zones.append(zone)
        
        # Prepare environmental data
        env_data = {
            'weather': environmental_data.weather,
            'sun_data': environmental_data.sun_data,
            'soil_moisture': environmental_data.soil_moisture,
            'temperature_stress': max(0, abs(environmental_data.temperature - 20) / 20),
            'humidity_stress': abs(environmental_data.humidity - 0.6) / 0.6
        }
        
        # Calculate incremental update
        incremental_result = await agronomic_engine.calculate_incremental_update(
            current_plant_placements, new_plant_placement, zones, env_data
        )
        
        return IncrementalUpdateResponse(**incremental_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Incremental update failed: {str(e)}")

@router.get("/cache/{cache_key}")
async def get_cached_result(
    cache_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve cached computation results.
    """
    if cache_key in computation_cache:
        return computation_cache[cache_key]
    else:
        raise HTTPException(status_code=404, detail="Cached result not found")

@router.delete("/cache/{cache_key}")
async def clear_cached_result(
    cache_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    Clear cached computation results.
    """
    if cache_key in computation_cache:
        del computation_cache[cache_key]
        return {"message": "Cache cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Cached result not found")

@router.websocket("/ws/agronomic-updates/{user_id}")
async def agronomic_websocket(
    websocket: WebSocket,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time agronomic updates.
    """
    await websocket.accept()
    
    try:
        # Add to websocket manager
        websocket_manager.add_connection(user_id, websocket)
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "subscribe_analysis":
                    # Subscribe to analysis updates
                    await websocket_manager.subscribe_to_analysis(user_id, message.get("garden_id"))
                    
                elif message.get("type") == "request_optimization":
                    # Handle optimization requests
                    await handle_optimization_request(websocket, message, user_id)
                    
                elif message.get("type") == "ping":
                    # Respond to ping
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        # Remove from websocket manager
        websocket_manager.remove_connection(user_id)

async def handle_optimization_request(websocket: WebSocket, message: Dict, user_id: str):
    """
    Handle optimization requests via WebSocket.
    """
    try:
        # Extract optimization parameters from message
        plants_data = message.get("plants", [])
        zones_data = message.get("zones", [])
        constraints_data = message.get("constraints", {})
        
        # Convert to internal models (simplified for WebSocket)
        plants = []
        for plant_data in plants_data:
            plant_specs = PlantSpecs(
                name=plant_data["name"],
                type=PlantType(plant_data["type"]),
                spacing_min=plant_data["spacing_min"],
                spacing_optimal=plant_data["spacing_optimal"],
                water_need=WaterNeed(plant_data["water_need"]),
                sun_exposure=SunExposure(plant_data["sun_exposure"]),
                growth_days=plant_data["growth_days"],
                height_max=plant_data["height_max"],
                width_max=plant_data["width_max"],
                root_depth=plant_data["root_depth"],
                yield_per_plant=plant_data["yield_per_plant"],
                companion_plants=plant_data.get("companion_plants", []),
                incompatible_plants=plant_data.get("incompatible_plants", [])
            )
            plants.append(plant_specs)
        
        zones = []
        for zone_data in zones_data:
            zone = GardenZone(
                id=zone_data["id"],
                name=zone_data["name"],
                area=zone_data["area"],
                soil_type=zone_data["soil_type"],
                ph_level=zone_data["ph_level"],
                sun_exposure=SunExposure(zone_data["sun_exposure"]),
                water_availability=zone_data["water_availability"],
                elevation=zone_data.get("elevation", 0.0),
                slope=zone_data.get("slope", 0.0),
                coordinates=zone_data.get("coordinates", (0.0, 0.0))
            )
            zones.append(zone)
        
        # Send progress updates
        await websocket.send_text(json.dumps({
            "type": "optimization_started",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Perform optimization
        optimized_placements = await agronomic_engine.optimize_placement(
            plants, zones, constraints_data
        )
        
        # Send results
        placement_results = []
        for placement in optimized_placements:
            placement_result = {
                "plant_id": placement.plant_id,
                "plant_name": placement.plant_specs.name,
                "x": placement.x,
                "y": placement.y,
                "planted_date": placement.planted_date.isoformat(),
                "current_stage": placement.current_stage.value
            }
            placement_results.append(placement_result)
        
        await websocket.send_text(json.dumps({
            "type": "optimization_completed",
            "placements": placement_results,
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Optimization failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }))

@router.post("/broadcast-update")
async def broadcast_agronomic_update(
    garden_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast agronomic updates to all connected clients for a specific garden.
    """
    try:
        # Prepare update message
        message = {
            "type": "agronomic_update",
            "garden_id": garden_id,
            "data": update_data,
            "timestamp": datetime.now().isoformat(),
            "user_id": str(current_user.id)
        }
        
        # Broadcast to all connected clients for this garden
        await websocket_manager.broadcast_to_garden(garden_id, message)
        
        return {"message": "Update broadcasted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the agronomic engine.
    """
    return {
        "status": "healthy",
        "engine": "agronomic",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(computation_cache),
        "active_connections": len(websocket_manager.active_connections)
    } 