from typing import Optional, List, Type, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.device_types.models import DeviceType


class DeviceTypeDAO(BaseDAO):
    model: Type[DeviceType] = DeviceType

    @classmethod
    async def find_all(
        cls,
        *,
        offset: int = 0,
        limit: int = 100,
        creator_id: Optional[int] = None,
        **filters: Any
    ) -> List[DeviceType]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.part_types),
                    selectinload(cls.model.creator),
                )
                .offset(offset)
                .limit(limit)
            )
            if creator_id is not None:
                query = query.where(cls.model.created_by == creator_id)
            if filters:
                query = query.filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: int) -> Optional[DeviceType]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == id_)
                .options(selectinload(cls.model.part_types))
            )
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def create(cls, **data: Any) -> DeviceType:
        """
        Создаёт новый объект DeviceType и загружает связанные объекты перед возвращением
        """
        async with async_session_maker() as session:
            instance = cls.model(**data)
            session.add(instance)
            await session.commit()

            # Перезагружаем объект из базы со связанными сущностями
            await session.refresh(instance)

            # Явно загружаем связанные сущности
            query = (
                select(cls.model)
                .where(cls.model.id == instance.id)
                .options(selectinload(cls.model.part_types))
            )
            result = await session.execute(query)
            loaded_instance = result.scalar_one_or_none()

            return loaded_instance or instance

    @classmethod
    async def update(cls, id_: Any, **data: Any) -> Optional[DeviceType]:
        """
        Обновляет объект DeviceType и загружает связанные объекты перед возвращением
        """
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).where(cls.model.id == id_))
            instance = result.scalars().first()
            if not instance:
                return None

            for key, value in data.items():
                setattr(instance, key, value)

            await session.commit()
            await session.refresh(instance)

            # Явно загружаем связанные сущности
            query = (
                select(cls.model)
                .where(cls.model.id == instance.id)
                .options(selectinload(cls.model.part_types))
            )
            result = await session.execute(query)
            loaded_instance = result.scalar_one_or_none()

            return loaded_instance or instance
