from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class PlantCatalog(Base):
    """
    Represents a type of plant in the global catalog.
    This is static data, not a user's specific plant instance.
    """
    __tablename__ = "plant_catalog"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    variety: Mapped[str | None] = mapped_column(String, nullable=True)
    plant_type: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    image: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sun: Mapped[str | None] = mapped_column(String, nullable=True)
    water: Mapped[str | None] = mapped_column(String, nullable=True)
    spacing: Mapped[str | None] = mapped_column(String, nullable=True)
    planting_season: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    harvest_season: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    compatibility: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<PlantCatalog(id={self.id}, name='{self.name}')>"
