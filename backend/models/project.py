from sqlalchemy import Column, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, UUID

class GardenProject(BaseModel):
    """
    Represents a single garden project owned by a user.
    """
    __tablename__ = "garden_projects"

    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True) # e.g., "Backyard", "Balcony"

    # Garden dimensions in meters
    width_m = Column(Float, nullable=False)
    depth_m = Column(Float, nullable=False)

    # Environmental settings
    sun_angle_deg = Column(Float, default=180.0)

    # Store settings or metadata as a flexible JSON blob
    settings = Column(JSON, nullable=True)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")

    plant_instances = relationship("PlantInstance", back_populates="project", cascade="all, delete-orphan")
    irrigation_zones = relationship("IrrigationZone", back_populates="project", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="project")

    def __repr__(self):
        return f"<GardenProject(id={self.id}, name='{self.name}')>"
