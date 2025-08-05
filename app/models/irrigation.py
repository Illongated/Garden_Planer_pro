from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey,
    Integer, JSON, String, Text, Time, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class EquipmentType(str, Enum):
    """Types of irrigation equipment."""
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    MICROJET = "microjet"
    ROTOR = "rotor"
    SPRAY = "spray"


class PipeMaterial(str, Enum):
    """Types of pipe materials."""
    PVC = "pvc"
    PE = "pe"
    PEX = "pex"
    COPPER = "copper"


class ZoneStatus(str, Enum):
    """Status of irrigation zones."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class ScheduleType(str, Enum):
    """Types of irrigation schedules."""
    DAILY = "daily"
    WEEKLY = "weekly"
    WEATHER_BASED = "weather_based"
    MANUAL = "manual"


class IrrigationEquipment(Base):
    """Model for irrigation equipment (emitters, sprinklers, etc.)."""
    __tablename__ = "irrigation_equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    equipment_type: Mapped[EquipmentType] = mapped_column(SQLEnum(EquipmentType), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    flow_rate_lph: Mapped[float] = mapped_column(Float, nullable=False)  # Liters per hour
    pressure_range_min: Mapped[float] = mapped_column(Float, nullable=False)  # Bar
    pressure_range_max: Mapped[float] = mapped_column(Float, nullable=False)  # Bar
    coverage_radius_m: Mapped[float] = mapped_column(Float, nullable=False)  # Meters
    spacing_m: Mapped[float] = mapped_column(Float, nullable=False)  # Recommended spacing
    cost_per_unit: Mapped[Decimal] = mapped_column(Float, nullable=False)  # USD
    specifications: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    zone_equipment: Mapped[List["IrrigationZoneEquipment"]] = relationship(
        "IrrigationZoneEquipment", back_populates="equipment", cascade="all, delete-orphan"
    )


class IrrigationZone(Base):
    """Model for irrigation zones."""
    __tablename__ = "irrigation_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    garden_id: Mapped[int] = mapped_column(ForeignKey("gardens.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ZoneStatus] = mapped_column(SQLEnum(ZoneStatus), default=ZoneStatus.ACTIVE, nullable=False)

    # Hydraulic properties
    required_flow_lph: Mapped[float] = mapped_column(Float, nullable=False)
    operating_pressure_bar: Mapped[float] = mapped_column(Float, nullable=False)
    total_area_m2: Mapped[float] = mapped_column(Float, nullable=False)

    # Clustering data
    cluster_center_x: Mapped[float] = mapped_column(Float, nullable=False)
    cluster_center_y: Mapped[float] = mapped_column(Float, nullable=False)
    plant_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)

    # Cost estimation
    estimated_cost: Mapped[Decimal] = mapped_column(Float, nullable=True)

    # Relationships
    garden: Mapped["Garden"] = relationship("Garden", back_populates="irrigation_zones")
    equipment: Mapped[List["IrrigationZoneEquipment"]] = relationship(
        "IrrigationZoneEquipment", back_populates="zone", cascade="all, delete-orphan"
    )
    pipes: Mapped[List["IrrigationPipe"]] = relationship(
        "IrrigationPipe", back_populates="zone", cascade="all, delete-orphan"
    )
    schedules: Mapped[List["IrrigationSchedule"]] = relationship(
        "IrrigationSchedule", back_populates="zone", cascade="all, delete-orphan"
    )


class IrrigationZoneEquipment(Base):
    """Junction table for zone equipment assignments."""
    __tablename__ = "irrigation_zone_equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("irrigation_zones.id"), nullable=False)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("irrigation_equipment.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    spacing_m: Mapped[float] = mapped_column(Float, nullable=False)
    layout_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)  # Position data

    # Relationships
    zone: Mapped["IrrigationZone"] = relationship("IrrigationZone", back_populates="equipment")
    equipment: Mapped["IrrigationEquipment"] = relationship("IrrigationEquipment", back_populates="zone_equipment")


class IrrigationPipe(Base):
    """Model for irrigation pipe network."""
    __tablename__ = "irrigation_pipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("irrigation_zones.id"), nullable=False)
    pipe_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pipe_type: Mapped[str] = mapped_column(String(50), nullable=False)  # main, lateral, sub-lateral
    material: Mapped[PipeMaterial] = mapped_column(SQLEnum(PipeMaterial), nullable=False)
    diameter_mm: Mapped[float] = mapped_column(Float, nullable=False)
    length_m: Mapped[float] = mapped_column(Float, nullable=False)

    # Hydraulic properties
    flow_rate_lph: Mapped[float] = mapped_column(Float, nullable=False)
    velocity_ms: Mapped[float] = mapped_column(Float, nullable=False)  # Meters per second
    pressure_loss_bar: Mapped[float] = mapped_column(Float, nullable=False)

    # Geometry
    start_x: Mapped[float] = mapped_column(Float, nullable=False)
    start_y: Mapped[float] = mapped_column(Float, nullable=False)
    end_x: Mapped[float] = mapped_column(Float, nullable=False)
    end_y: Mapped[float] = mapped_column(Float, nullable=False)

    # Cost
    cost_per_meter: Mapped[Decimal] = mapped_column(Float, nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Float, nullable=False)

    # Relationships
    zone: Mapped["IrrigationZone"] = relationship("IrrigationZone", back_populates="pipes")


class IrrigationSchedule(Base):
    """Model for irrigation schedules."""
    __tablename__ = "irrigation_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("irrigation_zones.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    schedule_type: Mapped[ScheduleType] = mapped_column(SQLEnum(ScheduleType), nullable=False)

    # Timing
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Frequency
    days_of_week: Mapped[List[int]] = mapped_column(JSON, nullable=True)  # 0=Monday, 6=Sunday
    interval_days: Mapped[int] = mapped_column(Integer, nullable=True)

    # Weather-based settings
    min_temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_humidity_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_humidity_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_rainfall_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Advanced settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    zone: Mapped["IrrigationZone"] = relationship("IrrigationZone", back_populates="schedules")


class WeatherData(Base):
    """Model for weather data from external APIs."""
    __tablename__ = "weather_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    garden_id: Mapped[int] = mapped_column(ForeignKey("gardens.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Weather parameters
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_percent: Mapped[float] = mapped_column(Float, nullable=False)
    rainfall_mm: Mapped[float] = mapped_column(Float, nullable=False)
    wind_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    solar_radiation_mj_m2: Mapped[float] = mapped_column(Float, nullable=False)

    # Calculated values
    evapotranspiration_mm: Mapped[float] = mapped_column(Float, nullable=False)
    irrigation_need_mm: Mapped[float] = mapped_column(Float, nullable=False)

    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # API provider
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

    # Relationships
    garden: Mapped["Garden"] = relationship("Garden", back_populates="weather_data")

    # Constraints
    __table_args__ = (
        UniqueConstraint('garden_id', 'date', name='uq_weather_garden_date'),
    )


class IrrigationProject(Base):
    """Model for irrigation design projects."""
    __tablename__ = "irrigation_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    garden_id: Mapped[int] = mapped_column(ForeignKey("gardens.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Design parameters
    water_source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # tap, well, tank
    source_pressure_bar: Mapped[float] = mapped_column(Float, nullable=False)
    source_flow_lph: Mapped[float] = mapped_column(Float, nullable=False)

    # Cost estimation
    total_equipment_cost: Mapped[Decimal] = mapped_column(Float, nullable=True)
    total_pipe_cost: Mapped[Decimal] = mapped_column(Float, nullable=True)
    total_installation_cost: Mapped[Decimal] = mapped_column(Float, nullable=True)
    total_project_cost: Mapped[Decimal] = mapped_column(Float, nullable=True)

    # Design data
    hydraulic_calculations: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    network_layout: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    equipment_selection: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    garden: Mapped["Garden"] = relationship("Garden", back_populates="irrigation_projects")
    zones: Mapped[List[IrrigationZone]] = relationship(
        "IrrigationZone", back_populates="garden", cascade="all, delete-orphan"
    )
