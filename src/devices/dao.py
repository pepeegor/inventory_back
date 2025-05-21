from typing import Any, Optional, List, Type
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.devices.models import Device
from src.device_types.models import DeviceType
from src.locations.models import Location

class DeviceDAO(BaseDAO):
    model: Type[Device] = Device

    @classmethod
    async def find_all(
        cls,
        *,
        offset: int = 0,
        limit: int = 100,
        type_id: int | None = None,
        status:  str | None = None,
        current_location_id: int | None = None
    ) -> List[Device]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.type)
                        .selectinload(DeviceType.part_types),
                    selectinload(cls.model.current_location)
                        .selectinload(Location.children),
                    selectinload(cls.model.current_location)
                        .selectinload(Location.devices),
                )
                .offset(offset)
                .limit(limit)
            )
            if type_id is not None:
                query = query.where(cls.model.type_id == type_id)
            if status is not None:
                query = query.where(cls.model.status == status)
            if current_location_id is not None:
                query = query.where(
                    cls.model.current_location_id == current_location_id
                )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: Any) -> Optional[Device]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == id_)
                .options(
                    selectinload(cls.model.type)
                        .selectinload(DeviceType.part_types),
                    selectinload(cls.model.current_location)
                        .selectinload(Location.children),
                    selectinload(cls.model.current_location)
                        .selectinload(Location.devices),
                )
            )
            result = await session.execute(query)
            return result.scalars().first()
