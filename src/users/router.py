from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.auth.dependencies import get_current_user
from src.auth.schemas import SUserRead
from src.users.dao import UserDAO

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/", response_model=List[SUserRead], summary="Список всех пользователей")
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
):
    """
    Получить список всех пользователей системы.
    """
    try:
        # Only admins can see all users
        if current_user.role not in ["admin", "main_admin"]:
            raise HTTPException(
                status_code=403, detail="Only admins can view all users"
            )

        users = await UserDAO.list_all(offset=offset, limit=limit)
        return users
    except SQLAlchemyError as e:
        logger.error(f"Database error while listing users: {str(e)}")
        raise HTTPException(500, f"Database error while listing users: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, f"Unexpected error: {str(e)}")


@router.get(
    "/{user_id}", response_model=SUserRead, summary="Получить пользователя по ID"
)
async def get_user(
    user_id: int,
    current_user=Depends(get_current_user),
):
    """
    Получить данные пользователя по его ID.
    """
    try:
        # Only admins or the user themselves can view user details
        if (
            current_user.role not in ["admin", "main_admin"]
            and current_user.id != user_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own profile or you need admin privileges",
            )

        user = await UserDAO.find_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting user {user_id}: {str(e)}")
        raise HTTPException(500, f"Database error while getting user: {str(e)}")
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, f"Unexpected error: {str(e)}")
