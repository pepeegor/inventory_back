from typing import Literal
from pydantic import BaseModel, Field, EmailStr, SecretStr
from src.schemas.base import OrmModel

__all__ = ["SUserRegister", "SUserRead", "SLoginRequest", "STokenResponse"]

class SUserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Логин пользователя от 3 до 50 символов")
    full_name: str = Field(..., min_length=1, max_length=100, description="Полное имя пользователя")
    email: EmailStr = Field(..., description="Корректный e‑mail пользователя")
    password: SecretStr = Field(..., min_length=8, description="Пароль длиной не менее 8 символов")
    role: str = Field(..., description="Роль пользователя: user, admin или main_admin")

class SUserRead(OrmModel):
    id: int = Field(..., description="ID пользователя")
    username: str = Field(..., description="Логин пользователя")
    full_name: str = Field(..., description="Полное имя пользователя")
    email: EmailStr = Field(..., description="E‑mail пользователя")
    role: str = Field(..., description="Роль пользователя")

class SLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="E‑mail пользователя, используемый для входа")
    password: SecretStr = Field(..., min_length=8, description="Пароль пользователя")

class STokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: Literal["bearer"] = Field("bearer", description="Тип токена, всегда 'bearer'")
