from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from crud.base import CRUDBase
from models.plant_catalog import PlantCatalog
from schemas.plant_catalog import PlantCatalogCreate, PlantCatalog as PlantCatalogSchema

class CRUDPlantCatalog(CRUDBase[PlantCatalog, PlantCatalogCreate, PlantCatalogSchema]):
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        q: Optional[str] = None,
        plant_type: Optional[str] = None,
        season: Optional[str] = None,
        sun: Optional[str] = None
    ):
        query = db.query(self.model)

        if q:
            query = query.filter(
                func.lower(self.model.name).contains(q.lower()) |
                func.lower(self.model.variety).contains(q.lower()) |
                func.lower(self.model.description).contains(q.lower())
            )

        if plant_type:
            query = query.filter(func.lower(self.model.plant_type) == plant_type.lower())

        if season:
            query = query.filter(self.model.planting_season.any(season))

        if sun:
            sun_str = sun.replace('-', ' ').lower()
            query = query.filter(func.lower(self.model.sun) == sun_str)

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return items, total

    def get_plant_types(self, db: Session):
        return db.query(self.model.plant_type).distinct().all()

    def get_planting_seasons(self, db: Session):
        # This is a bit more complex as it's an array.
        # A simple distinct on the array column might not be what we want.
        # Let's get all plants and extract seasons in Python.
        # This is not super efficient for large datasets, but for a few hundred plants it's fine.
        all_seasons = set()
        plants = db.query(self.model.planting_season).all()
        for plant_seasons in plants:
            if plant_seasons[0]:
                for season in plant_seasons[0]:
                    all_seasons.add(season)
        return sorted(list(all_seasons))


plant_catalog = CRUDPlantCatalog(PlantCatalog)
