from fastapi import Depends
from app.exceptions import ForbiddenException
from app.auth.dependencies import get_current_user
