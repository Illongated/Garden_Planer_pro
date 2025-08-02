from fastapi import APIRouter

from app.api.v1.endpoints import users, gardens, plants, plant_catalog

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(gardens.router, prefix="/gardens", tags=["Gardens"])
api_router.include_router(plants.router, prefix="/plants", tags=["Plants"])
api_router.include_router(plant_catalog.router, prefix="/plant-catalog", tags=["Plant Catalog"])
