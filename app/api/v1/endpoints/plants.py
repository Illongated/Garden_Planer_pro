from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from db.session import get_db
from models import User, Plant
from schemas import PlantCreate, PlantUpdate, Plant as PlantSchema
from crud import plant as crud_plant
from crud import garden as crud_garden
from api.deps import get_current_active_user

router = APIRouter()

@router.post("/", response_model=PlantSchema, status_code=status.HTTP_201_CREATED)
async def create_plant(
    *,
    db: AsyncSession = Depends(get_db),
    plant_in: PlantCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new plant in a garden owned by the current user.
    """
    garden = await crud_garden.get(db=db, id=plant_in.garden_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    if garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this garden")

    plant = await crud_plant.create(db=db, obj_in=plant_in)
    return plant

@router.get("/{plant_id}", response_model=PlantSchema)
async def read_plant(
    *,
    db: AsyncSession = Depends(get_db),
    plant_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific plant by ID.
    """
    plant = await crud_plant.get_with_garden(db=db, id=plant_id)
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    if not plant.garden or plant.garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return plant

@router.get("/by_garden/{garden_id}", response_model=list[PlantSchema])
async def read_plants_by_garden(
    *,
    db: AsyncSession = Depends(get_db),
    garden_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all plants for a specific garden.
    """
    garden = await crud_garden.get(db=db, id=garden_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    if garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    plants = await crud_plant.get_multi_by_garden(db=db, garden_id=garden_id, skip=skip, limit=limit)
    return plants

@router.put("/{plant_id}", response_model=PlantSchema)
async def update_plant(
    *,
    db: AsyncSession = Depends(get_db),
    plant_id: uuid.UUID,
    plant_in: PlantUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a plant.
    """
    plant = await crud_plant.get_with_garden(db=db, id=plant_id)
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    if not plant.garden or plant.garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    plant = await crud_plant.update(db=db, db_obj=plant, obj_in=plant_in)
    return plant

@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    *,
    db: AsyncSession = Depends(get_db),
    plant_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a plant.
    """
    plant = await crud_plant.get_with_garden(db=db, id=plant_id)
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    if not plant.garden or plant.garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    await crud_plant.remove(db=db, id=plant_id)
    return
