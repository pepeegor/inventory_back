from sqladmin import ModelView

from src.users.models import User
from src.devices.models import Device
from src.device_types.models import DeviceType
from src.locations.models import Location
from src.part_types.models import PartType
from src.failure_records.models import FailureRecord
from src.maintenance_tasks.models import MaintenanceTask
from src.inventory_items.models import InventoryItem
from src.inventory_events.models import InventoryEvent
from src.movements.models import Movement
from src.write_off_reports.models import WriteOffReport
from src.replacement_suggestions.models import ReplacementSuggestion


def fmt_list(obj, attr_name):
    items = getattr(obj, attr_name) or []
    return ", ".join(str(item) for item in items)


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = [c.name for c in User.__table__.c] + [
        User.movements,
        User.inventory_events,
        User.maintenance_tasks,
        User.write_offs_disposed,
        User.write_offs_approved,
        User.created_device_types,
        User.locations_created,
        User.created_part_types,
        User.created_devices,
    ]


class DeviceAdmin(ModelView, model=Device):
    name = "Устройство"
    name_plural = "Устройства"
    column_list = [c.name for c in Device.__table__.c] + [
        Device.type,
        Device.current_location,
        Device.movements,
        Device.inventory_items,
        Device.maintenance_tasks,
        Device.write_off_reports,
        Device.failure_records,
        Device.creator,
    ]


class DeviceTypeAdmin(ModelView, model=DeviceType):
    name = "Тип устройства"
    name_plural = "Типы устройств"
    column_list = [c.name for c in DeviceType.__table__.c] + [
        DeviceType.devices,
        DeviceType.part_types,
        DeviceType.creator,
    ]


class LocationAdmin(ModelView, model=Location):
    name = "Локация"
    name_plural = "Локации"
    column_list = [c.name for c in Location.__table__.c] + [
        Location.parent,
        Location.children,
        Location.devices,
        Location.movements_from,
        Location.movements_to,
        Location.inventory_events,
        Location.creator,
    ]


class PartTypeAdmin(ModelView, model=PartType):
    name = "Тип комплектующей"
    name_plural = "Типы комплектующих"
    column_list = [c.name for c in PartType.__table__.c] + [
        PartType.failure_records,
        PartType.replacement_suggestions,
        PartType.device_types,
        PartType.creator,
    ]


class FailureRecordAdmin(ModelView, model=FailureRecord):
    name = "Неполадка"
    name_plural = "Неполадки"
    column_list = [c.name for c in FailureRecord.__table__.c] + [
        FailureRecord.device,
        FailureRecord.part_type,
    ]


class MaintenanceTaskAdmin(ModelView, model=MaintenanceTask):
    name = "Задача обслуживания"
    name_plural = "Задачи обслуживания"
    column_list = [c.name for c in MaintenanceTask.__table__.c] + [
        MaintenanceTask.device,
        MaintenanceTask.assigned_user,
    ]


class InventoryItemAdmin(ModelView, model=InventoryItem):
    name = "Инвентарная позиция"
    name_plural = "Инвентарные позиции"
    column_list = [c.name for c in InventoryItem.__table__.c] + [
        InventoryItem.event,
        InventoryItem.device,
    ]


class InventoryEventAdmin(ModelView, model=InventoryEvent):
    name = "Инвентаризация"
    name_plural = "Инвентаризации"
    column_list = [c.name for c in InventoryEvent.__table__.c] + [
        InventoryEvent.location,
        InventoryEvent.performed_by_user,
        InventoryEvent.items,
    ]


class MovementAdmin(ModelView, model=Movement):
    name = "Перемещение"
    name_plural = "Перемещения"
    column_list = [c.name for c in Movement.__table__.c] + [
        Movement.device,
        Movement.from_location,
        Movement.to_location,
        Movement.performed_by_user,
    ]


class WriteOffReportAdmin(ModelView, model=WriteOffReport):
    name = "Списание"
    name_plural = "Списания"
    column_list = [c.name for c in WriteOffReport.__table__.c] + [
        WriteOffReport.device,
        WriteOffReport.disposed_by_user,
        WriteOffReport.approved_by_user,
    ]


class ReplacementSuggestionAdmin(ModelView, model=ReplacementSuggestion):
    name = "Рекомендация по замене"
    name_plural = "Рекомендации по замене"
    column_list = [c.name for c in ReplacementSuggestion.__table__.c] + [
        ReplacementSuggestion.part_type,
    ]
