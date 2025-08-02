from pydantic import BaseModel, Field
from typing import List, Dict

class PlantLocation(BaseModel):
    """
    Represents a plant and its location, used for irrigation planning.
    """
    plant_id: int
    water_needs: str = Field(json_schema_extra={"example": "Moderate"}) # Low, Moderate, High
    x: float
    y: float

class ZoneInput(BaseModel):
    """
    Input for calculating watering zones.
    """
    plants: List[PlantLocation]

class WateringZone(BaseModel):
    """
    Represents a single watering zone with a list of plant IDs.
    """
    zone_id: int
    water_needs: str
    plant_ids: List[int]

class ZoneOutput(BaseModel):
    """
    Output of the watering zone calculation.
    """
    zones: List[WateringZone]

class FlowInput(BaseModel):
    """
    Input for calculating flow and pressure.
    """
    zones: List[WateringZone]
    pipe_diameter_mm: float = Field(json_schema_extra={"example": 16.0})
    source_pressure_bar: float = Field(json_schema_extra={"example": 2.5})

class FlowOutput(BaseModel):
    """
    Output of the flow and pressure calculation.
    """
    required_flow_lph: float = Field(json_schema_extra={"example": 450.5}) # Liters per hour
    pressure_at_end_bar: float = Field(json_schema_extra={"example": 1.8})
    warnings: List[str] = []
