from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.plant import PlantCatalog, PlantInstance, CompanionRule
from ..schemas.plant import PlantCatalogCreate, PlantInstanceCreate, CompanionRuleCreate
import uuid

# --- PlantCatalog CRUD ---

async def get_plant_from_catalog(db: AsyncSession, catalog_id: uuid.UUID) -> PlantCatalog | None:
    result = await db.execute(select(PlantCatalog).filter(PlantCatalog.id == catalog_id))
    return result.scalars().first()

async def get_all_plants_from_catalog(db: AsyncSession, skip: int = 0, limit: int = 1000) -> list[PlantCatalog]:
    result = await db.execute(select(PlantCatalog).offset(skip).limit(limit))
    return result.scalars().all()

async def create_plant_in_catalog(db: AsyncSession, plant_in: PlantCatalogCreate) -> PlantCatalog:
    db_plant = PlantCatalog(**plant_in.model_dump())
    db.add(db_plant)
    await db.commit()
    await db.refresh(db_plant)
    return db_plant

# --- PlantInstance CRUD ---

async def get_plant_instance(db: AsyncSession, instance_id: uuid.UUID) -> PlantInstance | None:
    result = await db.execute(select(PlantInstance).filter(PlantInstance.id == instance_id))
    return result.scalars().first()

async def get_plant_instances_for_project(db: AsyncSession, project_id: uuid.UUID) -> list[PlantInstance]:
    result = await db.execute(select(PlantInstance).filter(PlantInstance.project_id == project_id))
    return result.scalars().all()

async def create_plant_instance(db: AsyncSession, instance_in: PlantInstanceCreate) -> PlantInstance:
    db_instance = PlantInstance(**instance_in.model_dump())
    db.add(db_instance)
    await db.commit()
    await db.refresh(db_instance)
    return db_instance

# --- CompanionRule CRUD ---

async def get_companion_rules_for_plant(db: AsyncSession, plant_id: uuid.UUID) -> list[CompanionRule]:
    """Gets all companion rules where the given plant is the source."""
    result = await db.execute(select(CompanionRule).filter(CompanionRule.source_plant_id == plant_id))
    return result.scalars().all()

async def create_companion_rule(db: AsyncSession, rule_in: CompanionRuleCreate) -> CompanionRule:
    db_rule = CompanionRule(**rule_in.model_dump())
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule
