from typing import Any, Optional, Type, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import date
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.replacement_suggestions.models import ReplacementSuggestion

class ReplacementSuggestionDAO(BaseDAO):
    model: Type[ReplacementSuggestion] = ReplacementSuggestion

    @classmethod
    async def find_all(
        cls,
        *,
        part_type_id: int | None = None,
        status:        str | None = None,
        date_from:     date | None = None,
        date_to:       date | None = None
    ) -> List[ReplacementSuggestion]:
        async with async_session_maker() as session:
            query = select(cls.model).options(
                selectinload(cls.model.part_type)
            )
            filters = []
            if part_type_id is not None:
                filters.append(cls.model.part_type_id == part_type_id)
            if status is not None:
                filters.append(cls.model.status == status)
            if date_from is not None:
                filters.append(cls.model.suggestion_date >= date_from)
            if date_to is not None:
                filters.append(cls.model.suggestion_date <= date_to)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(cls.model.suggestion_date.desc())
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_part_type_id(
        cls, part_type_id: int
    ) -> List[ReplacementSuggestion]:
        return await cls.find_all(part_type_id=part_type_id)

    @classmethod
    async def find_by_id(cls, id_: Any) -> Optional[ReplacementSuggestion]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.id == id_)
                .options(
                    selectinload(cls.model.part_type)
                )
            )
            return result.scalars().first()
