import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from .plant import PlantInstance
from .irrigation import IrrigationZone

# --- Base Schema ---

class GardenProjectBase(BaseModel):
    name: str = Field(..., max_length=255, example="My First Garden")
    description: str | None = Field(None, example="A small vegetable garden in the backyard.")
    location: str | None = Field(None, max_length=255, example="Backyard")
    width_m: float = Field(..., gt=0, example=5.0)
    depth_m: float = Field(..., gt=0, example=4.0)
    sun_angle_deg: float = Field(180.0, ge=0, le=360, example=180.0)
    settings: dict | None = Field(None, example={"soil_type": "loamy"})

# --- Schemas for API Operations ---

class GardenProjectCreate(GardenProjectBase):
    pass

class GardenProjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=255, example="My Updated Garden")
    description: str | None = Field(None)
    location: str | None = Field(None, max_length=255)
    width_m: float | None = Field(None, gt=0)
    depth_m: float | None = Field(None, gt=0)
    sun_angle_deg: float | None = Field(None, ge=0, le=360)
    settings: dict | None = Field(None)


# --- Public Schemas (for API responses) ---

class GardenProject(GardenProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GardenProjectDetail(GardenProject):
    """
    A full representation of a garden project, including its contents.
    """
    plant_instances: list[PlantInstance] = []
    irrigation_zones: list[IrrigationZone] = []
