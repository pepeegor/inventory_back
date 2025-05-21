from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import select, func

from src.database import async_session_maker

T = TypeVar("T")

class BaseDAO:
    model: Type[T]  

    @classmethod
    async def find_all(cls, **filters: Any) -> List[T]:
        async with async_session_maker() as session:
            query = select(cls.model)
            if filters:
                query = query.filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: Any) -> Optional[T]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model).where(cls.model.id == id_)
            )
            return result.scalars().first()

    @classmethod
    async def find_one_or_none(cls, **filters: Any) -> Optional[T]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def count(cls) -> int:
        async with async_session_maker() as session:
            result = await session.execute(
                select(func.count()).select_from(cls.model)
            )
            return result.scalar_one()

    @classmethod
    async def paginate(
        cls,
        offset: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        async with async_session_maker() as session:
            query = select(cls.model).offset(offset).limit(limit)
            if filters:
                query = query.filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def create(cls, **data: Any) -> T:
        async with async_session_maker() as session:
            instance = cls.model(**data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    @classmethod
    async def update(cls, id_: Any, **data: Any) -> Optional[T]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model).where(cls.model.id == id_)
            )
            instance = result.scalars().first()
            if not instance:
                return None

            for key, value in data.items():
                setattr(instance, key, value)

            await session.commit()
            await session.refresh(instance)
            return instance

    @classmethod
    async def delete(cls, id_: Any) -> bool:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model).where(cls.model.id == id_)
            )
            instance = result.scalars().first()
            if not instance:
                return False

            await session.delete(instance)
            await session.commit()
            return True