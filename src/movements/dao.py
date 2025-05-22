from typing import Type, Optional, Any, List
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
