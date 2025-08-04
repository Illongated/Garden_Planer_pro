# This file makes the 'models' directory a Python package.
# It also helps Alembic discover the models.

from .base import Base
from .user import User
from .garden import Garden
from .plant import Plant
from .plant_catalog import PlantCatalog
from .project import Project, ProjectMember, ProjectVersion, ProjectComment, ProjectActivity, ProjectPermission, ProjectStatus
from .project_management import (
    PMProject, Task, Bug, ProjectCollaborator, ProjectMetrics, 
    UserActivity, Feedback, Release, CodeReview, ProjectStatus as PMProjectStatus,
    TaskStatus, TaskPriority, BugSeverity
)
from .irrigation import (
    IrrigationEquipment, IrrigationZone, IrrigationZoneEquipment, IrrigationPipe,
    IrrigationSchedule, WeatherData, IrrigationProject, EquipmentType, PipeMaterial,
    ZoneStatus, ScheduleType
)

__all__ = [
    "Base",
    "User", 
    "Garden",
    "Plant",
    "PlantCatalog",
    "Project",
    "ProjectMember", 
    "ProjectVersion",
    "ProjectComment",
    "ProjectActivity",
    "ProjectPermission",
    "ProjectStatus",
    # Project Management models
    "PMProject",
    "Task",
    "Bug", 
    "ProjectCollaborator",
    "ProjectMetrics",
    "UserActivity",
    "Feedback",
    "Release",
    "CodeReview",
    "PMProjectStatus",
    "TaskStatus",
    "TaskPriority",
    "BugSeverity",
    "IrrigationEquipment",
    "IrrigationZone",
    "IrrigationZoneEquipment", 
    "IrrigationPipe",
    "IrrigationSchedule",
    "WeatherData",
    "IrrigationProject",
    "EquipmentType",
    "PipeMaterial",
    "ZoneStatus",
    "ScheduleType"
]
