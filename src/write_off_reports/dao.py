from typing import Any, Optional, List, Type
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.write_off_reports.models import WriteOffReport


class WriteOffReportDAO(BaseDAO):
    model: Type[WriteOffReport] = WriteOffReport

    @classmethod
    async def find_all(
        cls,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        disposed_by: int | None = None,
        approved_by: int | None = None
    ) -> List[WriteOffReport]:
        async with async_session_maker() as session:
            query = select(cls.model).options(
                selectinload(cls.model.device),
                selectinload(cls.model.disposed_by_user),
                selectinload(cls.model.approved_by_user),
            )
            filters: list[Any] = []
            if date_from is not None:
                filters.append(cls.model.report_date >= date_from)
            if date_to is not None:
                filters.append(cls.model.report_date <= date_to)
            if disposed_by is not None:
                filters.append(cls.model.disposed_by == disposed_by)
            if approved_by is not None:
                filters.append(cls.model.approved_by == approved_by)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(cls.model.report_date.desc())
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, id_: Any) -> Optional[WriteOffReport]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(cls.model)
                .where(cls.model.id == id_)
                .options(
                    selectinload(cls.model.device),
                    selectinload(cls.model.disposed_by_user),
                    selectinload(cls.model.approved_by_user),
                )
            )
            return result.scalars().first()

    @classmethod
    async def count_all(cls) -> int:
        async with async_session_maker() as session:
            result = await session.execute(select(func.count(cls.model.id)))
            return result.scalar()
