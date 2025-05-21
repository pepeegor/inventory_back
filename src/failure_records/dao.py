# src/failure_records/dao.py

from typing import Any, Optional, List, Type
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.failure_records.models import FailureRecord


class FailureRecordDAO(BaseDAO):
    model: Type[FailureRecord] = FailureRecord

    @classmethod
    async def find_by_device_id(cls, device_id: int) -> List[FailureRecord]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.device_id == device_id)
                .options(
                    selectinload(cls.model.part_type), selectinload(cls.model.device)
                )
                .order_by(cls.model.failure_date.desc())
            )
            return result.scalars().all()

    @classmethod
    async def find_by_part_type_id(cls, part_type_id: int) -> List[FailureRecord]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.part_type_id == part_type_id)
                .options(
                    selectinload(cls.model.part_type), selectinload(cls.model.device)
                )
                .order_by(cls.model.failure_date.desc())
            )
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: Any) -> Optional[FailureRecord]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.id == id_)
                .options(
                    selectinload(cls.model.part_type), selectinload(cls.model.device)
                )
            )
            return result.scalars().first()
