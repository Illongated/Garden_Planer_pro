from pydantic import BaseModel, Field
from typing import List

from pydantic import ConfigDict

class Plant(BaseModel):
    """
    Schema for a plant in the catalogue.
    """
    id: int
    name: str = Field(json_schema_extra={"example": "Tomato"})
    scientific_name: str = Field(json_schema_extra={"example": "Solanum lycopersicum"})
    description: str
    sun_needs: str = Field(json_schema_extra={"example": "Full Sun"}) # e.g., "Full Sun", "Partial Shade", "Full Shade"
    water_needs: str = Field(json_schema_extra={"example": "Moderate"}) # e.g., "Low", "Moderate", "High"
    companion_plants: List[int] = Field(default_factory=list, json_schema_extra={"example": [2, 3]}) # List of plant IDs
    antagonist_plants: List[int] = Field(default_factory=list, json_schema_extra={"example": [4]}) # List of plant IDs

    model_config = ConfigDict(from_attributes=True)
