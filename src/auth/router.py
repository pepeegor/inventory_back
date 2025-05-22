from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

from src.exceptions import BadRequestException, UnauthorizedException
from src.auth.auth import authenticate_user, create_access_token, get_password_hash
from src.users.dao import UserDAO
from src.auth.dependencies import get_current_user
from src.auth.schemas import (
    SChangePassword,
    SLoginRequest,
    STokenResponse,
    SUserProfileUpdate,
    SUserRegister,
    SUserRead,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth & Пользователи"],
)

# Настройка логирования
logger = logging.getLogger(__name__)


@router.post(
    "/register", summary="Регистрация нового пользователя", response_model=SUserRead
)
async def register_user(user_data: SUserRegister) -> SUserRead:
    try:
        existing_user = await UserDAO.find_one_or_none(email=user_data.email)
        if existing_user:
            raise BadRequestException(
                detail="Пользователь с таким e-mail уже существует"
            )

        hashed_password = get_password_hash(user_data.password.get_secret_value())
        user = await UserDAO.create(
            username=user_data.username,
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
        )
        return SUserRead.model_validate(user)
    except IntegrityError as e:
        error_msg = str(e)
        if "unique constraint" in error_msg.lower() and "email" in error_msg.lower():
            raise BadRequestException(
                detail="Пользователь с таким e-mail уже существует"
            )
        elif (
            "unique constraint" in error_msg.lower() and "username" in error_msg.lower()
        ):
            raise BadRequestException(
                detail="Пользователь с таким username уже существует"
            )
        else:
            raise BadRequestException(detail=f"Ошибка создания пользователя: {str(e)}")
    except SQLAlchemyError as e:
        raise BadRequestException(detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        raise BadRequestException(detail=f"Неизвестная ошибка: {str(e)}")


@router.post(
    "/login", summary="Авторизация пользователя (login)", response_model=STokenResponse
)
async def login_user(response: Response, user_data: SLoginRequest) -> STokenResponse:
    try:
        user = await authenticate_user(user_data.email, user_data.password)
        if not user:
            raise UnauthorizedException(detail="Неверный e-mail или пароль")
        access_token = create_access_token({"sub": user.id})
        response.set_cookie("shelter_access_token", access_token, httponly=True)
        return STokenResponse(access_token=access_token, token_type="bearer")
    except SQLAlchemyError as e:
        # Логирование ошибки для диагностики
        logger.error(f"SQLAlchemy error during authentication: {str(e)}", exc_info=True)
        raise UnauthorizedException(detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}", exc_info=True)
        if isinstance(e, UnauthorizedException):
            raise e
        raise UnauthorizedException(detail=f"Ошибка аутентификации: {str(e)}")


@router.post(
    "/logout",
    dependencies=[Depends(get_current_user)],
    summary="Выход пользователя (logout)",
)
async def logout_user(response: Response) -> JSONResponse:
    response.delete_cookie(key="shelter_access_token", httponly=True)
    return {"detail": "Successfully logged out"}


@router.get(
    "/me",
    response_model=SUserRead,
    summary="Профиль текущего пользователя",
    dependencies=[Depends(get_current_user)],
)
async def get_my_profile(current_user=Depends(get_current_user)) -> SUserRead:
    """
    Возвращает данные авторизованного под текущим токеном пользователя.
    """
    return SUserRead.model_validate(current_user)


@router.put(
    "/me",
    response_model=SUserRead,
    summary="Обновить свой профиль (username и/или full_name)",
    dependencies=[Depends(get_current_user)],
)
async def update_profile(
    data: SUserProfileUpdate, current_user=Depends(get_current_user)
) -> SUserRead:
    try:
        payload = data.model_dump(exclude_none=True)
        if not payload:
            raise BadRequestException(detail="Нечего обновлять")

        updated = await UserDAO.update(current_user.id, **payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return SUserRead.model_validate(updated)
    except IntegrityError as e:
        error_msg = str(e)
        if "unique constraint" in error_msg.lower() and "username" in error_msg.lower():
            raise BadRequestException(
                detail="Пользователь с таким username уже существует"
            )
        else:
            raise BadRequestException(detail=f"Ошибка обновления профиля: {str(e)}")
    except SQLAlchemyError as e:
        raise BadRequestException(detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        raise BadRequestException(detail=f"Неизвестная ошибка: {str(e)}")


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Сменить пароль",
    dependencies=[Depends(get_current_user)],
)
async def change_password(
    data: SChangePassword, current_user=Depends(get_current_user)
):
    try:
        user = await authenticate_user(
            current_user.email, data.old_password.get_secret_value()
        )
        if not user:
            raise UnauthorizedException(detail="Неверный текущий пароль")

        new_hash = get_password_hash(data.new_password.get_secret_value())
        await UserDAO.update(current_user.id, password_hash=new_hash)

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError as e:
        raise BadRequestException(detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        if isinstance(e, UnauthorizedException):
            raise e
        raise BadRequestException(detail=f"Ошибка при смене пароля: {str(e)}")
