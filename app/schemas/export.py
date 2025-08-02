from pydantic import BaseModel, Field
from typing import Dict, Any

class ExportResponse(BaseModel):
    """
    A generic response model for export operations.
    """
    project_id: str
    format: str
    download_url: str | None = None
    message: str

class ProjectJSONExport(BaseModel):
    """
    The structure of the exported project data in JSON format.
    """
    project_details: Dict[str, Any]
    plant_catalogue_used: Dict[int, Any]
