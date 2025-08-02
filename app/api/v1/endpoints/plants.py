import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from redis.asyncio import Redis

from app.schemas.plant import Plant
from app.db.mock_data import PLANT_CATALOGUE
from app.core.config import settings

router = APIRouter()

def get_redis(request: Request) -> Redis:
    return request.app.state.redis

@router.get("/", response_model=List[Plant])
async def search_plants(
    request: Request,
    q: Optional[str] = Query(None, description="Search term to query in plant name and description."),
    sun: Optional[str] = Query(None, description="Filter by sun needs (e.g., 'Full Sun', 'Partial Shade')."),
    water: Optional[str] = Query(None, description="Filter by water needs (e.g., 'Low', 'Moderate', 'High')."),
    redis: Redis = Depends(get_redis)
):
    """
    Search the plant catalogue with optional filters.
    Results are cached in Redis for performance.
    """
    # Create a unique cache key based on the query parameters
    cache_key = f"plants_search:q={q}:sun={sun}:water={water}"

    cached_result = await redis.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    # If not in cache, filter the data
    results = [Plant(**p) for p in PLANT_CATALOGUE]

    if q:
        q_lower = q.lower()
        results = [
            p for p in results
            if q_lower in p.name.lower() or q_lower in p.description.lower()
        ]

    if sun:
        results = [p for p in results if p.sun_needs.lower() == sun.lower()]

    if water:
        results = [p for p in results if p.water_needs.lower() == water.lower()]

    # Store the result in Redis with an expiration time
    await redis.set(cache_key, json.dumps([p.dict() for p in results]), ex=settings.REDIS_CACHE_EXPIRE_SECONDS)

    return results

@router.get("/{plant_id}", response_model=Plant)
async def read_plant(
    plant_id: int,
    redis: Redis = Depends(get_redis)
):
    """
    Get a single plant by its ID.
    Result is cached in Redis.
    """
    cache_key = f"plant:{plant_id}"

    cached_result = await redis.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    plant = next((Plant(**p) for p in PLANT_CATALOGUE if p["id"] == plant_id), None)

    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

    await redis.set(cache_key, plant.json(), ex=settings.REDIS_CACHE_EXPIRE_SECONDS)

    return plant
