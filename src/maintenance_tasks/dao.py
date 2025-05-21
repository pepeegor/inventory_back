from datetime import date
from typing import Optional, List, Type
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database import async_session_maker
from src.dao.base import BaseDAO
from src.maintenance_tasks.models import MaintenanceTask

class MaintenanceTaskDAO(BaseDAO):
    model: Type[MaintenanceTask] = MaintenanceTask

    @classmethod
    async def find_all(
        cls,
        *,
        device_id: Optional[int] = None,
        assigned_to: Optional[int] = None,
        status: Optional[str] = None,
        scheduled_from: Optional[date] = None,
        scheduled_to: Optional[date] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[MaintenanceTask]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.device),
                    selectinload(cls.model.assigned_user),
                )
                .offset(offset)
                .limit(limit)
            )
            if device_id is not None:
                query = query.where(cls.model.device_id == device_id)
            if assigned_to is not None:
                query = query.where(cls.model.assigned_to == assigned_to)
            if status is not None:
                query = query.where(cls.model.status == status)
            if scheduled_from is not None:
                query = query.where(cls.model.scheduled_date >= scheduled_from)
            if scheduled_to is not None:
                query = query.where(cls.model.scheduled_date <= scheduled_to)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: int) -> Optional[MaintenanceTask]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == id_)
                .options(
                    selectinload(cls.model.device),
                    selectinload(cls.model.assigned_user),
                )
            )
            result = await session.execute(query)
            return result.scalars().first()
