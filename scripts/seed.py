import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from app.models import User, Garden, Plant  # noqa
from app.crud import user as crud_user
from app.crud import garden as crud_garden
from app.crud import plant as crud_plant
from app.schemas import UserCreate, GardenCreate, PlantCreate
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data(db: AsyncSession) -> None:
    """
    Populates the database with initial data.
    """
    # Create Users
    logger.info("Creating users...")
    user1_in = UserCreate(email="user1@example.com", password="password123", full_name="Alice")
    user2_in = UserCreate(email="user2@example.com", password="password456", full_name="Bob")

    user1 = await crud_user.get_by_email(db, email=user1_in.email)
    if not user1:
        user1 = await crud_user.create(db, obj_in=user1_in)
        logger.info(f"Created user: {user1.email}")
    else:
        logger.info(f"User already exists: {user1.email}")

    user2 = await crud_user.get_by_email(db, email=user2_in.email)
    if not user2:
        user2 = await crud_user.create(db, obj_in=user2_in)
        logger.info(f"Created user: {user2.email}")
    else:
        logger.info(f"User already exists: {user2.email}")

    # Create Gardens
    logger.info("Creating gardens...")
    garden1_in = GardenCreate(name="Alice's Herb Garden", location="Kitchen Window")
    garden2_in = GardenCreate(name="Bob's Vegetable Patch", location="Backyard")

    garden1 = await crud_garden.create_with_owner(db, obj_in=garden1_in, owner_id=user1.id)
    logger.info(f"Created garden: {garden1.name}")
    garden2 = await crud_garden.create_with_owner(db, obj_in=garden2_in, owner_id=user2.id)
    logger.info(f"Created garden: {garden2.name}")

    # Create Plants
    logger.info("Creating plants...")
    plant1_in = PlantCreate(name="Basil", species="Ocimum basilicum", garden_id=garden1.id)
    plant2_in = PlantCreate(name="Tomato", species="Solanum lycopersicum", garden_id=garden2.id)
    plant3_in = PlantCreate(name="Mint", species="Mentha spicata", garden_id=garden1.id)

    await crud_plant.create(db, obj_in=plant1_in)
    logger.info(f"Created plant: {plant1_in.name}")
    await crud_plant.create(db, obj_in=plant2_in)
    logger.info(f"Created plant: {plant2_in.name}")
    await crud_plant.create(db, obj_in=plant3_in)
    logger.info(f"Created plant: {plant3_in.name}")

    logger.info("Database seeding completed successfully.")

async def main() -> None:
    logger.info("Starting database seeding...")
    async with engine.begin() as conn:
        # You might want to drop and create tables for a clean seed
        # from app.models.base import Base
        # await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)
        pass # Assuming alembic handles table creation

    async with AsyncSessionLocal() as session:
        await seed_data(session)

    await engine.dispose()
    logger.info("Finished database seeding.")


if __name__ == "__main__":
    asyncio.run(main())
