from sqlalchemy import (
    Column,
    String,
    Float,
    JSON,
    ForeignKey,
    Enum,
    Integer,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .base import BaseModel, UUID
import enum

# --- Enums for categorical data ---

class SunPreference(str, enum.Enum):
    full_sun = "full_sun"
    partial_shade = "partial_shade"
    full_shade = "full_shade"

class PlantStatus(str, enum.Enum):
    planning = "planning"
    planted = "planted"
    growing = "growing"
    harvested = "harvested"
    inactive = "inactive"

class CompanionType(str, enum.Enum):
    friend = "friend"
    enemy = "enemy"
    neutral = "neutral"

# --- Models ---

class PlantCatalog(BaseModel):
    """
    Static catalog of all available plant species and their characteristics.
    """
    __tablename__ = "plant_catalog"

    species_name = Column(String(255), unique=True, index=True, nullable=False)
    common_name = Column(String(255), nullable=True)
    description = Column(String, nullable=True)

    # Growing conditions
    space_m2 = Column(Float, nullable=False) # Area required per plant
    sun_preference = Column(Enum(SunPreference), nullable=False)

    # Water needs
    water_liters_per_week = Column(Float, nullable=False)

    # Rich metadata
    rich_metadata = Column(JSON, nullable=True) # e.g., soil type, harvest time, etc.

    def __repr__(self):
        return f"<PlantCatalog(id={self.id}, species_name='{self.species_name}')>"


class PlantInstance(BaseModel):
    """
    An instance of a plant from the catalog, placed within a specific garden project.
    """
    __tablename__ = "plant_instances"

    project_id = Column(UUID(as_uuid=True), ForeignKey("garden_projects.id"), nullable=False, index=True)
    catalog_id = Column(UUID(as_uuid=True), ForeignKey("plant_catalog.id"), nullable=False, index=True)

    # Position in the garden grid (in decimeters, as per original logic)
    x_coord = Column(Integer, nullable=False)
    y_coord = Column(Integer, nullable=False)

    status = Column(Enum(PlantStatus), default=PlantStatus.planning, nullable=False)
    is_manual_placement = Column(Boolean, default=False, nullable=False)

    # Relationships
    project = relationship("GardenProject", back_populates="plant_instances")
    catalog_entry = relationship("PlantCatalog")
    irrigation_zone_id = Column(UUID(as_uuid=True), ForeignKey("irrigation_zones.id"), nullable=True)
    irrigation_zone = relationship("IrrigationZone", back_populates="plant_instances")

    # History of changes can be tracked via the AuditLog table

    def __repr__(self):
        return f"<PlantInstance(id={self.id}, project_id='{self.project_id}')>"


class CompanionRule(BaseModel):
    """
    Defines a companion relationship (friend or enemy) between two plant species.
    This is a directional link from 'source' to 'target'.
    """
    __tablename__ = "companion_rules"

    source_plant_id = Column(UUID(as_uuid=True), ForeignKey("plant_catalog.id"), nullable=False, index=True)
    target_plant_id = Column(UUID(as_uuid=True), ForeignKey("plant_catalog.id"), nullable=False, index=True)

    relationship_type = Column(Enum(CompanionType), nullable=False)

    # Ensure a pair of plants can only have one type of relationship defined
    __table_args__ = (
        UniqueConstraint("source_plant_id", "target_plant_id", name="uq_companion_rule_pair"),
    )

    source_plant = relationship("PlantCatalog", foreign_keys=[source_plant_id])
    target_plant = relationship("PlantCatalog", foreign_keys=[target_plant_id])

    def __repr__(self):
        return f"<CompanionRule({self.source_plant_id} -> {self.target_plant_id}: {self.relationship_type})>"
