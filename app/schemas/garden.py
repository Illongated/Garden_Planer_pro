from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

# --- Base ---
class GardenBase(BaseModel):
    name: str
    location: Optional[str] = None

# --- Create ---
class GardenCreate(GardenBase):
    pass

# --- Update ---
class GardenUpdate(GardenBase):
    name: Optional[str] = None # All fields optional for update

# --- InDB ---
class GardenInDBBase(GardenBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Public ---
class Garden(GardenInDBBase):
    pass

from .plant import Plant # Import here to avoid circular dependency issues

class GardenWithPlants(Garden):
    """
    Extends Garden to include a list of its plants.
    """
    plants: list[Plant] = []
