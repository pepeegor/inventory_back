from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError

from src.config import settings
from src.users.dao import UserDAO
from src.exceptions import UnauthorizedException, ForbiddenException
from src.users.models import User


def get_token(request: Request) -> str:
    token = request.cookies.get("shelter_access_token")
    if not token:
        raise UnauthorizedException()
    return token


async def get_current_user(token: str = Depends(get_token)) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )
    except JWTError:
        raise UnauthorizedException(detail="Invalid token")

    exp = payload.get("exp")
    if not exp or int(exp) < datetime.now(timezone.utc).timestamp():
        raise UnauthorizedException(detail="Token expired")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Invalid token payload")

    user = await UserDAO.find_by_id(int(user_id))
    if not user:
        raise UnauthorizedException(detail="User not found")

    return user


async def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"admin"}:
        raise ForbiddenException(detail="Admin privileges required")
    return user



async def get_current_user_optional(request: Request) -> Optional[User]:
    token = request.cookies.get("shelter_access_token")
    if not token:
        return None

    try:
        return await get_current_user(token)
    except HTTPException:
        return None