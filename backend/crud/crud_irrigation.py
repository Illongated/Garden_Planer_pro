from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.irrigation import IrrigationZone
from ..schemas.irrigation import IrrigationZoneCreate
import uuid

async def create_irrigation_zone(db: AsyncSession, zone_in: IrrigationZoneCreate) -> IrrigationZone:
    """Create a new irrigation zone for a project."""
    db_zone = IrrigationZone(**zone_in.model_dump())
    db.add(db_zone)
    await db.commit()
    await db.refresh(db_zone)
    return db_zone

async def get_irrigation_zones_for_project(db: AsyncSession, project_id: uuid.UUID) -> list[IrrigationZone]:
    """Get all irrigation zones for a specific project."""
    result = await db.execute(select(IrrigationZone).filter(IrrigationZone.project_id == project_id))
    return result.scalars().all()
