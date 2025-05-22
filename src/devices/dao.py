from typing import Any, Optional, List, Type
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.devices.models import Device
from src.locations.models import Location
from src.device_types.models import DeviceType
from src.part_types.models import PartType


class DeviceDAO(BaseDAO):
    model: Type[Device] = Device

    @classmethod
    async def find_all(
        cls,
        *,
        creator_id: int,
        offset: int = 0,
        limit: int = 100,
        type_id: int | None = None,
        status: str | None = None,
        current_location_id: int | None = None
    ) -> List[Device]:
        """
        Возвращает только те устройства, у которых current_location.created_by == creator_id.
        """
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                # подгружаем связанные объекты
                .options(
                    selectinload(cls.model.type),
                    selectinload(cls.model.type).selectinload(DeviceType.part_types),
                    selectinload(cls.model.current_location),
                )
                # join на Location, чтобы фильтровать по created_by
                .join(cls.model.current_location)
                .where(Location.created_by == creator_id)
                .offset(offset)
                .limit(limit)
            )
            if type_id is not None:
                q = q.where(cls.model.type_id == type_id)
            if status is not None:
                q = q.where(cls.model.status == status)
            if current_location_id is not None:
                q = q.where(cls.model.current_location_id == current_location_id)

            result = await session.execute(q)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: Any, *, creator_id: int) -> Optional[Device]:
        """
        Тот же join+фильтр по created_by, чтобы не дать посмотреть чужое устройство.
        """
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .options(
                    selectinload(cls.model.type),
                    selectinload(cls.model.type).selectinload(DeviceType.part_types),
                    selectinload(cls.model.current_location),
                )
                .join(cls.model.current_location)
                .where(cls.model.id == id_)
                .where(Location.created_by == creator_id)
            )
            result = await session.execute(q)
            return result.scalars().first()
