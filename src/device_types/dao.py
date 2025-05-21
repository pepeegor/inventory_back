from typing import Optional, List, Type, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.device_types.models import DeviceType

class DeviceTypeDAO(BaseDAO):
    model: Type[DeviceType] = DeviceType

    @classmethod
    async def find_all(
        cls,
        offset: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[DeviceType]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(selectinload(cls.model.part_types))
                .offset(offset)
                .limit(limit)
            )
            if filters:
                query = query.filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: int) -> Optional[DeviceType]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == id_)
                .options(selectinload(cls.model.part_types))
            )
            result = await session.execute(query)
            return result.scalars().first()
