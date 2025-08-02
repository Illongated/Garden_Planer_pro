from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .plant import Plant

class Garden(Base):
    """Garden model."""
    __tablename__ = 'gardens'

    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="gardens")
    plants: Mapped[list["Plant"]] = relationship("Plant", back_populates="garden", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Garden(id={self.id}, name='{self.name}')>"
