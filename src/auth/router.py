from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse

from src.exceptions import BadRequestException, UnauthorizedException
from src.auth.auth import authenticate_user, create_access_token, get_password_hash
from src.users.dao import UserDAO
from src.auth.dependencies import get_current_user
from src.auth.schemas import SLoginRequest, STokenResponse, SUserRegister, SUserRead

router = APIRouter(
    prefix="/auth",
    tags=["Auth & Пользователи"],
)

@router.post("/register", summary="Регистрация нового пользователя", response_model=SUserRead)
async def register_user(user_data: SUserRegister) -> SUserRead:
    existing_user = await UserDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise BadRequestException(detail="Пользователь с таким e-mail уже существует")
    hashed_password = get_password_hash(user_data.password.get_secret_value())
    user = await UserDAO.create(
        username=user_data.username,
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )
    return SUserRead.model_validate(user)

@router.post("/login", summary="Авторизация пользователя (login)", response_model=STokenResponse)
async def login_user(response: Response, user_data: SLoginRequest) -> STokenResponse:
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise UnauthorizedException(detail="Неверный e-mail или пароль")
    access_token = create_access_token({"sub": user.id})
    response.set_cookie("shelter_access_token", access_token, httponly=True)
    return STokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.post(
    "/logout",
    dependencies=[Depends(get_current_user)],
    summary="Выход пользователя (logout)"
)
async def logout_user(response: Response) -> JSONResponse:
    response.delete_cookie(
        key="shelter_access_token",
        httponly=True
    )
    return {"detail": "Successfully logged out"}