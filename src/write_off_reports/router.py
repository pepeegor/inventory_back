# src/write_off_reports/router.py

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.auth.dependencies import get_current_admin_user, get_current_user
from src.write_off_reports.dao import WriteOffReportDAO
from src.write_off_reports.schemas import (
    SWriteOffReportRead,
    SWriteOffReportCreate,
    SWriteOffReportUpdate,
)
from src.devices.dao import DeviceDAO
from src.users.dao import UserDAO

router = APIRouter(
    prefix="/write-off-reports",
    tags=["Отчеты по списанию"],
)


@router.get(
    "/",
    response_model=List[SWriteOffReportRead],
    summary="Список всех отчётов (фильтр по дате/пользователю)",
    dependencies=[Depends(get_current_user)],
)
async def list_reports(
    date_from: Optional[date] = Query(None, description="Дата от"),
    date_to: Optional[date] = Query(None, description="Дата до"),
    disposed_by: Optional[int] = Query(None, description="ID списавшего"),
    approved_by: Optional[int] = Query(None, description="ID утвердившего"),
    current_user=Depends(get_current_user),
) -> List[SWriteOffReportRead]:
    # If the user is not an admin, they can only see their own reports
    if current_user.role != "admin" and disposed_by is None:
        disposed_by = current_user.id

    items = await WriteOffReportDAO.find_all(
        date_from=date_from,
        date_to=date_to,
        disposed_by=disposed_by,
        approved_by=approved_by,
    )
    return [SWriteOffReportRead.model_validate(i) for i in items]


@router.get(
    "/{report_id}",
    response_model=SWriteOffReportRead,
    summary="Детали отчёта",
    dependencies=[Depends(get_current_user)],
)
async def get_report(report_id: int) -> SWriteOffReportRead:
    report = await WriteOffReportDAO.find_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return SWriteOffReportRead.model_validate(report)


@router.post(
    "/",
    response_model=SWriteOffReportRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отчёт",
)
async def create_report(
    data: SWriteOffReportCreate, current_user=Depends(get_current_user)
) -> SWriteOffReportRead:
    if not await DeviceDAO.find_by_id(data.device_id):
        raise HTTPException(status_code=404, detail="Device not found")

    payload = data.model_dump(exclude={"disposed_by", "approved_by"})
    payload["disposed_by"] = current_user.id
    payload["approved_by"] = None

    try:
        created = await WriteOffReportDAO.create(**payload)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid report data")
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while creating report"
        )

    report = await WriteOffReportDAO.find_by_id(created.id)
    return SWriteOffReportRead.model_validate(report)


@router.put(
    "/{report_id}",
    response_model=SWriteOffReportRead,
    summary="Изменить причину или исполнителей",
    dependencies=[Depends(get_current_user)],
)
async def update_report(
    report_id: int, data: SWriteOffReportUpdate
) -> SWriteOffReportRead:
    payload = data.model_dump(exclude_none=True)
    if payload.get("disposed_by") is not None:
        if not await UserDAO.find_by_id(payload["disposed_by"]):
            raise HTTPException(status_code=404, detail="Disposed_by user not found")
    if payload.get("approved_by") is not None:
        if not await UserDAO.find_by_id(payload["approved_by"]):
            raise HTTPException(status_code=404, detail="Approved_by user not found")

    updated = await WriteOffReportDAO.update(report_id, **payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")

    report = await WriteOffReportDAO.find_by_id(report_id)
    return SWriteOffReportRead.model_validate(report)


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить отчёт",
    dependencies=[Depends(get_current_user)],
)
async def delete_report(report_id: int) -> Response:
    success = await WriteOffReportDAO.delete(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{report_id}/approve",
    response_model=SWriteOffReportRead,
    summary="Утвердить отчёт (только для админов)",
)
async def approve_report(
    report_id: int, current_user=Depends(get_current_admin_user)
) -> SWriteOffReportRead:

    report = await WriteOffReportDAO.find_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    updated = await WriteOffReportDAO.update(report_id, approved_by=current_user.id)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to approve report")

    report = await WriteOffReportDAO.find_by_id(report_id)
    return SWriteOffReportRead.model_validate(report)
