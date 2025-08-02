from sqlalchemy import Column, Integer, String, Text, ARRAY
from app.models.base import Base

class PlantCatalog(Base):
    """
    Represents a type of plant in the global catalog.
    This is static data, not a user's specific plant instance.
    """
    __tablename__ = "plant_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    variety = Column(String)
    plant_type = Column(String, index=True)
    image = Column(String)
    description = Column(Text)
    sun = Column(String)
    water = Column(String)
    spacing = Column(String)
    planting_season = Column(ARRAY(String))
    harvest_season = Column(ARRAY(String))
    compatibility = Column(ARRAY(String))
    tips = Column(Text)

    def __repr__(self):
        return f"<PlantCatalog(id={self.id}, name='{self.name}')>"
