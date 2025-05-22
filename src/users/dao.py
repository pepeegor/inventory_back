from typing import Type, Any, List, Optional
from sqlalchemy import select
from src.dao.base import BaseDAO
from src.users.models import User

class UserDAO(BaseDAO):
    model: Type[User] = User

    @classmethod
    async def find_by_email(cls, email: str) -> Optional[User]:
        return await cls.find_one_or_none(email=email)

    @classmethod
    async def list_all(cls, offset: int = 0, limit: int = 100) -> List[User]:
        # reuse BaseDAO.paginate
        return await cls.paginate(offset=offset, limit=limit)
