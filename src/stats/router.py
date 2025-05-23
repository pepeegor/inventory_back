from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
import random
from typing import Dict, List, Any

router = APIRouter(prefix="/stats", tags=["statistics"])


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
