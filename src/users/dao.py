from typing import List
from sqlalchemy import select
from src.dao.base import BaseDAO
from src.users.models import User
from src.database import async_session_maker
from sqlalchemy.orm import selectinload

class UserDAO(BaseDAO):
    
    model = User

    
    