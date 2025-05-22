from typing import List, Optional, Type
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database import async_session_maker
from src.dao.base import BaseDAO
from src.part_types.models import PartType


class PartTypeDAO(BaseDAO):
    model: Type[PartType] = PartType

    @classmethod
    async def find_all(cls, *, creator_id: Optional[int] = None) -> List[PartType]:
        async with async_session_maker() as session:
            q = select(cls.model).options(selectinload(cls.model.device_types))
            if creator_id is not None:
                q = q.where(cls.model.created_by == creator_id)
            result = await session.execute(q)
            return result.scalars().all()

    @classmethod
    async def find_by_id(
        cls, id_: int, *, creator_id: Optional[int] = None
    ) -> Optional[PartType]:
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .where(cls.model.id == id_)
                .options(selectinload(cls.model.device_types))
            )
            if creator_id is not None:
                q = q.where(cls.model.created_by == creator_id)
            result = await session.execute(q)
            return result.scalars().first()
