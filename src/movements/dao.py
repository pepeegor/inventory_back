from typing import Type, Optional, Any, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.movements.models import Movement
from src.dao.base import BaseDAO
from src.database import async_session_maker


class MovementDAO(BaseDAO):
    model: Type[Movement] = Movement

    @classmethod
    async def find_by_device_id(
        cls, device_id: Any, user_id: Optional[int] = None
    ) -> List[Movement]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.device_id == device_id)
                .options(
                    selectinload(cls.model.from_location),
                    selectinload(cls.model.to_location),
                    selectinload(cls.model.performed_by_user),
                )
                .order_by(cls.model.moved_at.desc())
            )
            if user_id is not None:
                query = query.where(cls.model.performed_by == user_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: Any) -> Optional[Movement]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == id_)
                .options(
                    selectinload(cls.model.from_location),
                    selectinload(cls.model.to_location),
                    selectinload(cls.model.performed_by_user),
                )
            )
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_all(
        cls,
        *,
        device_id: Optional[int] = None,
        performed_by: Optional[int] = None,
        from_location_id: Optional[int] = None,
        to_location_id: Optional[int] = None,
        moved_from: Optional[datetime] = None,
        moved_to: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Movement]:
        """
        Получить все перемещения с фильтрацией и пагинацией
        """
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.from_location),
                    selectinload(cls.model.to_location),
                    selectinload(cls.model.performed_by_user),
                )
                .order_by(cls.model.moved_at.desc())
                .offset(offset)
                .limit(limit)
            )

            if device_id is not None:
                query = query.where(cls.model.device_id == device_id)
            if performed_by is not None:
                query = query.where(cls.model.performed_by == performed_by)
            if from_location_id is not None:
                query = query.where(cls.model.from_location_id == from_location_id)
            if to_location_id is not None:
                query = query.where(cls.model.to_location_id == to_location_id)
            if moved_from is not None:
                query = query.where(cls.model.moved_at >= moved_from)
            if moved_to is not None:
                query = query.where(cls.model.moved_at <= moved_to)

            result = await session.execute(query)
            return result.scalars().all()
