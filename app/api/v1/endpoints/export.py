import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response, JSONResponse
from redis.asyncio import Redis

from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserPublic
from app.schemas.export import ProjectJSONExport
from app.api.v1.endpoints.projects import fake_projects_db # Import fake DB
from app.db.mock_data import PLANT_CATALOGUE
from app.core.config import settings

router = APIRouter()

def get_redis(request: Request) -> Redis:
    return request.app.state.redis

async def get_project_for_export(project_id: uuid.UUID, current_user: UserPublic) -> dict:
    """Helper to get and validate a project for export."""
    project = fake_projects_db.get(project_id)
    if not project or project["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.get("/json", response_model=ProjectJSONExport)
async def export_project_json(
    project_id: uuid.UUID = Query(...),
    current_user: UserPublic = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    Export a project's data as a JSON object. Cached in Redis.
    """
    cache_key = f"export:json:{project_id}"
    cached_result = await redis.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    project = await get_project_for_export(project_id, current_user)

    # Create a relevant subset of the plant catalogue for context
    used_plant_ids = {p['plant_id'] for p in project.get('layout', {}).values()}
    plant_catalogue_subset = {p['id']: p for p in PLANT_CATALOGUE if p['id'] in used_plant_ids}

    export_data = ProjectJSONExport(
        project_details=project,
        plant_catalogue_used=plant_catalogue_subset
    )

    await redis.set(cache_key, export_data.json(), ex=settings.REDIS_CACHE_EXPIRE_SECONDS)
    return export_data

@router.get("/pdf")
async def export_project_pdf(
    project_id: uuid.UUID = Query(...),
    current_user: UserPublic = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    Simulates exporting a project plan as a PDF file. Cached in Redis.
    In a real application, this would generate a PDF using a library like ReportLab or WeasyPrint.
    """
    cache_key = f"export:pdf:{project_id}"
    cached_result = await redis.get(cache_key)
    if cached_result:
        return Response(content=cached_result, media_type="application/pdf")

    project = await get_project_for_export(project_id, current_user)

    # Mock PDF content
    content = f"--- PDF EXPORT ---\nProject: {project['name']}\nID: {project['id']}\n--- MOCK FILE ---"

    await redis.set(cache_key, content, ex=settings.REDIS_CACHE_EXPIRE_SECONDS)
    return Response(content=content, media_type="application/pdf")

@router.get("/png")
async def export_project_png(
    project_id: uuid.UUID = Query(...),
    current_user: UserPublic = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    Simulates exporting a project layout as a PNG image. Cached in Redis.
    In a real application, this would generate an image using a library like Pillow or Matplotlib.
    """
    cache_key = f"export:png:{project_id}"
    cached_result = await redis.get(cache_key)
    if cached_result:
        return Response(content=cached_result, media_type="image/png")

    project = await get_project_for_export(project_id, current_user)

    # Mock PNG content
    content = f"PNG image data for project {project['name']}"

    await redis.set(cache_key, content, ex=settings.REDIS_CACHE_EXPIRE_SECONDS)
    return Response(content=f"Fake PNG data: {content}", media_type="image/png")
