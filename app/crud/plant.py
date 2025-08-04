from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid

from app.crud.base import CRUDBase
from models import Plant
from schemas import PlantCreate, PlantUpdate

class CRUDPlant(CRUDBase[Plant, PlantCreate, PlantUpdate]):
    async def get_with_garden(self, db: AsyncSession, *, id: uuid.UUID) -> Optional[Plant]:
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.garden))
            .filter(self.model.id == id)
        )
        return result.scalars().first()

    async def get_multi_by_garden(
        self, db: AsyncSession, *, garden_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Plant]:
        result = await db.execute(
            select(self.model)
            .where(self.model.garden_id == garden_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

plant = CRUDPlant(Plant)
