from pydantic import SecretStr
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from src.auth.auth import (
    authenticate_user,
    authenticate_user_by_username,
    create_access_token,
    get_password_hash,
)
from src.auth.dependencies import get_current_admin_user, get_current_user
from src.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email_or_username, password = form["username"], form["password"]

        if "@" in email_or_username:
            user = await authenticate_user(email_or_username, password)
        else:
            user = await authenticate_user_by_username(email_or_username, password)
        if not user:
            return False
        if user:
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        user = await get_current_admin_user(await get_current_user(token))
        if not user:
            return False
        return True


authentication_backend = AdminAuth(secret_key=settings.secret_key)
