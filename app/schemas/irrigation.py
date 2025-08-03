from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# Enums
class EquipmentType(str, Enum):
    """Types of irrigation equipment."""
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    MICROJET = "microjet"
    ROTOR = "rotor"
    SPRAY = "spray"


class PipeMaterial(str, Enum):
    """Types of pipe materials."""
    PVC = "pvc"
    PE = "pe"
    PEX = "pex"
    COPPER = "copper"


class ZoneStatus(str, Enum):
    """Status of irrigation zones."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class ScheduleType(str, Enum):
    """Types of irrigation schedules."""
    DAILY = "daily"
    WEEKLY = "weekly"
    WEATHER_BASED = "weather_based"
    MANUAL = "manual"


class WaterSourceType(str, Enum):
    """Types of water sources."""
    TAP = "tap"
    WELL = "well"
    TANK = "tank"
    STREAM = "stream"


# Base schemas
class IrrigationEquipmentBase(BaseModel):
    """Base schema for irrigation equipment."""
    name: str = Field(..., description="Equipment name")
    equipment_type: EquipmentType = Field(..., description="Type of equipment")
    manufacturer: str = Field(..., description="Manufacturer name")
    model: str = Field(..., description="Model number")
    flow_rate_lph: float = Field(..., description="Flow rate in liters per hour")
    pressure_range_min: float = Field(..., description="Minimum operating pressure in bar")
    pressure_range_max: float = Field(..., description="Maximum operating pressure in bar")
    coverage_radius_m: float = Field(..., description="Coverage radius in meters")
    spacing_m: float = Field(..., description="Recommended spacing in meters")
    cost_per_unit: float = Field(..., description="Cost per unit in USD")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Additional specifications")


class IrrigationZoneBase(BaseModel):
    """Base schema for irrigation zones."""
    name: str = Field(..., description="Zone name")
    description: Optional[str] = Field(None, description="Zone description")
    status: ZoneStatus = Field(default=ZoneStatus.ACTIVE, description="Zone status")
    required_flow_lph: float = Field(..., description="Required flow rate in liters per hour")
    operating_pressure_bar: float = Field(..., description="Operating pressure in bar")
    total_area_m2: float = Field(..., description="Total area in square meters")
    cluster_center_x: float = Field(..., description="Cluster center X coordinate")
    cluster_center_y: float = Field(..., description="Cluster center Y coordinate")
    plant_ids: List[int] = Field(..., description="List of plant IDs in this zone")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost in USD")


class IrrigationPipeBase(BaseModel):
    """Base schema for irrigation pipes."""
    pipe_name: str = Field(..., description="Pipe name")
    pipe_type: str = Field(..., description="Type of pipe (main, lateral, sub-lateral)")
    material: PipeMaterial = Field(..., description="Pipe material")
    diameter_mm: float = Field(..., description="Pipe diameter in millimeters")
    length_m: float = Field(..., description="Pipe length in meters")
    flow_rate_lph: float = Field(..., description="Flow rate in liters per hour")
    velocity_ms: float = Field(..., description="Flow velocity in meters per second")
    pressure_loss_bar: float = Field(..., description="Pressure loss in bar")
    start_x: float = Field(..., description="Start X coordinate")
    start_y: float = Field(..., description="Start Y coordinate")
    end_x: float = Field(..., description="End X coordinate")
    end_y: float = Field(..., description="End Y coordinate")
    cost_per_meter: float = Field(..., description="Cost per meter in USD")
    total_cost: float = Field(..., description="Total cost in USD")


class IrrigationScheduleBase(BaseModel):
    """Base schema for irrigation schedules."""
    name: str = Field(..., description="Schedule name")
    schedule_type: ScheduleType = Field(..., description="Type of schedule")
    start_time: time = Field(..., description="Start time")
    duration_minutes: int = Field(..., description="Duration in minutes")
    days_of_week: Optional[List[int]] = Field(None, description="Days of week (0=Monday, 6=Sunday)")
    interval_days: Optional[int] = Field(None, description="Interval in days")
    min_temperature_c: Optional[float] = Field(None, description="Minimum temperature in Celsius")
    max_temperature_c: Optional[float] = Field(None, description="Maximum temperature in Celsius")
    min_humidity_percent: Optional[float] = Field(None, description="Minimum humidity percentage")
    max_humidity_percent: Optional[float] = Field(None, description="Maximum humidity percentage")
    min_rainfall_mm: Optional[float] = Field(None, description="Minimum rainfall in millimeters")
    is_active: bool = Field(default=True, description="Whether schedule is active")
    priority: int = Field(default=1, description="Schedule priority")


class WeatherDataBase(BaseModel):
    """Base schema for weather data."""
    date: datetime = Field(..., description="Weather data date")
    temperature_c: float = Field(..., description="Temperature in Celsius")
    humidity_percent: float = Field(..., description="Humidity percentage")
    rainfall_mm: float = Field(..., description="Rainfall in millimeters")
    wind_speed_kmh: float = Field(..., description="Wind speed in kilometers per hour")
    solar_radiation_mj_m2: float = Field(..., description="Solar radiation in MJ/m²")
    evapotranspiration_mm: float = Field(..., description="Evapotranspiration in millimeters")
    irrigation_need_mm: float = Field(..., description="Irrigation need in millimeters")
    source: str = Field(..., description="Weather data source")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw weather data")


class IrrigationProjectBase(BaseModel):
    """Base schema for irrigation projects."""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    water_source_type: WaterSourceType = Field(..., description="Type of water source")
    source_pressure_bar: float = Field(..., description="Source pressure in bar")
    source_flow_lph: float = Field(..., description="Source flow rate in liters per hour")
    total_equipment_cost: Optional[float] = Field(None, description="Total equipment cost in USD")
    total_pipe_cost: Optional[float] = Field(None, description="Total pipe cost in USD")
    total_installation_cost: Optional[float] = Field(None, description="Total installation cost in USD")
    total_project_cost: Optional[float] = Field(None, description="Total project cost in USD")
    hydraulic_calculations: Optional[Dict[str, Any]] = Field(None, description="Hydraulic calculations data")
    network_layout: Optional[Dict[str, Any]] = Field(None, description="Network layout data")
    equipment_selection: Optional[Dict[str, Any]] = Field(None, description="Equipment selection data")
    is_active: bool = Field(default=True, description="Whether project is active")


# Create schemas
class IrrigationEquipmentCreate(IrrigationEquipmentBase):
    """Schema for creating irrigation equipment."""
    pass


class IrrigationZoneCreate(IrrigationZoneBase):
    """Schema for creating irrigation zones."""
    garden_id: UUID = Field(..., description="Garden ID")


class IrrigationPipeCreate(IrrigationPipeBase):
    """Schema for creating irrigation pipes."""
    zone_id: UUID = Field(..., description="Zone ID")


class IrrigationScheduleCreate(IrrigationScheduleBase):
    """Schema for creating irrigation schedules."""
    zone_id: UUID = Field(..., description="Zone ID")


class WeatherDataCreate(WeatherDataBase):
    """Schema for creating weather data."""
    garden_id: UUID = Field(..., description="Garden ID")


class IrrigationProjectCreate(IrrigationProjectBase):
    """Schema for creating irrigation projects."""
    garden_id: UUID = Field(..., description="Garden ID")


# Update schemas
class IrrigationEquipmentUpdate(BaseModel):
    """Schema for updating irrigation equipment."""
    name: Optional[str] = None
    equipment_type: Optional[EquipmentType] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    flow_rate_lph: Optional[float] = None
    pressure_range_min: Optional[float] = None
    pressure_range_max: Optional[float] = None
    coverage_radius_m: Optional[float] = None
    spacing_m: Optional[float] = None
    cost_per_unit: Optional[float] = None
    specifications: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IrrigationZoneUpdate(BaseModel):
    """Schema for updating irrigation zones."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ZoneStatus] = None
    required_flow_lph: Optional[float] = None
    operating_pressure_bar: Optional[float] = None
    total_area_m2: Optional[float] = None
    cluster_center_x: Optional[float] = None
    cluster_center_y: Optional[float] = None
    plant_ids: Optional[List[int]] = None
    estimated_cost: Optional[float] = None


class IrrigationPipeUpdate(BaseModel):
    """Schema for updating irrigation pipes."""
    pipe_name: Optional[str] = None
    pipe_type: Optional[str] = None
    material: Optional[PipeMaterial] = None
    diameter_mm: Optional[float] = None
    length_m: Optional[float] = None
    flow_rate_lph: Optional[float] = None
    velocity_ms: Optional[float] = None
    pressure_loss_bar: Optional[float] = None
    start_x: Optional[float] = None
    start_y: Optional[float] = None
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    cost_per_meter: Optional[float] = None
    total_cost: Optional[float] = None


class IrrigationScheduleUpdate(BaseModel):
    """Schema for updating irrigation schedules."""
    name: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    start_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    days_of_week: Optional[List[int]] = None
    interval_days: Optional[int] = None
    min_temperature_c: Optional[float] = None
    max_temperature_c: Optional[float] = None
    min_humidity_percent: Optional[float] = None
    max_humidity_percent: Optional[float] = None
    min_rainfall_mm: Optional[float] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class IrrigationProjectUpdate(BaseModel):
    """Schema for updating irrigation projects."""
    name: Optional[str] = None
    description: Optional[str] = None
    water_source_type: Optional[WaterSourceType] = None
    source_pressure_bar: Optional[float] = None
    source_flow_lph: Optional[float] = None
    total_equipment_cost: Optional[float] = None
    total_pipe_cost: Optional[float] = None
    total_installation_cost: Optional[float] = None
    total_project_cost: Optional[float] = None
    hydraulic_calculations: Optional[Dict[str, Any]] = None
    network_layout: Optional[Dict[str, Any]] = None
    equipment_selection: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


# Response schemas
class IrrigationEquipment(IrrigationEquipmentBase):
    """Schema for returning irrigation equipment."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IrrigationZone(IrrigationZoneBase):
    """Schema for returning irrigation zones."""
    id: UUID
    garden_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IrrigationPipe(IrrigationPipeBase):
    """Schema for returning irrigation pipes."""
    id: UUID
    zone_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IrrigationSchedule(IrrigationScheduleBase):
    """Schema for returning irrigation schedules."""
    id: UUID
    zone_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WeatherData(WeatherDataBase):
    """Schema for returning weather data."""
    id: UUID
    garden_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IrrigationProject(IrrigationProjectBase):
    """Schema for returning irrigation projects."""
    id: UUID
    garden_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Specialized schemas for hydraulic calculations
class HydraulicCalculationInput(BaseModel):
    """Input for hydraulic calculations."""
    zones: List[IrrigationZone]
    source_pressure_bar: float = Field(..., description="Source pressure in bar")
    source_flow_lph: float = Field(..., description="Source flow rate in liters per hour")
    pipe_material: PipeMaterial = Field(..., description="Pipe material")
    pipe_diameter_mm: float = Field(..., description="Pipe diameter in millimeters")


class HydraulicCalculationResult(BaseModel):
    """Result of hydraulic calculations."""
    total_flow_lph: float = Field(..., description="Total flow rate in liters per hour")
    total_pressure_loss_bar: float = Field(..., description="Total pressure loss in bar")
    final_pressure_bar: float = Field(..., description="Final pressure in bar")
    velocity_ms: float = Field(..., description="Flow velocity in meters per second")
    reynolds_number: float = Field(..., description="Reynolds number")
    friction_factor: float = Field(..., description="Friction factor")
    warnings: List[str] = Field(default_factory=list, description="Calculation warnings")
    is_system_viable: bool = Field(..., description="Whether the system is viable")


class EquipmentSelectionInput(BaseModel):
    """Input for equipment selection."""
    zone_area_m2: float = Field(..., description="Zone area in square meters")
    water_needs: str = Field(..., description="Water needs (low, moderate, high)")
    budget_constraint: Optional[float] = Field(None, description="Budget constraint in USD")
    preferred_equipment_type: Optional[EquipmentType] = Field(None, description="Preferred equipment type")


class EquipmentSelectionResult(BaseModel):
    """Result of equipment selection."""
    recommended_equipment: IrrigationEquipment
    quantity_needed: int = Field(..., description="Quantity of equipment needed")
    total_cost: float = Field(..., description="Total cost in USD")
    coverage_efficiency: float = Field(..., description="Coverage efficiency percentage")
    justification: str = Field(..., description="Selection justification")


class ClusteringInput(BaseModel):
    """Input for plant clustering."""
    plants: List[Dict[str, Any]] = Field(..., description="List of plants with coordinates and water needs")
    max_zones: int = Field(..., description="Maximum number of zones")
    min_plants_per_zone: int = Field(default=1, description="Minimum plants per zone")


class ClusteringResult(BaseModel):
    """Result of plant clustering."""
    zones: List[IrrigationZone]
    cluster_centers: List[Dict[str, float]] = Field(..., description="Cluster center coordinates")
    total_cost: float = Field(..., description="Total estimated cost")
    efficiency_score: float = Field(..., description="Clustering efficiency score")


class WeatherForecastInput(BaseModel):
    """Input for weather forecast integration."""
    garden_id: UUID = Field(..., description="Garden ID")
    days_ahead: int = Field(default=7, description="Number of days to forecast")
    location: Optional[str] = Field(None, description="Location for weather data")


class WeatherForecastResult(BaseModel):
    """Result of weather forecast."""
    forecast_data: List[WeatherData] = Field(..., description="Weather forecast data")
    irrigation_recommendations: List[Dict[str, Any]] = Field(..., description="Irrigation recommendations")
    water_savings_potential: float = Field(..., description="Potential water savings in liters")


class CostEstimationInput(BaseModel):
    """Input for cost estimation."""
    zones: List[IrrigationZone]
    equipment_selections: List[EquipmentSelectionResult]
    pipe_network: List[IrrigationPipe]
    installation_complexity: str = Field(..., description="Installation complexity (simple, moderate, complex)")


class CostEstimationResult(BaseModel):
    """Result of cost estimation."""
    equipment_cost: float = Field(..., description="Equipment cost in USD")
    pipe_cost: float = Field(..., description="Pipe cost in USD")
    installation_cost: float = Field(..., description="Installation cost in USD")
    total_cost: float = Field(..., description="Total cost in USD")
    cost_breakdown: Dict[str, float] = Field(..., description="Detailed cost breakdown")
    roi_estimate: float = Field(..., description="Return on investment estimate")


# Legacy schemas for backward compatibility
class PlantLocation(BaseModel):
    """Represents a plant and its location, used for irrigation planning."""
    plant_id: int
    water_needs: str = Field(json_schema_extra={"example": "Moderate"})  # Low, Moderate, High
    x: float
    y: float


class ZoneInput(BaseModel):
    """Input for calculating watering zones."""
    plants: List[PlantLocation]


class WateringZone(BaseModel):
    """Represents a single watering zone with a list of plant IDs."""
    zone_id: int
    water_needs: str
    plant_ids: List[int]


class ZoneOutput(BaseModel):
    """Output of the watering zone calculation."""
    zones: List[WateringZone]


class FlowInput(BaseModel):
    """Input for calculating flow and pressure."""
    zones: List[WateringZone]
    pipe_diameter_mm: float = Field(json_schema_extra={"example": 16.0})
    source_pressure_bar: float = Field(json_schema_extra={"example": 2.5})


class FlowOutput(BaseModel):
    """Output of the flow and pressure calculation."""
    required_flow_lph: float = Field(json_schema_extra={"example": 450.5})  # Liters per hour
    pressure_at_end_bar: float = Field(json_schema_extra={"example": 1.8})
    warnings: List[str] = []
