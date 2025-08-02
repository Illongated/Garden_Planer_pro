from pydantic import BaseModel, Field
import uuid
from datetime import datetime, date
from typing import Optional

# Base schema with fields common to create and update
class PlantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the plant")
    species: Optional[str] = Field(None, max_length=100, description="Scientific species name")
    planting_date: Optional[date] = Field(None, description="Date the plant was planted")
    notes: Optional[str] = Field(None, max_length=500, description="User notes for the plant")

# Schema for creating a new plant (requires garden_id)
class PlantCreate(PlantBase):
    garden_id: uuid.UUID = Field(..., description="The ID of the garden this plant belongs to")

# Schema for updating a plant (all fields are optional)
class PlantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[str] = Field(None, max_length=100)
    planting_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

# Base schema for data returned from the DB, includes all model fields
class PlantInDBBase(PlantBase):
    id: uuid.UUID
    garden_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Public schema for returning a plant to the client
class Plant(PlantInDBBase):
    pass
