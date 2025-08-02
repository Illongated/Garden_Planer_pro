from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .... import crud, models, schemas
from ..deps import get_current_active_user
from ....db.session import get_db_session
from ....models.plant import CompanionType

router = APIRouter()

@router.get("/plants/catalog/{plant_id}/compatible-pairs", response_model=List[schemas.PlantCatalog])
async def get_compatible_plants(
    *,
    db: AsyncSession = Depends(get_db_session),
    plant_id: str,
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Fetch all compatible plant pairs (friends) for a given species from the catalog.
    This demonstrates an optimized query for companion planting rules.
    """
    # First, ensure the plant exists
    plant = await crud.crud_plant.get_plant_from_catalog(db, catalog_id=plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found in catalog")

    # This is a simplified example. A more optimized query could do this in one step
    # with a more complex join in the CRUD layer.
    rules = await crud.crud_plant.get_companion_rules_for_plant(db, plant_id=plant_id)

    compatible_plants = []
    for rule in rules:
        if rule.relationship_type == CompanionType.friend:
            # The rule gives us the target plant's ID, we need to fetch the full object
            compatible_plant = await crud.crud_plant.get_plant_from_catalog(db, catalog_id=rule.target_plant_id)
            if compatible_plant:
                compatible_plants.append(compatible_plant)

    return compatible_plants


@router.get("/audit/by-project/{project_id}", response_model=List[schemas.AuditLog])
async def get_project_audit_log(
    *,
    db: AsyncSession = Depends(get_db_session),
    project_id: str,
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Fetch the audit log for a specific project.
    """
    # Check if user has access to this project
    project = await crud.crud_project.get_project(db, project_id=project_id, owner_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    logs = await crud.crud_audit.get_audit_logs_for_project(db, project_id=project_id)
    return logs

@router.get("/audit/by-user/{user_id}", response_model=List[schemas.AuditLog])
async def get_user_audit_log(
    *,
    db: AsyncSession = Depends(get_db_session),
    user_id: str,
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Fetch the audit log for a specific user.
    Only allows a user to fetch their own log.
    """
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    logs = await crud.crud_audit.get_audit_logs_for_user(db, user_id=user_id)
    return logs
