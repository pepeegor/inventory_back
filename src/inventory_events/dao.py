from datetime import date
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database import async_session_maker
from src.inventory_events.models import InventoryEvent
from src.dao.base import BaseDAO


class InventoryEventDAO(BaseDAO):
    model = InventoryEvent

    @classmethod
    async def find_all(
        cls,
        *,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        location_id: Optional[int] = None,
        user_id: Optional[int] = None,
        is_admin: bool = False,
        offset: int = 0,
        limit: int = 100
    ) -> List[InventoryEvent]:
        async with async_session_maker() as session:
            query = select(cls.model).options(
                selectinload(cls.model.location),
                selectinload(cls.model.performed_by_user),
                selectinload(cls.model.items),
            )

            # Применяем фильтры
            if date_from:
                query = query.where(cls.model.event_date >= date_from)
            if date_to:
                query = query.where(cls.model.event_date <= date_to)
            if location_id:
                query = query.where(cls.model.location_id == location_id)

            # Фильтруем по пользователю только если не админ
            if not is_admin:
                query = query.where(cls.model.performed_by == user_id)

            # Добавляем пагинацию в конце
            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: int) -> Optional[InventoryEvent]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == id_)
                .options(
                    selectinload(cls.model.location),
                    selectinload(cls.model.performed_by_user),
                    selectinload(cls.model.items),
                )
            )
            result = await session.execute(query)
            return result.scalars().first()
