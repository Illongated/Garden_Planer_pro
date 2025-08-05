from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Shared properties
class PlantCatalogBase(BaseModel):
    name: str
    variety: Optional[str] = None
    plant_type: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    sun: Optional[str] = None
    water: Optional[str] = None
    spacing: Optional[str] = None
    planting_season: Optional[List[str]] = []
    harvest_season: Optional[List[str]] = []
    compatibility: Optional[List[str]] = []
    tips: Optional[str] = None

# Properties to receive on item creation
class PlantCatalogCreate(PlantCatalogBase):
    pass

# Properties to return to client
class PlantCatalog(PlantCatalogBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Compatibilité Pydantic v2+

# Properties for paginated response
class PaginatedPlantCatalog(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PlantCatalog]
