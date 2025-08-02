from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud
from app.api import deps
from app.schemas.plant_catalog import PaginatedPlantCatalog, PlantCatalog

router = APIRouter()

@router.get("/", response_model=PaginatedPlantCatalog)
def read_plant_catalog(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    q: Optional[str] = Query(None, description="Full-text search query"),
    plant_type: Optional[str] = Query(None, description="Filter by plant type"),
    season: Optional[str] = Query(None, description="Filter by planting season"),
    sun: Optional[str] = Query(None, description="Filter by sun requirement"),
):
    """
    Retrieve plants from the catalog with pagination and filtering.
    """
    skip = (page - 1) * page_size
    plants, total = crud.plant_catalog.get_multi(
        db, skip=skip, limit=page_size, q=q, plant_type=plant_type, season=season, sun=sun
    )
    return PaginatedPlantCatalog(
        total=total,
        page=page,
        page_size=page_size,
        items=plants
    )

@router.get("/types", response_model=List[str])
def get_plant_types(db: Session = Depends(deps.get_db)):
    """
    Get a list of unique plant types.
    """
    types = crud.plant_catalog.get_plant_types(db)
    return [t[0] for t in types if t[0]]


@router.get("/seasons", response_model=List[str])
def get_planting_seasons(db: Session = Depends(deps.get_db)):
    """
    Get a list of unique planting seasons.
    """
    return crud.plant_catalog.get_planting_seasons(db)
