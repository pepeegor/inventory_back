# src/analytics/router.py

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query


from src.analytics.schemas import FailureStats, ForecastResponse
from src.auth.dependencies import get_current_admin_user, get_current_user
from src.part_types.dao import PartTypeDAO
from src.failure_records.dao import FailureRecordDAO

router = APIRouter(
    prefix="/analytics/part-types/{part_type_id}",
    tags=["Аналитика"],
    dependencies=[Depends(get_current_admin_user)],
)


@router.get(
    "/failure-stats",
    response_model=FailureStats,
    summary="Статистика отказов по типу детали",
)
async def failure_stats(
    part_type_id: int,
    date_from: Optional[date] = Query(
        None, alias="from", description="Дата начала периода"
    ),
    date_to: Optional[date] = Query(None, alias="to", description="Дата конца периода"),
    current_user=Depends(get_current_user),
):
    part_type = await PartTypeDAO.find_by_id(part_type_id)
    if not part_type:
        raise HTTPException(status_code=404, detail="PartType not found")

    records = await FailureRecordDAO.find_by_part_type_id(part_type_id, creator_id=current_user.id)
    if date_from:
        records = [r for r in records if r.failure_date >= date_from]
    if date_to:
        records = [r for r in records if r.failure_date <= date_to]

    total = len(records)
    deltas = []
    for r in records:
        if r.device.purchase_date:
            delta = (r.failure_date - r.device.purchase_date).days
            deltas.append(delta)
    avg = sum(deltas) / len(deltas) if deltas else None

    return FailureStats(total_failures=total, avg_time_to_failure_days=avg)


@router.get(
    "/forecast-replacement",
    response_model=ForecastResponse,
    summary="Прогноз даты следующей замены",
)
async def forecast_replacement(part_type_id: int):
    part_type = await PartTypeDAO.find_by_id(part_type_id)
    if not part_type:
        raise HTTPException(status_code=404, detail="PartType not found")

    interval = part_type.expected_failure_interval_days
    if interval is None:
        raise HTTPException(
            status_code=400,
            detail="expected_failure_interval_days not set for this PartType",
        )

    records = await FailureRecordDAO.find_by_part_type_id(part_type_id)
    if records:
        last_date = max(r.failure_date for r in records)
    else:
        last_date = date.today()

    forecast = last_date + timedelta(days=interval)
    return ForecastResponse(forecast_replacement_date=forecast)
