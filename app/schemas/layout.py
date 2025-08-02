from pydantic import BaseModel, Field
from typing import List, Dict

class PlantPosition(BaseModel):
    """
    Represents a single plant's position in the garden layout.
    """
    plant_id: int = Field(json_schema_extra={"example": 1})
    x: float = Field(json_schema_extra={"example": 10.5})
    y: float = Field(json_schema_extra={"example": 20.0})

class LayoutInput(BaseModel):
    """
    Input schema for the layout optimizer.
    """
    garden_width: float = Field(json_schema_extra={"example": 100.0})
    garden_length: float = Field(json_schema_extra={"example": 200.0})
    plants: List[PlantPosition]

class LayoutOutput(BaseModel):
    """
    Output schema from the layout optimizer.
    """
    optimized_layout: List[PlantPosition]
    warnings: List[str] = Field(default_factory=list, json_schema_extra={"example": ["Tomato and Cabbage are too close."]})
