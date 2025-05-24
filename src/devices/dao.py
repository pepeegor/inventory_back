from typing import Any, Optional, List, Type
from sqlalchemy import select, or_, func
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
        is_admin: bool = False,
        offset: int = 0,
        limit: int = 100,
        type_id: int | None = None,
        status: str | None = None,
        current_location_id: int | None = None
    ) -> List[Device]:
        """
        Возвращает устройства:
        - Для админа: все устройства
        - Для обычного пользователя: устройства, у которых current_location.created_by == creator_id или created_by == creator_id
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
                .offset(offset)
                .limit(limit)
            )

            # Применяем фильтры доступа только для не-админов
            if not is_admin:
                q = (
                    q
                    # join на Location, чтобы фильтровать по created_by
                    .outerjoin(cls.model.current_location).where(
                        or_(
                            Location.created_by == creator_id,
                            cls.model.created_by == creator_id,
                        )
                    )
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
    async def find_by_id(
        cls, id_: Any, *, creator_id: int, is_admin: bool = False
    ) -> Optional[Device]:
        """
        Возвращает устройство:
        - Для админа: любое устройство
        - Для обычного пользователя: если оно принадлежит пользователю (created_by == creator_id) или находится
          в локации пользователя (current_location.created_by == creator_id)
        """
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .options(
                    selectinload(cls.model.type),
                    selectinload(cls.model.type).selectinload(DeviceType.part_types),
                    selectinload(cls.model.current_location),
                )
                .where(cls.model.id == id_)
            )

            # Применяем фильтры доступа только для не-админов
            if not is_admin:
                q = q.outerjoin(cls.model.current_location).where(
                    or_(
                        Location.created_by == creator_id,
                        cls.model.created_by == creator_id,
                    )
                )

            result = await session.execute(q)
            return result.scalars().first()

    @classmethod
    async def update_status(cls, device_id: int, status: str) -> Optional[Device]:
        """
        Updates device status and returns the updated device
        """
        async with async_session_maker() as session:
            device = await session.get(cls.model, device_id)
            if not device:
                return None

            device.status = status
            await session.commit()
            await session.refresh(device)
            return device

    @classmethod
    async def find_by_id_admin(cls, id_: Any) -> Optional[Device]:
        """
        Возвращает устройство без проверки прав доступа (для админских операций)
        """
        async with async_session_maker() as session:
            q = (
                select(cls.model)
                .options(
                    selectinload(cls.model.type),
                    selectinload(cls.model.type).selectinload(DeviceType.part_types),
                    selectinload(cls.model.current_location),
                )
                .where(cls.model.id == id_)
            )
            result = await session.execute(q)
            return result.scalars().first()

    @classmethod
    async def count_all(cls) -> int:
        async with async_session_maker() as session:
            result = await session.execute(select(func.count(cls.model.id)))
            return result.scalar()

    @classmethod
    async def count_created_between(cls, start, end) -> int:
        async with async_session_maker() as session:
            result = await session.execute(
                select(func.count(cls.model.id)).where(
                    cls.model.purchase_date >= start, cls.model.purchase_date < end
                )
            )
            return result.scalar()
