from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
import random
from typing import Dict, List, Any, Optional
from sqlalchemy import func, select, and_, extract, case, text
from sqlalchemy.orm import joinedload

from src.auth.dependencies import get_current_user
from src.database import async_session_maker
from src.devices.models import Device
from src.device_types.models import DeviceType
from src.maintenance_tasks.models import MaintenanceTask
from src.failure_records.models import FailureRecord
from src.replacement_suggestions.models import ReplacementSuggestion
from src.write_off_reports.models import WriteOffReport
from src.stats.dao import StatsDAO

router = APIRouter(
    prefix="/stats",
    tags=["Статистика"],
)


@router.get("/datacenter-activity", response_model=Dict[str, List[Any]])
async def get_datacenter_activity():
    """
    Возвращает метрики активности дата-центра за последние 24 часа.

    Returns:
        Dict с ключами:
        - timestamps: список временных меток (ISO-формат)
        - values: список значений загрузки (0-100%)
    """
    # Генерируем данные за последние 24 часа с часовым интервалом
    now = datetime.now()
    timestamps = [(now - timedelta(hours=24 - i)).isoformat() for i in range(25)]

    # Имитируем нагрузку сервера с некоторыми колебаниями
    base_load = 40  # Базовая загрузка
    values = []

    for i in range(25):
        # Утром и в рабочие часы загрузка выше
        hour = (now - timedelta(hours=24 - i)).hour
        time_factor = 1.0

        if 9 <= hour <= 18:  # Рабочие часы
            time_factor = 1.5
        elif 19 <= hour <= 22:  # Вечерние часы
            time_factor = 1.3
        elif 0 <= hour <= 5:  # Ночные часы
            time_factor = 0.6

        # Добавляем случайные колебания
        fluctuation = random.uniform(-10, 10)
        load = min(95, max(10, base_load * time_factor + fluctuation))
        values.append(round(load, 1))

    return {"timestamps": timestamps, "values": values}


@router.get(
    "/device-lifecycle",
    response_model=List[Dict[str, Any]],
    summary="Жизненный цикл устройств по типам",
)
async def get_device_lifecycle(
    months: int = Query(12, description="Количество месяцев для анализа"),
    current_user=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Возвращает данные для диаграммы жизненного цикла устройств:
    - Количество устройств в разных состояниях по типам
    - Динамика изменения состояний во времени
    """
    return await StatsDAO.get_device_lifecycle(months=months)


@router.get(
    "/reliability-map",
    response_model=List[Dict[str, Any]],
    summary="Карта надежности оборудования",
)
async def get_reliability_map(
    current_user=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Возвращает данные для тепловой карты надежности оборудования:
    - Показатели надежности по производителям и моделям
    - Статистика отказов
    """
    return await StatsDAO.get_reliability_map()


@router.get(
    "/maintenance-efficiency",
    response_model=List[Dict[str, Any]],
    summary="Эффективность обслуживания",
)
async def get_maintenance_efficiency(
    months: int = Query(12, description="Количество месяцев для анализа"),
    current_user=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Возвращает данные для диаграммы эффективности обслуживания:
    - Плановые и внеплановые обслуживания
    - Время простоя
    - Своевременность выполнения
    """
    return await StatsDAO.get_maintenance_efficiency(months=months)


@router.get(
    "/failure-analysis",
    response_model=Dict[str, List[Dict[str, Any]]],
    summary="Анализ отказов компонентов",
)
async def get_failure_analysis(
    current_user=Depends(get_current_user),
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Возвращает данные для диаграммы анализа отказов:
    - Иерархия: тип устройства -> тип компонента -> причина отказа
    - Статистика по времени устранения
    """
    return await StatsDAO.get_failure_analysis()
