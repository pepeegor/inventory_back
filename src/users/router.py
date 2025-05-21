from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import EmailStr
from src.auth.auth import get_password_hash
from src.users.dao import UserDAO
from src.auth.dependencies import get_current_admin_user, get_current_main_admin_user, get_current_user
from src.users.schemas import SUserInfo, SUserUpdate, SUserRolesUpdate

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@router.get("/me", summary="Текущий профиль пользователя")
async def read_current_user(user = Depends(get_current_user)) -> SUserInfo:
    return user

@router.patch("/me", summary="Обновить свой профиль (username или пароль)")
async def update_current_user(
    data: SUserUpdate,
    user = Depends(get_current_user)
) -> SUserInfo:
    update_data = data.model_dump(exclude_none=True)
    if "password" in update_data:
        raw = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(raw.get_secret_value())
    update_data["updated_at"] = datetime.now(timezone.utc)
    return await UserDAO.update(str(user.id), **update_data)


@router.get(
    "/",
    dependencies=[Depends(get_current_admin_user)],
    summary="Список всех пользователей (admin)"
)
async def list_users() -> list[SUserInfo]:
    return await UserDAO.find_all()


@router.get(
    "/{email}",
    dependencies=[Depends(get_current_admin_user)],
    summary="Детали пользователя по e‑mail (admin)"
)
async def get_user_by_email(email: EmailStr) -> SUserInfo:
    user = await UserDAO.find_one_or_none(email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch(
    "/{email}",
    dependencies=[Depends(get_current_admin_user)],
    summary="Обновить пользователя по e‑mail (admin)"
)
async def update_user_by_email(
    email: EmailStr,
    data: SUserUpdate
) -> SUserInfo:
    user = await UserDAO.find_one_or_none(email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = data.model_dump(exclude_none=True)
    if "password" in update_data:
        raw = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(raw.get_secret_value())
    update_data["updated_at"] = datetime.now(timezone.utc)
    return await UserDAO.update(str(user.id), **update_data)


@router.put("/{email}/roles", summary="Назначить роли пользователю по e‑mail (main_admin)")
async def set_user_roles_by_email(
    email: EmailStr,
    data: SUserRolesUpdate,
    current_user = Depends(get_current_main_admin_user),
) -> SUserInfo:
    user = await UserDAO.find_one_or_none(email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.email == current_user.email and "main_admin" not in data.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own main_admin role"
        )

    return await UserDAO.set_roles(str(user.id), data.roles)


@router.delete(
    "/{email}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя по e‑mail (main_admin)"
)
async def delete_user_by_email(
    email: EmailStr,
    current_user = Depends(get_current_main_admin_user),
):
    if email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя"
        )

    user = await UserDAO.find_one_or_none(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await UserDAO.delete(str(user.id))
