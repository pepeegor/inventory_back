from typing import Any, Optional, List, Type
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.failure_records.models import FailureRecord
from src.devices.models import Device
from src.locations.models import Location


class FailureRecordDAO(BaseDAO):
    model: Type[FailureRecord] = FailureRecord

    @classmethod
    async def find_by_device_id(
        cls, device_id: int, *, creator_id: int
    ) -> List[FailureRecord]:
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .join(cls.model.device)
                .join(Device.current_location)
                .where(cls.model.device_id == device_id)
                .where(Location.created_by == creator_id)
                .options(
                    selectinload(cls.model.part_type),
                    selectinload(cls.model.device),
                )
                .order_by(cls.model.failure_date.desc())
            )
            result = await session.execute(q)
            return result.scalars().all()

    @classmethod
    async def find_by_part_type_id(
        cls, part_type_id: int, *, creator_id: int
    ) -> List[FailureRecord]:
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .join(cls.model.device)
                .join(Device.current_location)
                .where(cls.model.part_type_id == part_type_id)
                .where(Location.created_by == creator_id)
                .options(
                    selectinload(cls.model.part_type),
                    selectinload(cls.model.device),
                )
                .order_by(cls.model.failure_date.desc())
            )
            result = await session.execute(q)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: Any, *, creator_id: int) -> Optional[FailureRecord]:
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .join(cls.model.device)
                .join(Device.current_location)
                .where(cls.model.id == id_)
                .where(Location.created_by == creator_id)
                .options(
                    selectinload(cls.model.part_type),
                    selectinload(cls.model.device),
                )
            )
            result = await session.execute(q)
            return result.scalars().first()

    @classmethod
    async def find_all_by_creator_id(cls, *, creator_id: int) -> List[FailureRecord]:
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .join(cls.model.device)
                .join(Device.current_location)
                .where(Location.created_by == creator_id)
                .options(
                    selectinload(cls.model.part_type),
                    selectinload(cls.model.device),
                )
                .order_by(cls.model.failure_date.desc())
            )
            result = await session.execute(q)
            return result.scalars().all()

    @classmethod
    async def count_all(cls) -> int:
        async with async_session_maker() as session:
            result = await session.execute(select(func.count(cls.model.id)))
            return result.scalar()
