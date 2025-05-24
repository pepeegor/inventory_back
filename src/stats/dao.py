from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import (
    select,
    func,
    case,
    and_,
    extract,
    text,
    cast,
    Date,
    Integer,
    Interval,
    DateTime,
    Float,
)
from sqlalchemy.sql import expression
from sqlalchemy.orm import joinedload

from src.database import async_session_maker
from src.devices.models import Device
from src.device_types.models import DeviceType
from src.maintenance_tasks.models import MaintenanceTask
from src.failure_records.models import FailureRecord
from src.replacement_suggestions.models import ReplacementSuggestion
from src.write_off_reports.models import WriteOffReport
from src.part_types.models import PartType
from src.devices.dao import DeviceDAO
from src.maintenance_tasks.dao import MaintenanceTaskDAO
from src.failure_records.dao import FailureRecordDAO
from src.replacement_suggestions.dao import ReplacementSuggestionDAO
from src.write_off_reports.dao import WriteOffReportDAO


class StatsDAO:
    @classmethod
    async def get_device_lifecycle(
        cls,
        months: int = 12,
    ) -> List[Dict[str, Any]]:
        """
        Получает данные для диаграммы жизненного цикла устройств:
        - Количество устройств в разных состояниях по типам
        - Динамика изменения состояний во времени
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        async with async_session_maker() as session:
            # Получаем все устройства с их типами и статусами
            query = (
                select(
                    DeviceType.manufacturer,
                    DeviceType.model,
                    Device.status,
                    func.date_part("year", Device.purchase_date).label("year"),
                    func.date_part("month", Device.purchase_date).label("month"),
                    func.count(Device.id).label("count"),
                    func.count(MaintenanceTask.id).label("in_maintenance"),
                    func.count(FailureRecord.id).label("has_failures"),
                )
                .select_from(Device)
                .join(DeviceType)
                .outerjoin(
                    MaintenanceTask,
                    and_(
                        MaintenanceTask.device_id == Device.id,
                        MaintenanceTask.status == "in_progress",
                    ),
                )
                .outerjoin(
                    FailureRecord,
                    and_(
                        FailureRecord.device_id == Device.id,
                        FailureRecord.resolved_date.is_(None),
                    ),
                )
                .where(Device.purchase_date.between(start_date, end_date))
                .group_by(
                    DeviceType.manufacturer,
                    DeviceType.model,
                    Device.status,
                    "year",
                    "month",
                )
            )

            result = await session.execute(query)
            data = result.fetchall()

            return [
                {
                    "device_type": f"{row.manufacturer} {row.model}",
                    "status": row.status,
                    "date": f"{int(row.year)}-{int(row.month):02d}",
                    "total": row.count,
                    "states": {
                        "working": row.count - row.in_maintenance - row.has_failures,
                        "maintenance": row.in_maintenance,
                        "failed": row.has_failures,
                    },
                }
                for row in data
            ]

    @classmethod
    async def get_reliability_map(cls) -> List[Dict[str, Any]]:
        """
        Получает данные для тепловой карты надежности оборудования:
        - Показатели надежности по производителям и моделям
        - Статистика отказов
        """
        async with async_session_maker() as session:
            # Подзапрос для подсчета всех устройств
            devices_count = (
                select(Device.type_id, func.count(Device.id).label("total_devices"))
                .group_by(Device.type_id)
                .subquery()
            )

            # Подзапрос для подсчета отказов
            failures = (
                select(
                    Device.type_id,
                    func.count(FailureRecord.id).label("failures_count"),
                    func.coalesce(
                        func.avg(
                            func.extract(
                                "epoch",
                                cast(FailureRecord.resolved_date, DateTime)
                                - cast(FailureRecord.failure_date, DateTime),
                            )
                            / 86400.0  # в днях
                        ),
                        0.0,
                    ).label("avg_repair_time"),
                )
                .join(FailureRecord, FailureRecord.device_id == Device.id)
                .group_by(Device.type_id)
                .subquery()
            )

            query = (
                select(
                    DeviceType.manufacturer,
                    DeviceType.model,
                    devices_count.c.total_devices,
                    func.coalesce(failures.c.failures_count, 0).label("failures"),
                    func.coalesce(failures.c.avg_repair_time, 0.0).label("repair_time"),
                )
                .select_from(DeviceType)
                .join(devices_count, devices_count.c.type_id == DeviceType.id)
                .outerjoin(failures, failures.c.type_id == DeviceType.id)
            )

            result = await session.execute(query)
            data = result.fetchall()

            return [
                {
                    "manufacturer": row.manufacturer,
                    "model": row.model,
                    "total_devices": row.total_devices,
                    "reliability_score": round(
                        (
                            (1 - (row.failures / row.total_devices)) * 100
                            if row.total_devices > 0
                            else 100
                        ),
                        2,
                    ),
                    "failures": row.failures,
                    "avg_repair_days": round(float(row.repair_time), 1),
                }
                for row in data
            ]

    @classmethod
    async def get_maintenance_efficiency(cls, months: int = 12) -> List[Dict[str, Any]]:
        """
        Получает данные для диаграммы эффективности обслуживания:
        - Плановые и внеплановые обслуживания
        - Время простоя
        - Своевременность выполнения
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        async with async_session_maker() as session:
            query = (
                select(
                    func.date_part("year", MaintenanceTask.scheduled_date).label(
                        "year"
                    ),
                    func.date_part("month", MaintenanceTask.scheduled_date).label(
                        "month"
                    ),
                    MaintenanceTask.task_type,
                    func.count(MaintenanceTask.id).label("tasks_count"),
                    func.coalesce(
                        func.avg(
                            func.extract(
                                "epoch",
                                cast(MaintenanceTask.completed_date, DateTime)
                                - cast(MaintenanceTask.scheduled_date, DateTime),
                            )
                            / 86400.0  # в днях
                        ),
                        0.0,
                    ).label("avg_completion_time"),
                    func.coalesce(
                        func.sum(
                            case(
                                (
                                    MaintenanceTask.completed_date
                                    <= MaintenanceTask.scheduled_date,
                                    1,
                                ),
                                else_=0,
                            )
                        ),
                        0,
                    ).label("on_time_count"),
                )
                .where(MaintenanceTask.scheduled_date.between(start_date, end_date))
                .group_by("year", "month", MaintenanceTask.task_type)
                .order_by("year", "month")
            )

            result = await session.execute(query)
            data = result.fetchall()

            return [
                {
                    "date": f"{int(row.year)}-{int(row.month):02d}",
                    "task_type": row.task_type,
                    "total_tasks": row.tasks_count,
                    "avg_completion_days": round(float(row.avg_completion_time), 1),
                    "on_time_percentage": round(
                        (
                            (row.on_time_count / row.tasks_count) * 100
                            if row.tasks_count > 0
                            else 0
                        ),
                        1,
                    ),
                }
                for row in data
            ]

    @classmethod
    async def get_failure_analysis(cls) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получает данные для диаграммы анализа отказов:
        - Иерархия: тип устройства -> тип компонента -> причина отказа
        - Статистика по времени устранения
        """
        async with async_session_maker() as session:
            query = (
                select(
                    DeviceType.manufacturer,
                    DeviceType.model,
                    PartType.name.label("part_type"),
                    FailureRecord.description,
                    func.count(FailureRecord.id).label("failures_count"),
                    func.coalesce(
                        func.avg(
                            func.extract(
                                "epoch",
                                cast(FailureRecord.resolved_date, DateTime)
                                - cast(FailureRecord.failure_date, DateTime),
                            )
                            / 86400.0  # в днях
                        ),
                        0.0,
                    ).label("avg_resolution_time"),
                )
                .select_from(FailureRecord)
                .join(Device, Device.id == FailureRecord.device_id)
                .join(DeviceType, DeviceType.id == Device.type_id)
                .join(PartType, PartType.id == FailureRecord.part_type_id)
                .group_by(
                    DeviceType.manufacturer,
                    DeviceType.model,
                    PartType.name,
                    FailureRecord.description,
                )
            )

            result = await session.execute(query)
            data = result.fetchall()

            # Преобразуем в список для Sunburst диаграммы
            failure_data = []

            # Добавляем корневой элемент
            failure_data.append(
                {
                    "id": "root",
                    "name": "All Failures",
                    "parent": "",
                }
            )

            # Обрабатываем данные и создаем плоский список с parent-child отношениями
            for row in data:
                device_type = f"{row.manufacturer} {row.model}"
                device_id = f"device_{device_type.replace(' ', '_')}"
                part_id = f"part_{device_id}_{row.part_type.replace(' ', '_')}"
                failure_id = f"failure_{part_id}_{row.description.replace(' ', '_')}"

                # Добавляем уровень устройства если его еще нет
                if not any(item["id"] == device_id for item in failure_data):
                    failure_data.append(
                        {
                            "id": device_id,
                            "name": device_type,
                            "parent": "root",
                        }
                    )

                # Добавляем уровень компонента
                if not any(item["id"] == part_id for item in failure_data):
                    failure_data.append(
                        {
                            "id": part_id,
                            "name": row.part_type,
                            "parent": device_id,
                        }
                    )

                # Добавляем конкретный отказ
                failure_data.append(
                    {
                        "id": failure_id,
                        "name": row.description,
                        "parent": part_id,
                        "value": row.failures_count,
                        "resolution_time": round(float(row.avg_resolution_time), 1),
                    }
                )

            # Возвращаем словарь с узлами для Sunburst диаграммы
            return {"nodes": failure_data}
