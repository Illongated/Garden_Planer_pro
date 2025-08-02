import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- Base Project Schemas ---
from pydantic import ConfigDict

class ProjectBase(BaseModel):
    """
    Base schema for project data.
    """
    name: str = Field(json_schema_extra={"example": "My Vegetable Garden"})
    description: str | None = Field(default=None, json_schema_extra={"example": "A small garden for herbs and vegetables."})

# --- Schemas for API Operations ---
class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.
    """
    pass

class ProjectUpdate(BaseModel):
    """
    Schema for updating a project. All fields are optional.
    """
    name: str | None = Field(default=None, json_schema_extra={"example": "My Updated Vegetable Garden"})
    description: str | None = Field(default=None, json_schema_extra={"example": "An updated description."})
    layout: Dict[str, Any] | None = Field(default=None, json_schema_extra={"example": {"plant_1": {"x": 10, "y": 20}}})

# --- Schema for API Responses ---
class Project(ProjectBase):
    """
    Schema for returning a project to the client.
    """
    id: uuid.UUID
    owner_id: uuid.UUID
    layout: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
