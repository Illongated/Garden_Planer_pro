from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List

from .... import crud, models, schemas
from ..deps import get_current_active_user
from ....db.session import get_db_session

router = APIRouter()

@router.get("/", response_model=List[schemas.GardenProject])
async def read_projects(
    db: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve garden projects for the current user.
    """
    projects = await crud.crud_project.get_projects_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return projects

@router.post("/", response_model=schemas.GardenProject)
async def create_project(
    *,
    db: AsyncSession = Depends(get_db_session),
    project_in: schemas.GardenProjectCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new garden project.
    """
    project = await crud.crud_project.create_project(
        db=db, project_in=project_in, owner_id=current_user.id
    )
    return project

@router.get("/{project_id}", response_model=schemas.GardenProjectDetail)
async def read_project(
    *,
    db: AsyncSession = Depends(get_db_session),
    project_id: str,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get project by ID.
    """
    project = await crud.crud_project.get_project_with_details(
        db=db, project_id=project_id, owner_id=current_user.id
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=schemas.GardenProject)
async def update_project(
    *,
    db: AsyncSession = Depends(get_db_session),
    project_id: str,
    project_in: schemas.GardenProjectUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a garden project.
    """
    project = await crud.crud_project.get_project(
        db=db, project_id=project_id, owner_id=current_user.id
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project = await crud.crud_project.update_project(
        db=db, db_project=project, project_in=project_in
    )
    return project

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    *,
    db: AsyncSession = Depends(get_db_session),
    project_id: str,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a garden project.
    """
    project = await crud.crud_project.get_project(
        db=db, project_id=project_id, owner_id=current_user.id
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await crud.crud_project.delete_project(db=db, db_project=project)
    return {"ok": True}
