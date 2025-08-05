from sqlalchemy import String, ForeignKey, Integer, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .garden import Garden

class Plant(Base):
    """Plant model."""
    __tablename__ = 'plants'

    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    species: Mapped[str | None] = mapped_column(String, nullable=True)
    planting_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    garden_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("gardens.id"), index=True)

    # Relationships
    garden: Mapped["Garden"] = relationship("Garden", back_populates="plants")

    def __repr__(self):
        return f"<Plant(id={self.id}, name='{self.name}')>"
