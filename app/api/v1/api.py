from fastapi import APIRouter

from api.v1.endpoints import auth, users, gardens, plants, plant_catalog, agronomic, projects, security, project_management

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Other endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(gardens.router, prefix="/gardens", tags=["Gardens"])
api_router.include_router(plants.router, prefix="/plants", tags=["Plants"])
api_router.include_router(plant_catalog.router, prefix="/plant-catalog", tags=["Plant Catalog"])
api_router.include_router(agronomic.router, prefix="/agronomic", tags=["Agronomic Engine"])
api_router.include_router(projects.router, prefix="/projects", tags=["Project Management"])
api_router.include_router(project_management.router, prefix="/project-management", tags=["Project Management"])
api_router.include_router(security.router, prefix="/security", tags=["Security"])
