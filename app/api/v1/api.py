from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, plants, layout, irrigation, export

api_router = APIRouter()

# Include all the endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(plants.router, prefix="/plants", tags=["Plants Catalogue"])
api_router.include_router(layout.router, prefix="/layout", tags=["Layout Optimizer"])
api_router.include_router(irrigation.router, prefix="/irrigation", tags=["Irrigation Planner"])
api_router.include_router(export.router, prefix="/export", tags=["Export System"])
