import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from ..models.plant import SunPreference, PlantStatus, CompanionType

# --- PlantCatalog Schemas ---

class PlantCatalogBase(BaseModel):
    species_name: str = Field(..., max_length=255, example="Solanum lycopersicum")
    common_name: str | None = Field(None, max_length=255, example="Tomato")
    description: str | None = Field(None, example="A popular garden vegetable.")
    space_m2: float = Field(..., gt=0, example=0.5)
    sun_preference: SunPreference = Field(..., example=SunPreference.full_sun)
    water_liters_per_week: float = Field(..., gt=0, example=25.0)
    rich_metadata: dict | None = Field(None, example={"family": "Solanaceae", "harvest_days": 70})

class PlantCatalogCreate(PlantCatalogBase):
    pass

class PlantCatalogUpdate(BaseModel):
    species_name: str | None = Field(None, max_length=255)
    common_name: str | None = Field(None, max_length=255)
    description: str | None = Field(None)
    space_m2: float | None = Field(None, gt=0)
    sun_preference: SunPreference | None = Field(None)
    water_liters_per_week: float | None = Field(None, gt=0)
    rich_metadata: dict | None = Field(None)

class PlantCatalog(PlantCatalogBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- PlantInstance Schemas ---

class PlantInstanceBase(BaseModel):
    project_id: uuid.UUID
    catalog_id: uuid.UUID
    x_coord: int = Field(..., ge=0)
    y_coord: int = Field(..., ge=0)
    status: PlantStatus = Field(default=PlantStatus.planning)
    is_manual_placement: bool = Field(default=False)
    irrigation_zone_id: uuid.UUID | None = None

class PlantInstanceCreate(PlantInstanceBase):
    pass

class PlantInstanceUpdate(BaseModel):
    x_coord: int | None = Field(None, ge=0)
    y_coord: int | None = Field(None, ge=0)
    status: PlantStatus | None = Field(None)
    is_manual_placement: bool | None = Field(None)
    irrigation_zone_id: uuid.UUID | None = Field(None)

class PlantInstance(PlantInstanceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- CompanionRule Schemas ---

class CompanionRuleBase(BaseModel):
    source_plant_id: uuid.UUID
    target_plant_id: uuid.UUID
    relationship_type: CompanionType

class CompanionRuleCreate(CompanionRuleBase):
    pass

class CompanionRule(CompanionRuleBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
