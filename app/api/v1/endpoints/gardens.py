from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.models import User, Garden
from app.schemas import GardenCreate, GardenUpdate, GardenWithPlants, Garden as GardenSchema
from app.crud import garden as crud_garden
from app.api.deps import get_current_active_user

router = APIRouter()

@router.post("/", response_model=GardenSchema, status_code=status.HTTP_201_CREATED)
async def create_garden(
    *,
    db: AsyncSession = Depends(get_db),
    garden_in: GardenCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new garden for the current user.
    """
    garden = await crud_garden.create_with_owner(db=db, obj_in=garden_in, owner_id=current_user.id)
    return garden

@router.get("/", response_model=list[GardenSchema])
async def read_gardens(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all gardens for the current user.
    """
    gardens = await crud_garden.get_multi_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return gardens

@router.get("/{garden_id}", response_model=GardenWithPlants)
async def read_garden(
    *,
    db: AsyncSession = Depends(get_db),
    garden_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific garden by ID, including its plants.
    """
    garden = await crud_garden.get(db=db, id=garden_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    if garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return garden

@router.put("/{garden_id}", response_model=GardenSchema)
async def update_garden(
    *,
    db: AsyncSession = Depends(get_db),
    garden_id: uuid.UUID,
    garden_in: GardenUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a garden.
    """
    garden = await crud_garden.get(db=db, id=garden_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    if garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    garden = await crud_garden.update(db=db, db_obj=garden, obj_in=garden_in)
    return garden

@router.delete("/{garden_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_garden(
    *,
    db: AsyncSession = Depends(get_db),
    garden_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a garden.
    """
    garden = await crud_garden.get(db=db, id=garden_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    if garden.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    await crud_garden.remove(db=db, id=garden_id)
    return
