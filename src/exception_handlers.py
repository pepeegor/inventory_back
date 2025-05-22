from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    error_msg = str(exc)
    status_code = 400
    detail = "Ошибка базы данных"

    if isinstance(exc, IntegrityError):
        if "unique constraint" in error_msg.lower():
            if "email" in error_msg.lower():
                detail = "Пользователь с таким e-mail уже существует"
            elif "username" in error_msg.lower():
                detail = "Пользователь с таким username уже существует"
            elif "serial_number" in error_msg.lower():
                detail = "Устройство с таким серийным номером уже существует"
            else:
                detail = "Ошибка уникальности данных"
        elif "foreign key constraint" in error_msg.lower():
            detail = "Ошибка связи с другими данными"
        else:
            detail = "Ошибка целостности данных"

    return JSONResponse(status_code=status_code, content={"detail": detail})


async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = exc.errors()
    error_details = []

    for error in errors:
        error_details.append(
            {
                "loc": error.get("loc", []),
                "msg": error.get("msg", "Ошибка валидации"),
                "type": error.get("type", ""),
            }
        )

    return JSONResponse(
        status_code=422,
        content={"detail": "Ошибка валидации данных", "errors": error_details},
    )


def add_exception_handlers(app):
    """Register all exception handlers to the app."""
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
