from typing import Type, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.locations.models import Location
from src.dao.base import BaseDAO
from src.database import async_session_maker

class LocationDAO(BaseDAO):
    model: Type[Location] = Location

    @classmethod
    async def find_all(cls, **filters) -> list[Location]:
        async with async_session_maker() as session:
            query = select(cls.model).options(
                selectinload(cls.model.children),
                selectinload(cls.model.devices)
            )
            if filters:
                query = query.filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: int) -> Optional[Location]:
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == id_).options(
                selectinload(cls.model.children),
                selectinload(cls.model.devices)
            )
            result = await session.execute(query)
            return result.scalars().first()