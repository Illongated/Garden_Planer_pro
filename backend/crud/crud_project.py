from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models.project import GardenProject
from ..schemas.project import GardenProjectCreate, GardenProjectUpdate
import uuid

async def get_project(db: AsyncSession, project_id: uuid.UUID, owner_id: uuid.UUID) -> GardenProject | None:
    """Get a single project by its ID, ensuring it belongs to the owner."""
    result = await db.execute(
        select(GardenProject)
        .filter(GardenProject.id == project_id, GardenProject.owner_id == owner_id)
    )
    return result.scalars().first()

async def get_project_with_details(db: AsyncSession, project_id: uuid.UUID, owner_id: uuid.UUID) -> GardenProject | None:
    """Get a project with all its related plant instances and irrigation zones."""
    result = await db.execute(
        select(GardenProject)
        .options(
            selectinload(GardenProject.plant_instances),
            selectinload(GardenProject.irrigation_zones)
        )
        .filter(GardenProject.id == project_id, GardenProject.owner_id == owner_id)
    )
    return result.scalars().first()

async def get_projects_by_owner(db: AsyncSession, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[GardenProject]:
    """Get all projects for a specific owner."""
    result = await db.execute(
        select(GardenProject)
        .filter(GardenProject.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_project(db: AsyncSession, project_in: GardenProjectCreate, owner_id: uuid.UUID) -> GardenProject:
    """Create a new garden project for a user."""
    db_project = GardenProject(**project_in.model_dump(), owner_id=owner_id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def update_project(db: AsyncSession, db_project: GardenProject, project_in: GardenProjectUpdate) -> GardenProject:
    """Update a garden project."""
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    await db.commit()
    await db.refresh(db_project)
    return db_project

async def delete_project(db: AsyncSession, db_project: GardenProject) -> None:
    """Delete a garden project."""
    await db.delete(db_project)
    await db.commit()
