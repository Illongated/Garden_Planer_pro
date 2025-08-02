from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, UUID

class IrrigationZone(BaseModel):
    """
    Represents an irrigation zone within a garden project, grouping plants
    with similar water requirements.
    """
    __tablename__ = "irrigation_zones"

    name = Column(String(255), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("garden_projects.id"), nullable=False, index=True)

    # Store technical details like pipe layout, valve info, etc.
    settings = Column(JSON, nullable=True)

    project = relationship("GardenProject", back_populates="irrigation_zones")
    plant_instances = relationship("PlantInstance", back_populates="irrigation_zone")

    def __repr__(self):
        return f"<IrrigationZone(id={self.id}, name='{self.name}')>"
