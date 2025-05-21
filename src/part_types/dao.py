from typing import Optional, List, Type
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database import async_session_maker
from src.dao.base import BaseDAO
from src.part_types.models import PartType

class PartTypeDAO(BaseDAO):
    model: Type[PartType] = PartType

    @classmethod
    async def find_all(cls) -> List[PartType]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model)
                .options(selectinload(cls.model.device_types))
            )
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: int) -> Optional[PartType]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.id == id_)
                .options(selectinload(cls.model.device_types))
            )
            return result.scalars().first()
