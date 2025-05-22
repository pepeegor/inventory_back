from jose import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from pydantic import EmailStr, SecretStr
import logging

from src.users.dao import UserDAO
from src.config import settings

# Настройка логирования
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "sub": str(data.get("sub"))})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), settings.algorithm
    )
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: SecretStr):
    try:
        logger.info(f"Authenticating user with email: {email}")
        user = await UserDAO.find_one_or_none(email=email)
        if not user:
            logger.info(f"User with email {email} not found")
            return None

        logger.info(f"Verifying password for user {email}")
        if not verify_password(password.get_secret_value(), user.password_hash):
            logger.info(f"Invalid password for user {email}")
            return None

        logger.info(f"Authentication successful for user {email}")
        return user
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}", exc_info=True)
        raise
