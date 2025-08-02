import uuid
from pydantic import BaseModel, Field
from datetime import datetime

# --- Base Schema ---

class IrrigationZoneBase(BaseModel):
    name: str = Field(..., max_length=255, example="High-Water Zone")
    project_id: uuid.UUID
    settings: dict | None = Field(None, example={"valve_type": "automatic", "schedule": "daily"})

# --- Schemas for API Operations ---

class IrrigationZoneCreate(IrrigationZoneBase):
    pass

class IrrigationZoneUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    settings: dict | None = Field(None)

# --- Public Schema (for API responses) ---

class IrrigationZone(IrrigationZoneBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
