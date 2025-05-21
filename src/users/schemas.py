from pydantic import BaseModel, ConfigDict, Field, EmailStr, SecretStr, field_serializer, model_validator
from typing import List, Annotated
from uuid import UUID
from datetime import datetime
from pydantic import StringConstraints

from app.schemas.base import OrmModel


class SUserInfo(OrmModel):
    id: UUID = Field(..., description="UUID пользователя")
    username: str = Field(..., description="Логин пользователя")
    email: EmailStr = Field(..., description="E-mail пользователя")
    roles: List[str] = Field(..., description="Список кодовых названий ролей пользователя")
    created_at: datetime = Field(..., description="Когда пользователь зарегистрирован")
    updated_at: datetime = Field(..., description="Когда последний раз профиль обновлялся")

    @model_validator(mode="before")
    def convert_roles(cls, user):
        user.roles = [r.name for r in user.roles]
        return user


class SUserUpdate(BaseModel):
    """
    Схема частичного обновления профиля пользователя.
    Позволяет поменять только username или пароль.
    """
    model_config = ConfigDict(extra="forbid")

    username: Annotated[
        str,
        StringConstraints(min_length=3, max_length=50)
    ] | None = Field(
        None,
        description="Новый логин пользователя (от 3 до 50 символов)"
    )
    password: Annotated[
        SecretStr,
        StringConstraints(min_length=8)
    ] | None = Field(
        None,
        description="Новый пароль (не менее 8 символов)"
    )

    @model_validator(mode="before")
    def must_have_at_least_one_field(cls, data):
        if not data or all(data.get(field) is None for field in ("username", "password")):
            raise ValueError("Укажите username или password для обновления")
        return data

class SUserRolesUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    roles: List[str] = Field(
        ..., description="Список кодовых названий ролей"
    )
