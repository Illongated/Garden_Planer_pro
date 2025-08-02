from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, Dict, Optional, Union, List
import uuid

from app.crud.base import CRUDBase
from app.models import Garden, User
from app.schemas import GardenCreate, GardenUpdate

class CRUDGarden(CRUDBase[Garden, GardenCreate, GardenUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: GardenCreate, owner_id: uuid.UUID
    ) -> Garden:
        db_obj = Garden(**obj_in.model_dump(), owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Garden]:
        result = await db.execute(
            select(self.model)
            .where(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

garden = CRUDGarden(Garden)
