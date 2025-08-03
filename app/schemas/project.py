import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

# --- Enums ---
class ProjectPermission(str, Enum):
    """Project permission levels."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class ProjectStatus(str, Enum):
    """Project status."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

# --- Base Project Schemas ---
class ProjectBase(BaseModel):
    """Base schema for project data."""
    name: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "My Vegetable Garden"})
    description: Optional[str] = Field(default=None, json_schema_extra={"example": "A small garden for herbs and vegetables."})
    location: Optional[str] = Field(default=None, max_length=500, json_schema_extra={"example": "Backyard, Zone 5"})
    climate_zone: Optional[str] = Field(default=None, max_length=50, json_schema_extra={"example": "5b"})
    soil_type: Optional[str] = Field(default=None, max_length=100, json_schema_extra={"example": "Loamy soil"})
    garden_size: Optional[float] = Field(default=None, gt=0, json_schema_extra={"example": 25.5})

class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    is_public: bool = Field(default=False, json_schema_extra={"example": False})
    allow_comments: bool = Field(default=True, json_schema_extra={"example": True})
    allow_forking: bool = Field(default=True, json_schema_extra={"example": True})

class ProjectUpdate(BaseModel):
    """Schema for updating a project. All fields are optional."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=500)
    climate_zone: Optional[str] = Field(default=None, max_length=50)
    soil_type: Optional[str] = Field(default=None, max_length=100)
    garden_size: Optional[float] = Field(default=None, gt=0)
    status: Optional[ProjectStatus] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)
    allow_comments: Optional[bool] = Field(default=None)
    allow_forking: Optional[bool] = Field(default=None)
    layout_data: Optional[Dict[str, Any]] = Field(default=None)
    plant_data: Optional[Dict[str, Any]] = Field(default=None)
    irrigation_data: Optional[Dict[str, Any]] = Field(default=None)

# --- Project Member Schemas ---
class ProjectMemberBase(BaseModel):
    """Base schema for project member data."""
    permission: ProjectPermission = Field(default=ProjectPermission.VIEWER)

class ProjectMemberCreate(ProjectMemberBase):
    """Schema for adding a member to a project."""
    user_email: str = Field(..., json_schema_extra={"example": "user@example.com"})

class ProjectMemberUpdate(BaseModel):
    """Schema for updating project member permissions."""
    permission: ProjectPermission

class ProjectMember(ProjectMemberBase):
    """Schema for project member response."""
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    user_email: str
    user_full_name: Optional[str]
    invited_by: Optional[uuid.UUID]
    invited_at: Optional[datetime]
    accepted_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# --- Project Version Schemas ---
class ProjectVersionBase(BaseModel):
    """Base schema for project version data."""
    name: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "Initial Layout"})
    description: Optional[str] = Field(default=None, json_schema_extra={"example": "First version with basic layout"})

class ProjectVersionCreate(ProjectVersionBase):
    """Schema for creating a new project version."""
    layout_data: Optional[Dict[str, Any]] = Field(default=None)
    plant_data: Optional[Dict[str, Any]] = Field(default=None)
    irrigation_data: Optional[Dict[str, Any]] = Field(default=None)
    is_tagged: bool = Field(default=False)
    tag_name: Optional[str] = Field(default=None, max_length=100)

class ProjectVersion(ProjectVersionBase):
    """Schema for project version response."""
    id: uuid.UUID
    project_id: uuid.UUID
    version_number: int
    created_by: uuid.UUID
    creator_name: str
    layout_data: Optional[Dict[str, Any]]
    plant_data: Optional[Dict[str, Any]]
    irrigation_data: Optional[Dict[str, Any]]
    is_tagged: bool
    tag_name: Optional[str]
    parent_version_id: Optional[uuid.UUID]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Project Comment Schemas ---
class ProjectCommentBase(BaseModel):
    """Base schema for project comment data."""
    content: str = Field(..., min_length=1, json_schema_extra={"example": "This layout looks great!"})
    position_x: Optional[float] = Field(default=None, json_schema_extra={"example": 100.5})
    position_y: Optional[float] = Field(default=None, json_schema_extra={"example": 200.0})
    element_id: Optional[str] = Field(default=None, max_length=100, json_schema_extra={"example": "plant_123"})

class ProjectCommentCreate(ProjectCommentBase):
    """Schema for creating a new project comment."""
    parent_comment_id: Optional[uuid.UUID] = Field(default=None)

class ProjectCommentUpdate(BaseModel):
    """Schema for updating a project comment."""
    content: str = Field(..., min_length=1)

class ProjectComment(ProjectCommentBase):
    """Schema for project comment response."""
    id: uuid.UUID
    project_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    parent_comment_id: Optional[uuid.UUID]
    is_resolved: bool
    resolved_by: Optional[uuid.UUID]
    resolved_at: Optional[datetime]
    replies_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Project Activity Schemas ---
class ProjectActivity(BaseModel):
    """Schema for project activity response."""
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    activity_type: str
    description: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Project Response Schemas ---
class Project(ProjectBase):
    """Schema for returning a project to the client."""
    id: uuid.UUID
    owner_id: uuid.UUID
    owner_name: str
    status: ProjectStatus
    layout_data: Dict[str, Any] = Field(default_factory=dict)
    plant_data: Dict[str, Any] = Field(default_factory=dict)
    irrigation_data: Dict[str, Any] = Field(default_factory=dict)
    current_version: int
    last_modified_by: Optional[uuid.UUID]
    last_modified_user_name: Optional[str]
    is_public: bool
    allow_comments: bool
    allow_forking: bool
    members_count: int
    comments_count: int
    versions_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectDetail(Project):
    """Detailed project schema with related data."""
    members: List[ProjectMember] = Field(default_factory=list)
    recent_versions: List[ProjectVersion] = Field(default_factory=list)
    recent_comments: List[ProjectComment] = Field(default_factory=list)
    recent_activities: List[ProjectActivity] = Field(default_factory=list)

# --- Project List Response ---
class ProjectList(BaseModel):
    """Schema for project list response."""
    projects: List[Project]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

# --- Project Export/Import Schemas ---
class ProjectExport(BaseModel):
    """Schema for project export data."""
    project: Project
    versions: List[ProjectVersion]
    comments: List[ProjectComment]
    activities: List[ProjectActivity]
    export_metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectImport(BaseModel):
    """Schema for project import data."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    layout_data: Optional[Dict[str, Any]] = Field(default=None)
    plant_data: Optional[Dict[str, Any]] = Field(default=None)
    irrigation_data: Optional[Dict[str, Any]] = Field(default=None)
    import_metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Project Search and Filter Schemas ---
class ProjectFilter(BaseModel):
    """Schema for project filtering."""
    status: Optional[ProjectStatus] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)
    owner_id: Optional[uuid.UUID] = Field(default=None)
    search: Optional[str] = Field(default=None, max_length=100)
    climate_zone: Optional[str] = Field(default=None)
    soil_type: Optional[str] = Field(default=None)
    created_after: Optional[datetime] = Field(default=None)
    created_before: Optional[datetime] = Field(default=None)

class ProjectSort(BaseModel):
    """Schema for project sorting."""
    field: str = Field(default="created_at", json_schema_extra={"example": "name"})
    direction: str = Field(default="desc", json_schema_extra={"example": "asc"})

# --- WebSocket Message Schemas ---
class ProjectWebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str = Field(..., json_schema_extra={"example": "project_updated"})
    project_id: uuid.UUID
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[uuid.UUID] = Field(default=None)
    user_name: Optional[str] = Field(default=None)

class ProjectCollaborationMessage(BaseModel):
    """Schema for real-time collaboration messages."""
    type: str = Field(..., json_schema_extra={"example": "user_joined"})
    project_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    data: Optional[Dict[str, Any]] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
