from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .plant import Plant
    from .project import Project
    from .irrigation import IrrigationZone, IrrigationProject, WeatherData


class Garden(Base):
    """Garden model."""
    __tablename__ = 'gardens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="gardens")
    project: Mapped["Project | None"] = relationship(back_populates="gardens")
    plants: Mapped[list["Plant"]] = relationship("Plant", back_populates="garden", cascade="all, delete-orphan")

    # Irrigation relationships
    irrigation_zones: Mapped[list["IrrigationZone"]] = relationship("IrrigationZone", back_populates="garden",
                                                                    cascade="all, delete-orphan")
    irrigation_projects: Mapped[list["IrrigationProject"]] = relationship("IrrigationProject", back_populates="garden",
                                                                          cascade="all, delete-orphan")
    weather_data: Mapped[list["WeatherData"]] = relationship("WeatherData", back_populates="garden",
                                                             cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Garden(id={self.id}, name='{self.name}')>"
