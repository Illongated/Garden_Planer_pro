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

    # Seed Plant Catalog
    logger.info("Creating plant catalog...")
    from app.crud import plant_catalog as crud_plant_catalog
    from app.schemas import PlantCatalogCreate

    plant_catalog_data = [
        { "id": 1, "name": "Tomato", "variety": "Roma", "plant_type": "Vegetable", "image": "https://i.ibb.co/bFqgLqj/tomato.jpg", "description": "A popular and versatile vegetable, great for sauces and salads.", "sun": "Full Sun", "water": "Regular", "spacing": "18-24 inches", "planting_season": ["Spring", "Summer"], "harvest_season": ["Summer", "Fall"], "compatibility": ["Basil", "Carrot"], "tips": "Provide support with stakes or cages. Water consistently to prevent blossom-end rot." },
        { "id": 2, "name": "Basil", "variety": "Genovese", "plant_type": "Herb", "image": "https://i.ibb.co/mSgM1SP/basil.jpg", "description": "A fragrant herb that is a staple in Italian cuisine.", "sun": "Full Sun", "water": "Regular", "spacing": "10-12 inches", "planting_season": ["Spring", "Summer"], "harvest_season": ["Summer", "Fall"], "compatibility": ["Tomato", "Pepper"], "tips": "Pinch off flower buds to encourage leaf growth. Harvest leaves from the top to promote a bushier plant." },
        { "id": 3, "name": "Carrot", "variety": "Danvers", "plant_type": "Vegetable", "image": "https://i.ibb.co/hRk5T1N/carrot.jpg", "description": "A sweet root vegetable that is rich in Vitamin A.", "sun": "Full Sun", "water": "Regular", "spacing": "2-3 inches", "planting_season": ["Spring", "Fall"], "harvest_season": ["Summer", "Fall"], "compatibility": ["Lettuce", "Radish", "Tomato"], "tips": "Ensure soil is loose and free of rocks for straight root growth. Keep soil moist to prevent splitting." },
        { "id": 4, "name": "Marigold", "variety": "French", "plant_type": "Flower", "image": "https://i.ibb.co/qNq3sKk/marigold.jpg", "description": "A cheerful flower that helps deter pests in the garden.", "sun": "Full Sun", "water": "Moderate", "spacing": "8-10 inches", "planting_season": ["Spring", "Summer"], "harvest_season": [], "compatibility": ["Most vegetables"], "tips": "Deadhead spent blooms to encourage continuous flowering. Tolerant of poor soil and heat." },
        { "id": 5, "name": "Lettuce", "variety": "Romaine", "plant_type": "Vegetable", "image": "https://i.ibb.co/2Zp6fVn/lettuce.jpg", "description": "A crisp, leafy green perfect for salads and sandwiches.", "sun": "Partial Shade", "water": "Regular", "spacing": "8-12 inches", "planting_season": ["Spring", "Fall"], "harvest_season": ["Spring", "Fall"], "compatibility": ["Carrot", "Cucumber", "Strawberry"], "tips": "Prefers cooler weather. Provide afternoon shade in warmer climates to prevent bolting." },
        { "id": 6, "name": "Cucumber", "variety": "Marketmore", "plant_type": "Vegetable", "image": "https://i.ibb.co/Y06j2p1/cucumber.jpg", "description": "A refreshing vegetable for salads, pickling, or eating fresh.", "sun": "Full Sun", "water": "Plentiful", "spacing": "12-18 inches", "planting_season": ["Spring", "Summer"], "harvest_season": ["Summer"], "compatibility": ["Beans", "Corn", "Peas"], "tips": "Grow on a trellis to save space and keep fruit clean. Water deeply and consistently." },
        { "id": 7, "name": "Rosemary", "variety": "Arp", "plant_type": "Herb", "image": "https://i.ibb.co/K2gS3P1/rosemary.jpg", "description": "A woody, perennial herb with fragrant, needle-like leaves.", "sun": "Full Sun", "water": "Drought-tolerant", "spacing": "2-3 feet", "planting_season": ["Spring"], "harvest_season": ["Year-round"], "compatibility": ["Cabbage", "Sage"], "tips": "Requires well-drained soil. Can be grown in containers. Prune after flowering to maintain shape." },
        { "id": 8, "name": "Zinnia", "variety": "California Giant", "plant_type": "Flower", "image": "https://i.ibb.co/yQdCg8N/zinnia.jpg", "description": "A vibrant, easy-to-grow flower that attracts pollinators.", "sun": "Full Sun", "water": "Moderate", "spacing": "10-12 inches", "planting_season": ["Spring", "Summer"], "harvest_season": [], "compatibility": ["All plants"], "tips": "Deadhead regularly to promote more blooms. Good air circulation helps prevent powdery mildew." }
    ]

    for plant_data in plant_catalog_data:
        plant = await crud_plant_catalog.get(db, id=plant_data["id"])
        if not plant:
            plant_in = PlantCatalogCreate(**plant_data)
            await crud_plant_catalog.create(db, obj_in=plant_in)
            logger.info(f"Created catalog plant: {plant_in.name}")
        else:
            logger.info(f"Catalog plant already exists: {plant.name}")


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
